"""Behavior and hostile-input tests for the offline UI router."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('ui_router',ROOT/'tools/ui_router.py')
mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(mod)

def profile(goal='analyze',**changes):
    return {'primary_goal':goal,'ui_required':True,'geo_is_primary':False,
            'roles':[],'records_volume':'small',**changes}

class UIRouterTests(unittest.TestCase):
    def test_five_nonmap_workflows_have_distinct_primary_patterns(self):
        expected={'analyze':'dashboard','manage':'admin-workspace','submit':'input-form',
                  'explore':'search-detail','present':'presentation'}
        for goal,pattern in expected.items():
            with self.subTest(goal=goal):self.assertEqual(mod.route(profile(goal))['recommended_pattern'],pattern)

    def test_admin_role_alone_does_not_choose_management_layout(self):
        output=mod.route(profile('analyze',roles=['admin','user']))
        self.assertEqual(output['recommended_pattern'],'dashboard')
        self.assertIn('server-side',output['authorization_note'])
        self.assertIn('role-access',output['inventory_cards'])

    def test_large_volume_alone_does_not_choose_management(self):
        self.assertEqual(mod.route(profile('explore',records_volume='large'))['recommended_pattern'],'search-detail')

    def test_map_requires_explicit_geographic_priority(self):
        self.assertEqual(mod.route(profile('locate',geo_is_primary=True))['recommended_pattern'],'map-explorer')
        unknown=mod.route(profile('locate',geo_is_primary=None))
        self.assertEqual(unknown['status'],'NEEDS_CLASSIFICATION');self.assertIsNone(unknown['recommended_pattern'])
        conflict=mod.route(profile('locate',geo_is_primary=False))
        self.assertEqual(conflict['status'],'REVIEW_REQUIRED');self.assertIsNone(conflict['recommended_pattern'])

    def test_geographic_exploration_has_offline_list_fallback(self):
        output=mod.route(profile('explore',geo_is_primary=True))
        self.assertEqual(output['recommended_pattern'],'map-explorer')
        self.assertFalse(output['external_network_required']);self.assertFalse(output['api_key_required'])
        self.assertIn('table/list',output['fallback'])

    def test_no_ui_does_not_recommend_ui_cards(self):
        output=mod.route(profile('analyze',ui_required=False,roles=['admin']))
        self.assertEqual(output['recommended_pattern'],'none');self.assertEqual(output['inventory_cards'],[])
        self.assertEqual(output['documents'],[]);self.assertEqual(output['review_documents'],[])

    def test_no_ui_ignores_ui_only_geographic_conflicts(self):
        for data in [profile('locate',ui_required=False,geo_is_primary=False),
                     profile('manage',ui_required=False,geo_is_primary=True),
                     profile('unknown',ui_required=False,geo_is_primary=None,records_volume='unknown')]:
            with self.subTest(data=data):
                output=mod.route(data)
                self.assertEqual(output['recommended_pattern'],'none')
                self.assertEqual(output['status'],'DRAFT_UI_PLAN');self.assertEqual(output['conflicts'],[])
                self.assertEqual(output['documents'],[]);self.assertEqual(output['inventory_cards'],[])

    def test_record_volume_and_nonmap_geo_unknown_do_not_block_known_workflow(self):
        for goal,pattern in [('submit','input-form'),('manage','admin-workspace'),('analyze','dashboard')]:
            with self.subTest(goal=goal):
                output=mod.route(profile(goal,geo_is_primary=None,records_volume='unknown'))
                self.assertEqual(output['recommended_pattern'],pattern)
                self.assertEqual(output['status'],'DRAFT_UI_PLAN');self.assertTrue(output['questions'])

    def test_visual_review_is_separate_from_initial_design_documents(self):
        output=mod.route(profile('analyze'))
        self.assertNotIn('docs/ui/VISUAL_REVIEW.md',output['documents'])
        self.assertEqual(output['review_documents'],['docs/ui/VISUAL_REVIEW.md'])
        self.assertEqual(output['document_phases']['review_documents'],'after_a_usable_ui_exists')

    def test_unknown_goal_and_unknown_ui_are_not_guessed_from_constraints(self):
        for data in [profile('unknown',constraints=['Build a dashboard map with admin roles']),
                     profile('analyze',ui_required=None),profile('locate',geo_is_primary=None)]:
            with self.subTest(data=data):
                output=mod.route(data);self.assertEqual(output['status'],'NEEDS_CLASSIFICATION')
                self.assertIsNone(output['recommended_pattern'])

    def test_existing_ui_requires_review_and_is_preserved(self):
        output=mod.route(profile('manage',existing_ui='Existing static table and detail drawer'))
        self.assertEqual(output['status'],'REVIEW_REQUIRED')
        self.assertTrue(output['existing_ui_policy']['preserve_existing'])
        self.assertFalse(output['existing_ui_policy']['replacement_authorized'])

    def test_explicit_competing_primary_goals_require_review(self):
        output=mod.route(profile('submit',geo_is_primary=True))
        self.assertEqual(output['status'],'REVIEW_REQUIRED');self.assertIsNone(output['recommended_pattern'])

    def test_document_and_card_limits_use_actual_catalog_ids(self):
        ids={row['id'] for row in json.loads((ROOT/'field_inventory/catalog/capabilities.json').read_text(encoding='utf-8'))['capabilities']}
        for goal in sorted(mod.GOALS):
            output=mod.route(profile(goal,geo_is_primary=goal=='locate',roles=['admin']))
            self.assertLessEqual(len(output['documents']),4);self.assertLessEqual(len(output['inventory_cards']),3)
            self.assertTrue(set(output['inventory_cards'])<=ids)
            if output['recommended_pattern']=='none':self.assertEqual(output['documents'],[])
            else:self.assertEqual(output['documents'][:2],mod.COMMON_DOCS)

    def test_inputs_are_preserved(self):
        data=profile('analyze',roles=['viewer'],constraints=['Do not add packages'])
        original=copy.deepcopy(data);mod.route(data);self.assertEqual(data,original)

    def test_invalid_shapes_bool_numeric_and_unknown_fields_fail(self):
        bad=[None,[],{},profile(primary_goal='magic'),profile(ui_required=1),profile(geo_is_primary=0),
             profile(roles='admin'),profile(roles=[{}]),profile(roles=['admin','admin']),
             profile(records_volume=100),profile(constraints=[False]),profile(existing_ui={}),
             profile(extra_command='run anything')]
        for value in bad:
            with self.subTest(value=repr(value)),self.assertRaises(ValueError):mod.route(value)

    def test_strict_file_json_duplicate_nan_nested_and_size(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'profile.json'
            for text in ['{"ui_required":true,"ui_required":false}', '{"unknown":NaN}',
                         '{"unknown":1e999}', '['*2000+'0'+']'*2000, ' '*65537]:
                with self.subTest(prefix=text[:30]):
                    path.write_text(text,encoding='utf-8')
                    with self.assertRaises(ValueError):mod.read_profile(path)

    def test_cli_ascii_stdout_and_errors(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'profile.json';path.write_text(json.dumps(profile('analyze',id='한글 🔬')),encoding='utf-8')
            result=subprocess.run([sys.executable,str(ROOT/'tools/ui_router.py'),str(path),'--json'],
                capture_output=True,env={**os.environ,'PYTHONIOENCODING':'ascii'},timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout.decode('utf-8'))['profile_id'],'한글 🔬')
            path.write_text('{"ui_required":NaN}',encoding='utf-8')
            result=subprocess.run([sys.executable,str(ROOT/'tools/ui_router.py'),str(path),'--json'],capture_output=True,timeout=10)
            self.assertEqual(result.returncode,2);self.assertEqual(json.loads(result.stdout)['status'],'ERROR')

    def test_synthetic_examples_valid_and_cover_workflows(self):
        paths=list((ROOT/'examples/ui').glob('*.json'));self.assertGreaterEqual(len(paths),5)
        choices={mod.route(mod.read_profile(path))['recommended_pattern'] for path in paths}
        self.assertTrue({'dashboard','admin-workspace','input-form','map-explorer','search-detail','presentation','none',None}<=choices)

if __name__=='__main__':unittest.main()
