"""Executed synthetic archetype checks; no optional dependency or network."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'field_inventory' / 'tools' / 'archetypes.py'
spec = importlib.util.spec_from_file_location('archetypes', SCRIPT)
archetypes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archetypes)


class ArchetypeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def fixture(self, family):
        return json.loads((archetypes.EXAMPLES / (family + '.json')).read_text(encoding='utf-8'))

    def assert_demo(self, family):
        destination = self.root / family
        result = archetypes.run_demo(family, destination)
        self.assertEqual(result['status'], 'PASS', result)
        self.assertEqual(len(result['checks']), 4)
        self.assertEqual(sum(check['polarity'] == 'negative' for check in result['checks']), 2)
        for check in result['checks']:
            self.assertEqual(check['status'], 'PASS', check)
            self.assertTrue((destination / check['evidence']).is_file())
        self.assertEqual(json.loads((destination / 'validation.json').read_text(encoding='utf-8')), result)
        self.assertTrue((destination / 'input.json').is_file())
        self.assertTrue((destination / 'result.json').is_file())
        return destination

    def test_data_two_detected_negatives_and_empty_boundary(self):
        folder = self.assert_demo('data')
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        self.assertEqual(result['join']['expected_inner_rows'], 5)
        self.assertEqual(result['join']['expected_left_join_rows'], 6)
        groups = {group['group']: group for group in result['aggregate']['groups']}
        self.assertEqual(groups['A']['sum'], '0.6')
        self.assertEqual(groups['B']['sum'], '0.5')
        self.assertIsNone(groups['C']['sum'])
        self.assertIn('001', (folder / 'left.csv').read_text(encoding='utf-8'))

    def test_assignment_two_detected_negatives_and_infeasible_boundary(self):
        folder = self.assert_demo('assignment')
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        self.assertEqual(result['cost'], '60')

    def test_assignment_exact_large_cost_oracle(self):
        fixture = {'items': [{'id': 'a'}], 'options': [
            {'id': 'expensive', 'unit_cost': '10000000000000000000000000001'},
            {'id': 'cheaper', 'unit_cost': '10000000000000000000000000000'}]}
        result = archetypes.solve_assignment(fixture)
        self.assertEqual(archetypes.validate_small_assignment(fixture, result), [])
        self.assertEqual(result['assignment'], {'a': 'cheaper'})

    def test_assignment_oracle_resource_limit(self):
        fixture = {'items': [{'id': str(i)} for i in range(8)], 'options': [{'id': 'a', 'unit_cost': '1'}]}
        with self.assertRaises(ValueError):
            archetypes.assignment_oracle(fixture)

    def test_timeseries_two_detected_negatives_and_minimum_boundary(self):
        folder = self.assert_demo('timeseries')
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        self.assertEqual(result['mae'], 2.5)
        self.assertEqual([row['prediction'] for row in result['predictions']], [13, 13])

    def test_timeseries_rejects_unsorted_and_duplicate_dates(self):
        fixture = self.fixture('timeseries')
        for duplicate in (False, True):
            bad = copy.deepcopy(fixture)
            if duplicate:
                bad['observations'][1]['date'] = bad['observations'][0]['date']
            else:
                bad['observations'][0], bad['observations'][1] = bad['observations'][1], bad['observations'][0]
            with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                archetypes.forecast_persistence(bad)

    def test_timeseries_rejects_no_holdout(self):
        fixture = self.fixture('timeseries')
        fixture['train_count'] = len(fixture['observations'])
        with self.assertRaises(ValueError):
            archetypes.forecast_persistence(fixture)

    def test_timeseries_rejects_nonfinite_holdout_error(self):
        fixture = {'train_count': 1, 'observations': [{'date': '2026-01-01', 'value': 1e308},
                                                    {'date': '2026-01-02', 'value': -1e308}]}
        with self.assertRaises(ValueError):
            archetypes.forecast_persistence(fixture)

    def test_image_two_detected_negatives_and_single_pixel_boundary(self):
        folder = self.assert_demo('image')
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        self.assertEqual((result['aligned']['dx'], result['aligned']['dy']), (1, 0))
        self.assertEqual(result['aligned']['changed_pixels'], 0)
        self.assertEqual(result['aligned']['overlap_pixels'], 20)
        self.assertEqual(result['unaligned']['changed_pixels'], 25)
        self.assertEqual(result['aligned']['ignored_border_pixels'], 5)

    def test_image_threshold_is_inclusive(self):
        fixture = {'reference': [[10, 10]], 'target': [[14, 13]], 'threshold': 4, 'max_shift': 0}
        result = archetypes.compare_matrices(fixture)
        self.assertEqual(result['unaligned']['mask'], [[1, 0]])

    def test_image_validator_rejects_aligned_result_disguised_as_unaligned(self):
        fixture = self.fixture('image')
        result = archetypes.compare_matrices(fixture)
        result['unaligned'] = copy.deepcopy(result['aligned'])
        self.assertTrue(archetypes.validate_matrix(fixture, result))

    def test_image_rejects_shape_and_boolean_pixel(self):
        for target in ([[1]], [[True, 2], [3, 4]]):
            fixture = {'reference': [[1, 2], [3, 4]], 'target': target, 'threshold': 1, 'max_shift': 0}
            with self.subTest(target=target), self.assertRaises(ValueError):
                archetypes.compare_matrices(fixture)

    def test_rc_two_detected_negatives_and_zero_voltage_boundary(self):
        folder = self.assert_demo('rc')
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        self.assertLess(result['fine_final_error_v'], result['coarse_final_error_v'])
        self.assertAlmostEqual(result['tau_s'], 0.001)
        self.assertAlmostEqual(result['analytic_final_v'], 0.24893534183931973)

    def test_rc_rejects_nonphysical_and_unstable_steps(self):
        for field, value in (('resistance_ohm', -1), ('steps', 1), ('capacitance_f', 0)):
            fixture = self.fixture('rc'); fixture[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                archetypes.simulate_rc(fixture)

    def test_rc_large_decay_does_not_overflow_analytic_validator(self):
        fixture = {'resistance_ohm': 1, 'capacitance_f': 1, 'initial_voltage_v': 5,
                   'duration_s': 1000, 'steps': 1000}
        result = archetypes.simulate_rc(fixture)
        self.assertEqual(archetypes.validate_rc(fixture, result), [])

    def test_rc_avoids_intermediate_current_overflow(self):
        fixture = {'resistance_ohm': 1, 'capacitance_f': 1e-309, 'initial_voltage_v': 1e308,
                   'duration_s': 1e-310, 'steps': 10}
        result = archetypes.simulate_rc(fixture)
        self.assertEqual(archetypes.validate_rc(fixture, result), [])

    def test_rc_rejects_unrepresentable_half_step(self):
        fixture = {'resistance_ohm': 1, 'capacitance_f': 1, 'initial_voltage_v': 5,
                   'duration_s': 5e-324, 'steps': 1}
        with self.assertRaises(ValueError):
            archetypes.simulate_rc(fixture)

    def test_documents_two_detected_negatives_and_first_valid_date(self):
        folder = self.assert_demo('documents')
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        self.assertEqual(result['eligible_sources'], ['policy-2026.md'])
        self.assertEqual({hit['source_file'] for hit in result['hits']}, {'policy-2026.md'})
        self.assertTrue(all(hit['untrusted_source_data'] for hit in result['hits']))

    def test_documents_last_valid_date_is_inclusive_and_expired_not_used(self):
        fixture = self.fixture('documents')
        for stamp, expected in (('2026-12-31', ['policy-2026.md']), ('2027-01-01', [])):
            fixture['as_of'] = stamp
            result = archetypes.retrieve_documents(fixture, archetypes.EXAMPLES, self.root / (stamp + '.jsonl'))
            self.assertEqual(result['eligible_sources'], expected)
            self.assertEqual(archetypes.validate_retrieval(fixture, archetypes.EXAMPLES, result), [])

    def test_document_validator_rejects_fabricated_excerpt(self):
        fixture = self.fixture('documents')
        result = archetypes.retrieve_documents(fixture, archetypes.EXAMPLES, self.root / 'index.jsonl')
        result['hits'][0]['snippet'] = 'Invented yield rule, not present in the source.'
        self.assertTrue(archetypes.validate_retrieval(fixture, archetypes.EXAMPLES, result))

    def test_refuses_existing_output_without_modifying_it(self):
        output = self.root / 'existing'; output.mkdir()
        marker = output / 'keep.txt'; marker.write_text('original', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            archetypes.run_demo('data', output)
        self.assertEqual(marker.read_text(encoding='utf-8'), 'original')
        self.assertEqual(list(output.iterdir()), [marker])

    def test_all_six_families_execute(self):
        result = archetypes.run_demo('all', self.root / 'all')
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual({row['family'] for row in result['families']}, set(archetypes.FAMILIES))
        self.assertEqual(sum(len(row['checks']) for row in result['families']), 24)

    def test_cli_works_from_another_current_directory(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), 'demo', 'rc', '--out', str(self.root / 'cli')],
                              cwd=self.root, text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['status'], 'PASS')

    def test_cli_utf8_output_under_non_utf8_locale(self):
        output = self.root / '\ud569\uc131-\uacb0\uacfc'
        env = {**os.environ, 'PYTHONIOENCODING': 'cp949', 'PYTHONUTF8': '0'}
        proc = subprocess.run([sys.executable, str(SCRIPT), 'demo', 'rc', '--out', str(output)],
                              cwd=self.root, env=env, text=True, encoding='utf-8', capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['out'], str(output))


if __name__ == '__main__':
    unittest.main()
