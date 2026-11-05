import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
server_mod=module('evidence_server',ROOT/'mcp/local_evidence_server.py')
install_mod=module('installer',ROOT/'tools/install_skills.py')

class ProtocolInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.index=self.root/'index.jsonl';self.index.write_text(json.dumps({'id':'a','text':'Synthetic','source_file':'s','source_sha256':'0'*64,'locator':'text'})+'\n')
        self.s=server_mod.Server(self.index)
    def tearDown(self):self.temp.cleanup()
    def init(self):
        self.s.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2099-01-01','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
        self.s.handle({'jsonrpc':'2.0','method':'notifications/initialized'})
    def test_init_negotiation(self):
        r=self.s.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2099-01-01','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
        self.assertEqual(r['result']['protocolVersion'],'2025-06-18')
    def test_init_requires_client_identity(self):
        r=self.s.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{}}})
        self.assertEqual(r['error']['code'],-32602)
    def test_requires_initialization(self):
        r=self.s.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'});self.assertIn('error',r)
    def test_unknown_method(self):
        self.init();r=self.s.handle({'jsonrpc':'2.0','id':2,'method':'shell/execute'});self.assertEqual(r['error']['code'],-32601)
    def test_unknown_argument(self):
        self.init();r=self.s.handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'evidence_stats','arguments':{'path':'/etc/passwd'}}});self.assertEqual(r['error']['code'],-32602)
    def test_invalid_query_type(self):
        self.init();r=self.s.handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_evidence','arguments':{'query':123}}});self.assertEqual(r['error']['code'],-32602)
    def test_declared_argument_schema_is_enforced(self):
        self.init()
        for arguments in [{'query':'Synthetic','source':None},{'query':'Synthetic','limit':True},{'query':'Synthetic','limit':0}]:
            with self.subTest(arguments=arguments):
                r=self.s.handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_evidence','arguments':arguments}})
                self.assertEqual(r['error']['code'],-32602)
    def test_request_ids_are_strings_or_integers(self):
        for ident in [1.25,True,None,[],{}]:
            with self.subTest(ident=ident):
                r=self.s.handle({'jsonrpc':'2.0','id':ident,'method':'ping'})
                self.assertEqual(r['error']['code'],-32600)
        self.assertEqual(self.s.handle({'jsonrpc':'2.0','id':'request-1','method':'ping'})['id'],'request-1')
    def test_stdio_utf8_under_non_utf8_locale(self):
        text='한글 근거 🔬'
        row={'id':'a','text':text,'source_file':'근거.txt','source_sha256':'0'*64,'locator':'text'}
        self.index.write_text(json.dumps(row,ensure_ascii=False)+'\n',encoding='utf-8')
        requests=[
            {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}}},
            {'jsonrpc':'2.0','method':'notifications/initialized'},
            {'jsonrpc':'2.0','id':'읽기','method':'tools/call','params':{'name':'read_evidence','arguments':{'chunk_id':'a'}}},
        ]
        p=subprocess.run([sys.executable,str(ROOT/'mcp/local_evidence_server.py'),'--index',str(self.index)],
                         input=('\n'.join(json.dumps(r,ensure_ascii=False) for r in requests)+'\n').encode('utf-8'),
                         capture_output=True,env={**os.environ,'PYTHONIOENCODING':'ascii'},timeout=15)
        self.assertEqual(p.returncode,0,p.stderr.decode('utf-8','replace'))
        replies=[json.loads(line) for line in p.stdout.decode('utf-8').splitlines()]
        self.assertEqual(len(replies),2);self.assertEqual(replies[1]['id'],'읽기')
        self.assertEqual(json.loads(replies[1]['result']['content'][0]['text'])['text'],text)
    def test_stdio_rejects_ambiguous_json_and_recovers(self):
        lines=[b'{"jsonrpc":"2.0","id":1,"id":2,"method":"ping"}',
               b'{"jsonrpc":"2.0","id":NaN,"method":"ping"}',b'\xff',
               b'{"jsonrpc":"2.0","id":3,"method":"ping"}']
        p=subprocess.run([sys.executable,str(ROOT/'mcp/local_evidence_server.py'),'--index',str(self.index)],
                         input=b'\n'.join(lines)+b'\n',capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr.decode('utf-8','replace'))
        replies=[json.loads(line) for line in p.stdout.decode('utf-8').splitlines()]
        self.assertEqual([r['error']['code'] for r in replies[:3]],[-32700]*3)
        self.assertEqual(replies[3],{'jsonrpc':'2.0','id':3,'result':{}})
    def test_no_notification_response(self):
        self.assertIsNone(self.s.handle({'jsonrpc':'2.0','method':'notifications/initialized'}))
    def test_selected_skills_only(self):
        install_mod.install(self.root,['wb-start'])
        p=self.root/'.agents/skills/wb-start/SKILL.md'
        self.assertTrue(p.exists());self.assertNotIn('__KIT_ROOT__',p.read_text(encoding='utf-8'));self.assertFalse((self.root/'AGENTS.md').exists())
    def test_installer_refuses_existing(self):
        install_mod.install(self.root,['wb-start'])
        with self.assertRaises(ValueError):install_mod.install(self.root,['wb-start'])
    def test_inventory_skill_resolves_source_and_retains_license(self):
        install_mod.install(self.root,['wb-field-inventory'])
        dest=self.root/'.agents/skills/wb-field-inventory'
        text=(dest/'SKILL.md').read_text(encoding='utf-8')
        self.assertNotIn('__KIT_ROOT__',text)
        self.assertIn((ROOT/'field_inventory').as_posix(),text)
        self.assertEqual((dest/'LICENSE').read_bytes(),(ROOT/'LICENSE').read_bytes())
        self.assertFalse((self.root/'AGENTS.md').exists())
    def test_installer_refuses_traversal(self):
        with self.assertRaises(ValueError):install_mod.install(self.root,['../wb-start'])
    def test_all_skills_metadata_and_length(self):
        paths=list((ROOT/'.agents/skills').glob('*/SKILL.md'))
        expected={'wb-start','wb-intake','wb-vision','wb-docs','wb-data','wb-build','wb-debug',
                  'wb-optimize','wb-verify','wb-report','wb-explain','wb-finish',
                  'wb-graphics','wb-visualize','wb-stack','wb-pipeline','wb-physics','wb-stats','wb-field-inventory'}
        self.assertEqual({p.parent.name for p in paths},expected)
        for p in paths:
            text=p.read_text(encoding='utf-8');self.assertTrue(text.startswith('---\nname: wb-'));self.assertIn('description:',text);self.assertLess(len(text.splitlines()),100)

if __name__=='__main__':unittest.main()
