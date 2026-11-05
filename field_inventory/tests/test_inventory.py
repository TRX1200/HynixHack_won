"""Executable offline tests for the advisory routing inventory."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/inventory.py'
sp=importlib.util.spec_from_file_location('field_inventory',SCRIPT)
mod=importlib.util.module_from_spec(sp)
assert sp.loader is not None
sp.loader.exec_module(mod)
CARDS=mod.load_catalog()

def profile(name):
    return json.loads((ROOT/'examples/profiles'/f'{name}.json').read_text(encoding='utf-8'))

class CatalogTests(unittest.TestCase):
    def test_card_count(self): self.assertGreaterEqual(len(CARDS),90)
    def test_unique_and_complete(self): self.assertEqual(mod.validate_catalog(CARDS),[])
    def test_family_coverage(self):
        allk={k for c in CARDS for k in c['task_types']}
        self.assertTrue(mod.VALID_TYPES.issubset(allk))
    def test_recipe_resolves(self):
        for c in CARDS:
            self.assertTrue((ROOT/'recipes'/(c['id']+'.md')).is_file())
    def test_decision_rule_references_valid(self):
        ids={c['id'] for c in CARDS}
        rules=json.loads((ROOT/'catalog/decision_rules.json').read_text(encoding='utf-8'))['rules']
        self.assertGreaterEqual(len(rules),25)
        for r in rules:
            for n in (r['recommend']+r['avoid']):self.assertIn(n,ids)
    def test_patterns_not_claimed_implemented(self):
        patterns=json.loads((ROOT/'catalog/code_patterns.json').read_text(encoding='utf-8'))['patterns']
        self.assertGreaterEqual(len(patterns),12)
        self.assertTrue(all(p['implemented'] is False for p in patterns))
    def test_profiles_all_valid(self):
        for p in (ROOT/'examples/profiles').glob('*.json'):
            spec=json.loads(p.read_text(encoding='utf-8'))
            self.assertEqual(mod.validate_profile(spec),[],p.name)
            self.assertTrue(spec['_synthetic'])
    def test_empty_search(self):
        self.assertEqual(mod.search_cards(CARDS,'nonexistingunrelatedtokenabc'),[])
    def test_retrieval_routing(self):
        ret=mod.search_cards(CARDS,'vehicle bus route capacity',limit=5)
        self.assertEqual(ret[0][1]['id'],'vehicle-routing')
    def test_retrieval_korean(self):
        r=mod.search_cards(CARDS,'버스 노선 최적화',limit=5)
        self.assertEqual('vehicle-routing',r[0][1]['id'])
    def test_all_recipe_status_honest(self):
        self.assertTrue(all(c['implementation_status']=='RECIPE_ONLY' for c in CARDS))
    def test_retrieval_vision(self):
        ret=mod.search_cards(CARDS,'image align registration',limit=6)
        self.assertIn('image-registration',[r[1]['id'] for r in ret])

class GateTests(unittest.TestCase):
    def plan(self,name):return mod.plan(profile(name),CARDS)
    def top(self,name,kind):return self.plan(name)['recommended'][kind][0]['id']
    def test_multiple_domains(self):
        p=self.plan('composite_app')
        self.assertEqual(set(p['recommended']),{'web_app','data_pipeline','optimization','quality_security'})
        self.assertIn('web_app',p['validators'])
        self.assertIn('optimization',p['validators'])
    def test_route_rule(self): self.assertEqual(self.top('route','optimization'),'vehicle-routing')
    def test_route_no_global_optimum_claim(self):
        p=self.plan('route')
        self.assertTrue(p['advisory_only'])
        self.assertTrue(p['review_required'])
    def test_image_rule(self): self.assertEqual(self.top('image_inspection','computer_vision'),'image-registration')
    def test_ode_rule(self): self.assertEqual(self.top('physics_ode','scientific_computing'),'physics-ode')
    def test_forecast_rule(self): self.assertEqual(self.top('forecast','statistics_ml'),'forecasting')
    def test_docs_rule(self): self.assertEqual(self.top('docs','documents_search'),'text-index')
    def test_schedule_rule(self): self.assertEqual(self.top('scheduling','optimization'),'resource-schedule')
    def test_security_rule(self):
        p=self.plan('security')
        self.assertEqual(p['recommended']['web_app'][0]['id'],'role-access')
    def test_graph_rule(self): self.assertEqual(self.top('graph','optimization'),'weighted-shortest')
    def test_unknown_does_not_select_solver(self):
        p=self.plan('unknown')
        self.assertEqual(p['status'],'NEEDS_CLASSIFICATION')
        self.assertEqual(p['recommended'],{})
    def test_nonoptimization_not_forced(self):
        p=self.plan('not-optimization')
        self.assertNotIn('optimization',p['recommended'])
    def test_existing_stack_preference(self):
        p=profile('composite_app');p['environment']['existing_stack']='Node/Express'
        hint=mod.plan(p,CARDS)['architecture']['first_choice']
        self.assertIn('Node/Express',hint)
    def test_optimality_warning(self):
        p=profile('route');p['environment']['optimality_required']=True
        self.assertTrue(any('Global optimality' in x for x in mod.plan(p,CARDS)['warnings']))
    def test_offline_warning(self):
        self.assertTrue(any('Network' in x for x in self.plan('route')['warnings']))
    def test_decision_rule_only_with_explicit_properties(self):
        p=profile('route');p.pop('properties')
        self.assertFalse(any(d['id']=='routing-multi' for d in mod.plan(p,CARDS)['decision_gates_applied']))
    def test_graph_unweighted(self):
        p=dict(task_types=['optimization'],properties={'problem_structure':'shortest_path','edge_weight_type':'unweighted'},summary='Find minimum hops')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['optimization'][0]['id'],'unweighted-shortest')
    def test_graph_negative(self):
        p=dict(task_types=['optimization'],properties={'problem_structure':'shortest_path','edge_weight_type':'may_be_negative'},summary='Directed graph with negative cost')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['optimization'][0]['id'],'negative-shortest')
    def test_assignment_one_to_one(self):
        p=dict(task_types=['optimization'],properties={'problem_structure':'assignment','capacity_model':'one_to_one'},summary='pair workers and tasks')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['optimization'][0]['id'],'bipartite-match')
    def test_assignment_many(self):
        p=dict(task_types=['optimization'],properties={'problem_structure':'assignment','capacity_model':'many_to_one'},summary='many workers to teams')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['optimization'][0]['id'],'min-cost-flow')
    def test_integer_decisions(self):
        p=dict(task_types=['optimization'],properties={'problem_structure':'resource_allocation','decision_variable_type':'integer'},summary='allocate integral quantities')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['optimization'][0]['id'],'mixed-integer')
    def test_continuous_decisions(self):
        p=dict(task_types=['optimization'],properties={'problem_structure':'resource_allocation','decision_variable_type':'continuous','linear_model_confirmed':True},summary='linear allocation')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['optimization'][0]['id'],'linear-programming')
    def test_vision_segment(self):
        p=dict(task_types=['computer_vision'],properties={'task_subtype':'segmentation'},summary='detect pixels in mask')
        self.assertEqual(mod.plan(p,CARDS)['recommended']['computer_vision'][0]['id'],'image-segmentation')
    def test_microservice_warning_rule(self):
        p=dict(task_types=['integration'],environment={'network_allowed':False,'docker_available':False})
        r=mod.plan(p,CARDS)
        self.assertIn('runtime-no-docker',[x['id'] for x in r['decision_gates_applied']])
    def test_hypothesis(self):
        p=dict(task_types=['statistics_ml'],properties={'task_subtype':'hypothesis_test'})
        self.assertEqual(mod.plan(p,CARDS)['recommended']['statistics_ml'][0]['id'],'hypothesis-test')
    def test_prop_unrecognized_does_not_trigger(self):
        p=dict(task_types=['optimization'],properties={'edge_weight_type':'unknown'})
        self.assertFalse(any(d['id'].startswith('graph-') for d in mod.plan(p,CARDS)['decision_gates_applied']))

class ValidationTests(unittest.TestCase):
    def test_non_object(self): self.assertTrue(mod.validate_profile([]))
    def test_bad_type(self): self.assertTrue(mod.validate_profile({'task_types':'optimization'}))
    def test_unsupported_type(self): self.assertTrue(mod.validate_profile({'task_types':['magic-ai']}))
    def test_bad_signals(self): self.assertTrue(mod.validate_profile({'task_types':['web_app'],'signals':'foo'}))
    def test_missing_type_is_not_solver(self):
        self.assertEqual(mod.plan({'summary':'make it work'},CARDS)['status'],'NEEDS_CLASSIFICATION')
    def test_null_properties(self):self.assertTrue(mod.validate_profile({'task_types':[],'properties':None}))
    def test_null_environment(self):self.assertTrue(mod.validate_profile({'task_types':[],'environment':None}))
    def test_negative_catalog_dup(self):
        bad=CARDS+[CARDS[0]]
        self.assertTrue(any('duplicate' in err for err in mod.validate_catalog(bad)))
    def test_negative_catalog_missing(self):
        bad=[dict(c) for c in CARDS]
        bad[0]['title']=''
        self.assertTrue(any('missing title' in err for err in mod.validate_catalog(bad)))
    def test_terminal_plan_json_is_valid(self):
        p=ROOT/'examples/profiles/route.json'
        r=subprocess.run([sys.executable,str(SCRIPT),'plan',str(p),'--json'],capture_output=True,text=True,check=True)
        data=json.loads(r.stdout)
        self.assertEqual(data['profile_id'],'synth-route')
    def test_terminal_catalog_valid(self):
        r=subprocess.run([sys.executable,str(SCRIPT),'verify-catalog'],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(r.stdout)['status'],'PASS')
    def test_unknown_card_fails(self):
        r=subprocess.run([sys.executable,str(SCRIPT),'show','not-a-card'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)

if __name__=='__main__':unittest.main()
