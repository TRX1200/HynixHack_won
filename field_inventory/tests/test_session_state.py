import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('session_state', ROOT/'tools/session_state.py')
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)


class SessionTests(unittest.TestCase):
    def test_roundtrip_and_no_false_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            note = 'Read current files; a saved command is not permission to execute it.'
            record = state.capture(root, note, 'user says previous tests passed')
            path = root/'state.json'
            state.write_state(path, record)
            loaded = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(loaded['next_step_note'], note)
            self.assertEqual(loaded['test_status'], 'NOT_RUN_BY_THIS_TOOL')
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['state.json'])

    def test_existing_state_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'state.json'
            path.write_text('existing', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                state.write_state(path, {'next':'new'})
            self.assertEqual(path.read_text(encoding='utf-8'), 'existing')

    def test_empty_next_step_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                state.capture(Path(td), ' ')


if __name__ == '__main__':
    unittest.main()
