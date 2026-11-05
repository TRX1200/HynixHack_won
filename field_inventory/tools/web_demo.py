#!/usr/bin/env python3
"""Synthetic, local HTTP/UI role-boundary demo. No production login or persistence.

Run with --port 8765. The local terminal prints ephemeral reader/writer tokens.
Use --host 0.0.0.0 only when the permitted preview environment requires it.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import secrets
import threading
from urllib.parse import urlsplit

PAGE = r'''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>범용 워크벤치 · API 실습</title><style>
body{font:16px system-ui,sans-serif;background:#f4f6fa;color:#17243a;margin:0;padding:32px}
main{max-width:620px;margin:auto;background:white;border:1px solid #d9e1ed;border-radius:16px;padding:28px}
h1{font-size:25px}p{line-height:1.6;color:#4c5c73}label{display:block;margin:18px 0 6px}
input{box-sizing:border-box;width:100%;padding:12px;border:1px solid #8c9cb3;border-radius:6px;font:inherit}
button{padding:12px 18px;margin:20px 8px 0 0;border:0;border-radius:6px;background:#2458b8;color:white;font:inherit}
button:focus-visible,input:focus-visible{outline:3px solid #dc8c19;outline-offset:3px}
pre{white-space:pre-wrap;background:#edf2fa;padding:16px;min-height:55px;overflow-wrap:anywhere}
</style><main><p>LOCAL WORKBENCH / SYNTHETIC DEMO</p><h1>면적 계산과 서버 권한 확인</h1>
<p>서버 터미널의 임시 토큰을 입력하세요. writer는 계산 결과를 저장하고 reader는 조회합니다.
실습용 메모리 저장소이며 서버를 종료하면 결과가 사라집니다.</p>
<form id="calc"><label for="token">임시 접근 토큰</label><input id="token" type="password" autocomplete="off" required>
<label for="width">너비 (m)</label><input id="width" type="number" min="0" max="1000000" step="any" value="2" required>
<label for="height">높이 (m)</label><input id="height" type="number" min="0" max="1000000" step="any" value="3" required>
<button type="submit">계산하고 저장</button><button type="button" id="read">저장 결과 조회</button></form>
<pre id="result" role="status" aria-live="polite">아직 실행하지 않았습니다.</pre>
<script>
async function request(path,body){
 const out=document.getElementById('result');out.textContent='처리 중…';
 try{const r=await fetch(path,{method:body?'POST':'GET',headers:{'Authorization':'Bearer '+document.getElementById('token').value,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
 const data=await r.json();out.textContent='HTTP '+r.status+'\n'+JSON.stringify(data,null,2);
 }catch(e){out.textContent='연결 오류: 서버 실행 상태를 확인하세요.';}
}
document.getElementById('calc').addEventListener('submit',e=>{e.preventDefault();request('/api/calculate',{width:Number(document.getElementById('width').value),height:Number(document.getElementById('height').value)});});
document.getElementById('read').addEventListener('click',()=>request('/api/results'));
</script></main></html>'''


def strict_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('Duplicate JSON key')
        obj[key] = value
    return obj


def calculate(payload):
    if not isinstance(payload, dict) or set(payload) != {'width', 'height'}:
        raise ValueError('Expected exactly width and height in metres')
    for value in payload.values():
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1_000_000:
            raise ValueError('Dimensions must be finite numbers from 0 to 1000000')
    area = Decimal(str(payload['width'])) * Decimal(str(payload['height']))
    return {'width_m': payload['width'], 'height_m': payload['height'], 'area_m2': str(area)}


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address):
        self.tokens = {role: secrets.token_urlsafe(24) for role in ('reader', 'writer')}
        self.records = []
        self.record_lock = threading.Lock()
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        # Deliberately avoid recording Authorization headers or input data.
        pass

    def send(self, status, data, content_type='application/json; charset=utf-8'):
        raw = data.encode('utf-8') if isinstance(data, str) else json.dumps(data, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'")
        self.end_headers()
        self.wfile.write(raw)

    def permitted(self, write=False):
        auth = self.headers.get('Authorization', '')
        if not auth.isascii():
            self.send(401, {'error': 'Valid ephemeral demo token required'})
            return False
        role = next((r for r, t in self.server.tokens.items() if secrets.compare_digest(auth, 'Bearer '+t)), None)
        if role is None:
            self.send(401, {'error': 'Valid ephemeral demo token required'})
            return False
        if write and role != 'writer':
            self.send(403, {'error': 'Writer role required'})
            return False
        return True

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/':
            self.send(200, PAGE, 'text/html; charset=utf-8')
        elif path == '/api/health':
            self.send(200, {'status': 'ready', 'scope': 'synthetic demo only'})
        elif path == '/api/results':
            if self.permitted():
                with self.server.record_lock:
                    records = list(self.server.records)
                self.send(200, {'records': records})
        else:
            self.send(404, {'error': 'Unknown route'})

    def do_POST(self):
        if urlsplit(self.path).path != '/api/calculate':
            self.send(404, {'error': 'Unknown route'})
            return
        if not self.permitted(write=True):
            return
        if self.headers.get_content_type() != 'application/json':
            self.send(415, {'error': 'application/json required'})
            return
        try:
            if self.headers.get('Transfer-Encoding'):
                raise ValueError('Transfer encoding is unsupported')
            lengths = self.headers.get_all('Content-Length', [])
            if len(lengths) != 1 or not lengths[0].isdigit():
                raise ValueError('One Content-Length required')
            size = int(lengths[0])
            if not 0 < size <= 4096:
                self.send(413, {'error': 'Request must be 1..4096 bytes'})
                return
            self.connection.settimeout(3)
            raw = self.rfile.read(size)
            if len(raw) != size:
                raise ValueError('Incomplete JSON body')
            payload = json.loads(raw.decode('utf-8'), object_pairs_hook=strict_object,
                                 parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON')))
            result = calculate(payload)
        except (ValueError, OverflowError, TimeoutError):
            self.send(400, {'error': 'Invalid JSON or dimensions; use finite numbers in [0,1000000]'})
            return
        with self.server.record_lock:
            self.server.records.append(result)
            self.server.records = self.server.records[-20:]
        self.send(201, result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=['127.0.0.1', '0.0.0.0'], default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('port must be 0..65535')
    with DemoServer((args.host, args.port)) as server:
        print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}', 'ephemeral_demo_tokens': server.tokens,
                          'scope': 'Local educational example. No production identity, TLS, or persistence.'}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
