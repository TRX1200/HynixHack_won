#!/usr/bin/env python3
"""Local protocol smoke test. Does NOT connect to a model or the assessment host."""
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from workbench.documents import chunk_units
from workbench.core import write_new
import tempfile

def run():
    with tempfile.TemporaryDirectory() as temp:
        index=Path(temp)/'index.jsonl'
        c=chunk_units([{'text':'Synthetic policy: team A requires feature X.','source_file':'synthetic.txt','source_sha256':'0'*64,'locator':'text','warning':None}])
        write_new(index,'\n'.join(json.dumps(r) for r in c))
        requests=[
          {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'offline-smoke','version':'1'}}},
          {'jsonrpc':'2.0','method':'notifications/initialized'},
          {'jsonrpc':'2.0','id':2,'method':'tools/list'},
          {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'search_evidence','arguments':{'query':'feature X'}}},
          {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'read_evidence','arguments':{'chunk_id':c[0]['id']}}},
          {'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'evidence_stats','arguments':{}}},
          {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'read_evidence','arguments':{'chunk_id':'../../.env'}}},
        ]
        p=subprocess.run([sys.executable,str(ROOT/'mcp/local_evidence_server.py'),'--index',str(index)],input=''.join(json.dumps(r)+'\n' for r in requests),text=True,encoding='utf-8',capture_output=True,timeout=15)
        if p.returncode:raise RuntimeError(p.stderr)
        replies=[json.loads(line) for line in p.stdout.splitlines()]
        assert len(replies)==6
        assert replies[0]['result']['protocolVersion']=='2025-06-18'
        assert len(replies[1]['result']['tools'])==3
        assert not replies[2]['result']['isError']
        assert 'feature X' in replies[3]['result']['content'][0]['text']
        assert replies[-1]['result']['isError'] is True
        print(json.dumps({'passed':True,'checks':6,'scope':'Local stdio handshake/list/search/read/stats/invalid ID. Cofa and Codex end-to-end NOT tested.'},indent=2))
if __name__=='__main__':run()
