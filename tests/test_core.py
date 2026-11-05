import json
import tempfile
import unittest
from pathlib import Path
from workbench.core import *
from workbench.documents import chunk_units,extract_to_index,load_index,search_chunks,get_chunk
from workbench.optimization import solve_assignment,validate_assignment
from workbench.reporting import html_report,normalize_report

class CoreTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def file(self,name,text):
        p=self.root/name;p.write_text(text,encoding='utf-8',newline='\n');return p
    def test_profile_preserves_ids(self):
        p=self.file('a.csv','id,value\n001,1\n1,2\n001,\n')
        r=profile_csv(p,['id']);self.assertEqual(r['rows'],3);self.assertEqual(r['key_audit']['duplicate_key_rows_excess'],1)
        self.assertEqual(r['columns']['value']['missing_blank'],1)
    def test_duplicate_headers_rejected(self):
        with self.assertRaises(ValueError):read_csv(self.file('a.csv','x,x\n1,2\n'))
    def test_ragged_csv_rejected(self):
        with self.assertRaises(ValueError):read_csv(self.file('a.csv','x,y\n1\n'))
    def test_empty_csv_rejected(self):
        with self.assertRaises(ValueError):read_csv(self.file('a.csv',''))
    def test_multiline_csv(self):
        h,r=read_csv(self.file('a.csv','id,note\n1,"a\nb"\n'));self.assertEqual(len(r),1);self.assertEqual(r[0]['note'],'a\nb')
    def test_unclosed_csv_quote_rejected(self):
        with self.assertRaises(csv.Error):read_csv(self.file('a.csv','id,note\n1,"unfinished'))
    def test_cp949_explicit(self):
        p=self.root/'a.csv';p.write_bytes('이름,값\n가,2\n'.encode('cp949'))
        self.assertEqual(read_csv(p,'cp949')[1][0]['이름'],'가')
    def test_nonfinite_rejected(self):
        for value in ['NaN','Infinity','-Infinity',True]:
            with self.subTest(value=value),self.assertRaises(ValueError):finite_decimal(value)
    def test_join_multiplicity(self):
        l=self.file('l.csv','id\na\nb\nb\n');r=self.file('r.csv','id\na\nb\nb\n')
        result=join_audit(l,r,['id']);self.assertEqual(result['expected_inner_rows'],5);self.assertEqual(result['many_to_many_key_groups'],1)
    def test_join_blank_not_matching(self):
        l=self.file('l.csv','id,x\n,1\na,2\n');r=self.file('r.csv','id,y\n,2\na,3\n')
        result=join_audit(l,r,['id']);self.assertEqual(result['expected_inner_rows'],1);self.assertEqual(result['expected_left_join_rows'],2)
    def test_decimal_aggregate(self):
        result=aggregate_csv(self.file('a.csv','g,v\na,0.1\na,0.2\nb,\n'),['g'],'v')
        self.assertEqual(result['groups'][0]['sum'],'0.3');self.assertIsNone(result['groups'][1]['sum']);self.assertEqual(result['reconciled_rows'],3)
    def test_aggregate_invalid_not_dropped(self):
        with self.assertRaises(ValueError):aggregate_csv(self.file('a.csv','v\n1\noops\n'),[],'v')
    def test_large_decimal_sum_does_not_lose_units(self):
        r=aggregate_csv(self.file('a.csv','v\n10000000000000000000000000000\n1\n'),[],'v')
        self.assertEqual(r['groups'][0]['sum'],'10000000000000000000000000001')
    def test_decimal_sum_cancellation_is_exact(self):
        r=aggregate_csv(self.file('a.csv','v\n10000000000000000000000000000\n1\n-10000000000000000000000000000\n'),[],'v')
        self.assertEqual(r['groups'][0]['sum'],'1')
        self.assertEqual(r['groups'][0]['mean'],'0.3333333333333333333333333333')
    def test_decimal_alignment_limit_explicit(self):
        with self.assertRaisesRegex(ValueError,'aligned digits'):
            aggregate_csv(self.file('a.csv','v\n1E10000\n1\n'),[],'v')
    def test_decimal_underflow_does_not_become_zero_mean(self):
        with self.assertRaisesRegex(ValueError,'mean exceeds'):
            aggregate_csv(self.file('a.csv','v\n1E-10000000\n'),[],'v')
    def test_decimal_coefficient_limit_explicit(self):
        with self.assertRaisesRegex(ValueError,'coefficient'):
            exact_decimal_add(Decimal(0),Decimal('9'*10001))
    def test_aggregate_group_collision_rejected(self):
        with self.assertRaisesRegex(ValueError,'conflicts'):
            aggregate_csv(self.file('a.csv','sum,v\nteam-a,1\n'),['sum'],'v')
    def test_no_overwrite(self):
        p=self.file('a.txt','original')
        with self.assertRaises(FileExistsError):write_new(p,'new')
        self.assertEqual(p.read_text(),'original')
    def test_credential_path_rejected(self):
        with self.assertRaises(ValueError):checked_file(self.file('.env','secret'))
    def test_symlink_rejected(self):
        p=self.file('a.txt','ok');q=self.root/'alias'
        try:q.symlink_to(p)
        except OSError:self.skipTest('Symlinks not available')
        with self.assertRaises(ValueError):checked_file(q)
    def test_inventory_ignores_hidden(self):
        self.file('a.txt','ok');self.file('.env','hidden')
        self.assertEqual(inventory(self.root)['count'],1)
    def test_manifest_escape(self):
        with self.assertRaises(ValueError):check_manifest(self.root,{'files':[{'path':'../outside'}]})
    def test_manifest_missing(self):
        result=check_manifest(self.root,{'files':[{'path':'not-there'}]});self.assertFalse(result['all_passed'])
    def test_manifest_valid_json(self):
        self.file('a.json','{"x": 1}')
        self.assertTrue(check_manifest(self.root,{'files':[{'path':'a.json','format':'json'}]})['all_passed'])
    def test_ambiguous_or_nonfinite_json_rejected(self):
        for text in ['{"x":1,"x":2}','{"nested":{"x":1,"x":2}}','{"x":1e309}','{"x":1e-999}','{"x":NaN}']:
            with self.subTest(text=text),self.assertRaises(ValueError):load_json(self.file('a.json',text))
        self.assertEqual(load_json(self.file('a.json','{"x":0e-999,"id":9007199254740993}')),
                         {'x':0.0,'id':9007199254740993})
    def test_manifest_reports_malformed_csv(self):
        self.file('a.csv','id,note\n1,"unfinished')
        result=check_manifest(self.root,{'files':[{'path':'a.csv','format':'csv'}]})
        self.assertFalse(result['all_passed']);self.assertIn('error',result['checks'][0])
    def test_order_unique(self):
        r=solve_order({'nodes':['A','B','C'],'before':[['A','B'],['B','C']]});self.assertTrue(r['unique']);self.assertEqual(r['one_order'],['A','B','C'])
    def test_order_ambiguous(self):
        r=solve_order({'nodes':['A','B','C'],'before':[['A','B'],['A','C']]});self.assertFalse(r['unique']);self.assertEqual(r['status'],'FEASIBLE')
    def test_order_cycle(self):
        r=solve_order({'nodes':['A','B'],'before':[['A','B'],['B','A']]});self.assertEqual(r['status'],'INFEASIBLE_CYCLE');self.assertIsNone(r['one_order'])
    def test_order_undeclared(self):
        with self.assertRaises(ValueError):solve_order({'nodes':['A'],'before':[['A','B']]})
    def test_evidence_source_required(self):
        r=validate_evidence([{'id':'x','kind':'fact','statement':'claim'}]);self.assertFalse(r['structural_valid'])
    def test_evidence_reversed_dates(self):
        r=validate_evidence([{'id':'x','kind':'assumption','statement':'claim','valid_from':'2030-02-01','valid_to':'2030-01-01'}]);self.assertFalse(r['structural_valid'])
    def test_evidence_no_truth_claim(self):
        r=validate_evidence([{'id':'x','kind':'assumption','statement':'claim'}]);self.assertTrue(r['structural_valid']);self.assertFalse(r['semantic_truth_checked'])
    def test_evidence_unresolved_derived(self):
        r=validate_evidence([{'id':'x','kind':'derived','statement':'claim','based_on':['not-there']}]);self.assertFalse(r['structural_valid'])
    def test_extract_and_search(self):
        p=self.file('policy.md','# Rules\nTeam A needs feature X.\n');out=self.root/'index.jsonl'
        extract_to_index([str(p)],str(out),2,1);data=load_index(out)
        r=search_chunks(data,'feature X');self.assertTrue(r['hits']);self.assertIn('Team A',get_chunk(data,r['hits'][0]['id'])['text'])
    def test_index_get_rejects_path(self):
        with self.assertRaises(ValueError):get_chunk([],'../../.env')
    def test_duplicate_index_rejected(self):
        r={'id':'1','text':'x','source_file':'s','source_sha256':'a','locator':'text'}
        p=self.file('i.jsonl',json.dumps(r)+'\n'+json.dumps(r))
        with self.assertRaises(ValueError):load_index(p)
    def test_chunk_overlap(self):
        u={'text':'1\n2\n3\n4','source_file':'s','source_sha256':'a','locator':'text','warning':None}
        c=chunk_units([u],3,1);self.assertEqual(len(c),2);self.assertEqual(c[1]['line_start'],3)
    def test_empty_search_rejected(self):
        with self.assertRaises(ValueError):search_chunks([],'')
    def test_search_bound(self):
        with self.assertRaises(ValueError):search_chunks([],'query',limit=200)
    def test_search_no_hit_not_absence(self):
        r=search_chunks([],'term');self.assertEqual(r['hits'],[]);self.assertIn('not',r['method'])
    def test_report_html_escaped(self):
        out=html_report({'title':'<script>x</script>','summary':'<img src="https://example.invalid">'})
        self.assertNotIn('<script>x',out);self.assertIn('&lt;script&gt;',out)
    def test_report_pass_needs_evidence(self):
        with self.assertRaises(ValueError):normalize_report({'title':'Report','validation':[{'check':'x','expected':'1','actual':'1','status':'pass'}]})
    def test_report_not_run_valid(self):
        normalize_report({'title':'Report','validation':[{'check':'x','expected':'1','actual':'not run','status':'not_run'}]})
    def spec(self):
        return {'items':[{'id':'1','requires':['X']},{'id':'2','requires':['Y']}], 'options':[{'id':'basic','features':['X'],'unit_cost':'10','capacity':2},{'id':'plus','features':['X','Y'],'unit_cost':'25','capacity':2}]}
    def test_assignment_optimal(self):
        r=solve_assignment(self.spec());self.assertEqual(r['status'],'OPTIMAL_ENUMERATED');self.assertEqual(r['cost'],'35');self.assertTrue(r['validation']['feasible'])
    def test_assignment_feature_violation(self):
        r=validate_assignment(self.spec(),{'1':'basic','2':'basic'});self.assertFalse(r['feasible'])
    def test_assignment_capacity_violation(self):
        s=self.spec();s['options'][1]['capacity']=1
        self.assertFalse(validate_assignment(s,{'1':'plus','2':'plus'})['feasible'])
    def test_assignment_extra_item(self):
        self.assertFalse(validate_assignment(self.spec(),{'1':'basic','2':'plus','3':'basic'})['feasible'])
    def test_assignment_limit_not_optimal(self):
        r=solve_assignment(self.spec(),1);self.assertEqual(r['status'],'FEASIBLE_LIMIT');self.assertFalse(r['complete_enumeration'])
    def test_assignment_unknown_not_infeasible(self):
        s={'items':[{'id':'a'},{'id':'b'}],'options':[{'id':'x','features':[],'unit_cost':'1','capacity':1},{'id':'y','features':[],'unit_cost':'2','capacity':1}]}
        self.assertEqual(solve_assignment(s,1)['status'],'UNKNOWN_LIMIT')
    def test_assignment_infeasible(self):
        s=self.spec();s['items'][1]['requires']=['missing']
        self.assertEqual(solve_assignment(s)['status'],'INFEASIBLE')

if __name__=='__main__':unittest.main()
