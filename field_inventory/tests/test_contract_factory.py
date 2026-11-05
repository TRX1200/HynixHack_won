"""Validation plan generation tests. A generated plan is not a completed check."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('contract_factory',ROOT/'tools/contract_factory.py')
mod=importlib.util.module_from_spec(sp)
assert sp.loader is not None
sp.loader.exec_module(mod)

class ContractTests(unittest.TestCase):
    def test_every_family_emits_negative(self):
        data={'id':'synthetic','task_types':sorted(mod.mod.VALID_TYPES)}
        c=mod.create_contract(data)
        self.assertEqual({x['family'] for x in c['checks']},mod.mod.VALID_TYPES)
        for f in data['task_types']:
            self.assertTrue(any(x['family']==f and x['polarity']=='negative' for x in c['checks']))
    def test_nothing_falsely_passes(self):
        p=json.loads((ROOT/'examples/profiles/composite_app.json').read_text(encoding='utf-8'))
        c=mod.create_contract(p)
        self.assertEqual(c['summary']['passed'],0)
        self.assertTrue(all(x['status']=='NOT_RUN' for x in c['checks']))
    def test_hard_constraints_go_to_plan(self):
        c=mod.create_contract({'task_types':['optimization'],'hard_constraints':['every ID appears exactly once']})
        self.assertIn('R001',[x['id'] for x in c['checks']])
    def test_boundary_and_family_deduplication(self):
        with self.assertRaises(ValueError):
            mod.create_contract({'task_types':['web_app','web_app']})
        c=mod.create_contract({'task_types':['web_app']})
        ids=[x['id'] for x in c['checks']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(sum(x['polarity']=='boundary' for x in c['checks']),1)
    def test_multi_type_generated(self):
        c=mod.create_contract({'task_types':['web_app','statistics_ml']})
        self.assertTrue(any(x['family']=='web_app' for x in c['checks']))
        self.assertTrue(any(x['family']=='statistics_ml' for x in c['checks']))
    def test_invalid_type_rejected(self):
        with self.assertRaises(ValueError):mod.create_contract({'task_types':['unknown_family']})
    def test_cli_json(self):
        p=ROOT/'examples/profiles/route.json'
        r=subprocess.run([sys.executable,str(ROOT/'tools/contract_factory.py'),str(p),'--format','json'],capture_output=True,text=True,encoding='utf-8',check=True)
        self.assertEqual(json.loads(r.stdout)['status'],'PLAN_ONLY_NOT_VALIDATION')
    def test_output_exists_not_overwritten(self):
        p=ROOT/'examples/profiles/route.json'
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'a.md';f.write_text('existing',encoding='utf-8')
            r=subprocess.run([sys.executable,str(ROOT/'tools/contract_factory.py'),str(p),'--out',str(f)],capture_output=True,text=True,encoding='utf-8')
            self.assertNotEqual(r.returncode,0)
            self.assertEqual(f.read_text(encoding='utf-8'),'existing')

if __name__=='__main__':unittest.main()
