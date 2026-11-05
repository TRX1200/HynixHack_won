import importlib.util
import json
from pathlib import Path
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('web_demo', ROOT/'tools/web_demo.py')
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)


class WebDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = web.DemoServer(('127.0.0.1', 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(3)

    def request(self, path, body=None, role='writer', extra=None):
        headers = {'Content-Type': 'application/json'}
        if role:
            headers['Authorization'] = 'Bearer '+self.server.tokens.get(role, 'invalid')
        headers.update(extra or {})
        req = Request(self.url+path, data=body, headers=headers)
        try:
            response = urlopen(req, timeout=4)
        except HTTPError as e:
            response = e
        with response:
            return response.status, response.read().decode('utf-8')

    def test_http_calculation_and_reader_lookup(self):
        status, raw = self.request('/api/calculate', b'{"width":2.5,"height":4}')
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(raw)['area_m2'], '10.0')
        status, raw = self.request('/api/results', role='reader')
        self.assertEqual(status, 200)
        self.assertIn('10.0', [r['area_m2'] for r in json.loads(raw)['records']])

    def test_unauthenticated_and_invalid_tokens_rejected(self):
        for role in (None, 'fake'):
            self.assertEqual(self.request('/api/results', role=role)[0], 401)
        self.assertEqual(self.request('/api/results', extra={'Authorization':'Bearer invalid-é'})[0], 401)

    def test_reader_cannot_write_even_with_claimed_role(self):
        before = len(self.server.records)
        self.assertEqual(self.request('/api/calculate', b'{"width":2,"height":3}', 'reader', {'X-Role':'writer'})[0], 403)
        self.assertEqual(len(self.server.records), before)

    def test_bad_values_and_shapes_rejected(self):
        for payload in ({'width':-1,'height':2}, {'width':True,'height':2}, {'width':'2','height':3},
                        {'width':2}, {'width':2,'height':3,'role':'writer'}, [], {'width':1000001,'height':1}):
            with self.subTest(payload=payload):
                self.assertEqual(self.request('/api/calculate', json.dumps(payload).encode())[0], 400)

    def test_malformed_duplicate_and_nonfinite_json(self):
        for body in (b'{', b'{"width":2,"width":3,"height":4}', b'{"width":NaN,"height":2}', b'{"width":1e400,"height":2}'):
            self.assertEqual(self.request('/api/calculate', body)[0], 400)

    def test_boundaries(self):
        self.assertEqual(json.loads(self.request('/api/calculate', b'{"width":0,"height":3}')[1])['area_m2'], '0')
        self.assertEqual(json.loads(self.request('/api/calculate', b'{"width":1000000,"height":1000000}')[1])['area_m2'], '1000000000000')

    def test_content_type_and_body_limit(self):
        self.assertEqual(self.request('/api/calculate', b'{}', extra={'Content-Type':'text/plain'})[0], 415)
        self.assertEqual(self.request('/api/calculate', b' '*4097)[0], 413)

    def test_ui_and_unknown_route(self):
        status, text = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn('id="calc"', text)
        self.assertEqual(self.request('/missing')[0], 404)


if __name__ == '__main__':
    unittest.main()
