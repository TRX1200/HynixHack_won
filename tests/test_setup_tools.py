"""Regression checks for installation preservation and a usable MCP configuration."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_tool('setup_installer', ROOT / 'tools' / 'install_skills.py')


class SetupToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def config(self, *args):
        return subprocess.run(
            [sys.executable, '-B', str(ROOT / 'tools' / 'mcp_config.py'), *map(str, args)],
            capture_output=True, text=True, encoding='utf-8', timeout=15,
        )

    def index(self):
        path = self.root / 'synthetic index.jsonl'
        path.write_text(json.dumps({
            'id': 'synthetic-1', 'text': 'Local synthetic evidence only.',
            'source_file': 'synthetic.txt', 'source_sha256': '0' * 64,
            'locator': 'text',
        }) + '\n', encoding='utf-8')
        return path

    def test_duplicate_skill_selection_leaves_project_unchanged(self):
        with self.assertRaises(ValueError):
            installer.install(self.root, ['wb-start', 'wb-start'])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_empty_skill_selection_rejected(self):
        with self.assertRaises(ValueError):
            installer.install(self.root, [])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_installed_skill_preserves_original_license(self):
        installer.install(self.root, ['wb-start'])
        installed = self.root / '.agents' / 'skills' / 'wb-start'
        self.assertEqual((installed / 'LICENSE').read_bytes(), (ROOT / 'LICENSE').read_bytes())
        self.assertNotIn('__KIT_ROOT__', (installed / 'SKILL.md').read_text(encoding='utf-8'))

    def test_bad_later_skill_creates_nothing(self):
        with self.assertRaises(ValueError):
            installer.install(self.root, ['wb-start', 'wb-not-a-real-skill'])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_config_uses_real_executable_and_preserves_spaced_path(self):
        index = self.index()
        original = index.read_bytes()
        result = self.config('--index', index)
        self.assertEqual(result.returncode, 0, result.stderr)
        server = json.loads(result.stdout)['mcpServers']['local-evidence']
        self.assertEqual(Path(server['command']).resolve(), Path(sys.executable).resolve())
        self.assertEqual(server['args'], [str((ROOT / 'mcp' / 'local_evidence_server.py').resolve()), '--index', str(index.resolve())])
        self.assertEqual(index.read_bytes(), original)

    def test_config_refuses_invalid_or_empty_index(self):
        invalid = self.root / 'invalid.jsonl'
        for content in ['', '{"text":"missing required fields"}\n']:
            with self.subTest(content=content):
                invalid.write_text(content, encoding='utf-8')
                result = self.config('--index', invalid)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('error', json.loads(result.stderr))
                self.assertEqual(result.stdout, '')

    def test_config_refuses_missing_index(self):
        result = self.config('--index', self.root / 'missing.jsonl')
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stderr))

    def test_config_refuses_overwrite_without_changing_files(self):
        index = self.index()
        output = self.root / 'config.json'
        first = self.config('--index', index, '--out', output)
        self.assertEqual(first.returncode, 0, first.stderr)
        original = output.read_bytes()
        self.assertEqual(json.loads(original), json.loads(first.stdout))
        second = self.config('--index', index, '--out', output)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(output.read_bytes(), original)

    def test_generated_config_starts_server_and_lists_tools(self):
        result = self.config('--index', self.index())
        self.assertEqual(result.returncode, 0, result.stderr)
        server = json.loads(result.stdout)['mcpServers']['local-evidence']
        requests = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
                'protocolVersion': '2025-06-18', 'capabilities': {},
                'clientInfo': {'name': 'setup-smoke', 'version': '1'},
            }},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
        ]
        process = subprocess.run(
            [server['command'], *server['args']],
            input=''.join(json.dumps(r) + '\n' for r in requests),
            capture_output=True, text=True, encoding='utf-8', timeout=15,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        replies = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(len(replies), 2)
        self.assertEqual(len(replies[1]['result']['tools']), 3)


if __name__ == '__main__':
    unittest.main()
