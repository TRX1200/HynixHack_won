import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class CLITests(unittest.TestCase):
    def call(self,*args):return subprocess.run([sys.executable,str(ROOT/'tools/run.py'),*args],capture_output=True,text=True,encoding='utf-8',timeout=10)
    def test_doctor(self):
        p=self.call('doctor');self.assertEqual(p.returncode,0);self.assertTrue(json.loads(p.stdout)['python_supported'])
    def test_bad_input_error_code(self):
        p=self.call('csv-profile','missing-do-not-create.csv');self.assertEqual(p.returncode,2);self.assertIn('error',json.loads(p.stderr))
    def test_structural_failure_exit(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'e.json';p.write_text('[{"id":"x","kind":"fact","statement":"no source"}]')
            r=self.call('check-evidence',str(p));self.assertEqual(r.returncode,1)
    def test_real_example_aggregate(self):
        p=self.call('aggregate',str(ROOT/'examples/sample.csv'),'--group','team','--value','amount')
        self.assertEqual(p.returncode,0);data=json.loads(p.stdout);self.assertEqual(data['groups'][0]['sum'],'31.0')
    def test_electronics_rc_example(self):
        result=self.call('calculate',str(ROOT/'examples/electronics/rc.json'))
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data['calculator'],'rc')
        self.assertTrue(data['assumptions'])
    def test_html_output_without_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            out=str(Path(td)/'r.html')
            first=self.call('report',str(ROOT/'examples/report.json'),'--format','html','--out',out)
            second=self.call('report',str(ROOT/'examples/report.json'),'--format','html','--out',out)
            self.assertEqual(first.returncode,0);self.assertEqual(second.returncode,2)
    def test_unicode_cli_output_under_ascii_locale(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'data_\uac80\uc0ac_\U0001f642.csv'
            source.write_text('\ud56d\ubaa9,\uac12\na,1\n',encoding='utf-8')
            env=os.environ.copy();env['PYTHONIOENCODING']='ascii'
            result=subprocess.run([sys.executable,str(ROOT/'tools/run.py'),'csv-profile',str(source)],
                                  capture_output=True,env=env,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(result.stdout.decode('utf-8'))
            self.assertEqual(data['rows'],1)
            self.assertIn('\ud56d\ubaa9',data['columns'])
if __name__=='__main__':unittest.main()
