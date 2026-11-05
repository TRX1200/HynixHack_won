from __future__ import annotations
import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from workbench.contracts import convert_temperature, load_json, validate_result
ROOT = Path(__file__).resolve().parents[1]

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.p = {'schema_version':'1.0','unit':'K','items':[{'id':'0001','value':300.},{'id':'0002','value':None},{'id':'0003','value':302.}]}
    def test_normal_preserves_id_and_missing(self):
        r=convert_temperature(self.p)
        self.assertAlmostEqual(r['mean'],27.85)
        self.assertEqual((r['count_used'],r['count_total']),(2,3))
        self.assertEqual(r['items'][0]['id'],'0001')
        self.assertIsNone(r['items'][1]['value'])
    def test_all_missing_has_no_mean(self):
        for x in self.p['items']:x['value']=None
        self.assertIsNone(convert_temperature(self.p)['mean'])
    def test_zero_is_measurement(self):
        self.p['items']=[{'id':'a','value':0}];self.p['unit']='degC'
        self.assertEqual(convert_temperature(self.p)['mean'],0)
    def test_unit_error(self):
        self.p['unit']='C'
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_version_error(self):
        self.p['schema_version']='2.0'
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_bool_not_number(self):
        self.p['items'][0]['value']=True
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_nonfinite_and_strings(self):
        for bad in [float('inf'),float('nan'),'300',10**1000]:
            with self.subTest(bad=type(bad)):
                p=copy.deepcopy(self.p);p['items'][0]['value']=bad
                with self.assertRaises(ValueError):convert_temperature(p)
    def test_impossible_temperature(self):
        self.p['items'][0]['value']=-1
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_duplicate_id(self):
        self.p['items'][1]['id']='0001'
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_extra_field(self):
        self.p['assume']=True
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_empty_input(self):
        self.p['items']=[]
        with self.assertRaises(ValueError):convert_temperature(self.p)
    def test_json_duplicate_and_nan(self):
        for s in ['{"a":1,"a":2}','{"x":NaN}','{"x":Infinity}','{"x":1e309}','{"x":1e-999}']:
            with self.assertRaises(ValueError):load_json(s)
    def test_false_mean_and_count_rejected(self):
        for key,val in [('mean',999),('count_used',3),('unit','K')]:
            r=convert_temperature(self.p);r[key]=val
            with self.assertRaises(ValueError):validate_result(r)
    def test_json_schema_when_available(self):
        try:import jsonschema
        except ImportError:self.skipTest('jsonschema unavailable')
        schema=json.loads((ROOT/'examples/bridge/result.schema.json').read_text())
        jsonschema.validate(convert_temperature(self.p),schema)
    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out.json'
            cmd=[sys.executable,str(ROOT/'examples/bridge/produce.py'),str(ROOT/'examples/bridge/input.json'),'--output',str(out)]
            a=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(a.returncode,0,a.stderr)
            original=out.read_bytes()
            b=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertNotEqual(b.returncode,0)
            self.assertEqual(out.read_bytes(),original)
    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_python_to_node_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out.json'
            p=subprocess.run([sys.executable,str(ROOT/'examples/bridge/produce.py'),str(ROOT/'examples/bridge/input.json'),'--output',str(out)],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,0,p.stderr)
            n=subprocess.run(['node',str(ROOT/'examples/bridge/consume.mjs'),str(out)],capture_output=True,text=True,timeout=10)
            self.assertEqual(n.returncode,0,n.stderr)
            self.assertEqual(json.loads(n.stdout)['ids'],['0001','0002','0003'])
    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_node_rejects_forged_mean(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out.json';r=convert_temperature(self.p);r['mean']=999
            out.write_text(json.dumps(r))
            n=subprocess.run(['node',str(ROOT/'examples/bridge/consume.mjs'),str(out)],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(n.returncode,0)
    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_node_missing_and_bad_payloads(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out.json'
            for bad in [True,'300',1e308]:
                r=convert_temperature(self.p);r['items'][0]['value']=bad;out.write_text(json.dumps(r))
                n=subprocess.run(['node',str(ROOT/'examples/bridge/consume.mjs'),str(out)],capture_output=True,text=True,timeout=10)
                self.assertNotEqual(n.returncode,0)

if __name__=='__main__':unittest.main()
