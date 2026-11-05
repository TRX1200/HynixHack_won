"""Independent routing scenarios and adversarial profile/catalog regression tests."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/inventory.py'
sp=importlib.util.spec_from_file_location('inventory_hardened',SCRIPT)
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
CARDS=mod.load_catalog()

# Hand-authored expected model choices, not generated from the rules' recommendations.
# Every one of the 29 explicit rule branches has a positive and a missing-fact control.
CASES=[
 ('graph-unweighted','optimization',{'problem_structure':'shortest_path','edge_weight_type':'unweighted'},'unweighted-shortest'),
 ('graph-nonnegative','optimization',{'problem_structure':'shortest_path','edge_weight_type':'nonnegative'},'weighted-shortest'),
 ('graph-negative','optimization',{'problem_structure':'shortest_path','edge_weight_type':'may_be_negative'},'negative-shortest'),
 ('assignment-one-to-one','optimization',{'problem_structure':'assignment','capacity_model':'one_to_one'},'bipartite-match'),
 ('assignment-many-to-one','optimization',{'problem_structure':'assignment','capacity_model':'many_to_one'},'min-cost-flow'),
 ('assignment-facilities','optimization',{'problem_structure':'facility_location'},'facility-location'),
 ('routing-single','optimization',{'problem_structure':'routing','vehicle_count':'one'},'traveling-salesman'),
 ('routing-multi','optimization',{'problem_structure':'routing','vehicle_count':'multiple'},'vehicle-routing'),
 ('routing-directed','optimization',{'problem_structure':'routing','travel_cost_directional':True},'local-search'),
 ('schedule-cumulative','optimization',{'problem_structure':'scheduling','has_resource_constraints':True},'resource-schedule'),
 ('schedule-simple','optimization',{'problem_structure':'scheduling','has_resource_constraints':False,'interval_model_confirmed':True},'interval-schedule'),
 ('resource-fractional','optimization',{'problem_structure':'resource_allocation','decision_variable_type':'continuous','linear_model_confirmed':True},'linear-programming'),
 ('resource-discrete','optimization',{'problem_structure':'resource_allocation','decision_variable_type':'integer'},'mixed-integer'),
 ('budget-selection','optimization',{'problem_structure':'knapsack'},'knapsack'),
 ('opt-uncertain','optimization',{'uncertainty_model':'scenarios'},'robust-optimization'),
 ('opt-probabilistic','optimization',{'uncertainty_model':'probability'},'stochastic-optimization'),
 ('ml-temporal','statistics_ml',{'task_subtype':'time_series_forecast'},'forecasting'),
 ('ml-classify','statistics_ml',{'task_subtype':'classification'},'classification'),
 ('ml-regress','statistics_ml',{'task_subtype':'regression'},'regression'),
 ('ml-hypothesis','statistics_ml',{'task_subtype':'hypothesis_test'},'hypothesis-test'),
 ('vision-alignment','computer_vision',{'task_subtype':'image_comparison'},'image-registration'),
 ('vision-segmentation','computer_vision',{'task_subtype':'segmentation'},'image-segmentation'),
 ('physics-ode','scientific_computing',{'task_subtype':'ode'},'physics-ode'),
 ('physics-pde','scientific_computing',{'task_subtype':'pde'},'physics-pde'),
 ('document-retrieve','documents_search',{'task_subtype':'policy_retrieval'},'text-index'),
 ('app-auth','web_app',{'requires_role_authorization':True},'role-access'),
 ('app-calc','web_app',{'requires_api_calculation':True},'input-validation'),
 ('runtime-no-docker','integration',{'docker_available':False},'runtime-diagnose'),
 ('offline-no-external','integration',{'network_allowed':False},'runtime-diagnose'),
]

def selected(plan):
    return [card['id'] for cards in plan['recommended'].values() for card in cards]

class DecisionScenarioTests(unittest.TestCase):
    def test_all_29_positive_choices(self):
        self.assertEqual({case[0] for case in CASES},{rule['id'] for rule in mod._asset_rows(CARDS)[0]})
        for rule_id,family,properties,expected in CASES:
            with self.subTest(rule=rule_id):
                output=mod.plan({'task_types':[family],'properties':properties},CARDS)
                self.assertIn(rule_id,[item['id'] for item in output['decision_gates_applied']])
                self.assertIn(expected,selected(output))
                self.assertNotEqual(output['status'],'REVIEW_REQUIRED')

    def test_every_required_fact_missing_disables_its_rule(self):
        for rule_id,family,properties,_ in CASES:
            for field in properties:
                with self.subTest(rule=rule_id,missing=field):
                    incomplete={key:value for key,value in properties.items() if key!=field}
                    rules=mod.match_decision_rules({'task_types':[family],'properties':incomplete})
                    self.assertNotIn(rule_id,[rule['id'] for rule in rules])

    def test_avoid_is_exclusion_even_when_explicitly_requested(self):
        rules={rule['id']:rule for rule in mod._asset_rows(CARDS)[0]}
        for rule_id,family,properties,_ in CASES:
            avoided=rules[rule_id]['avoid']
            if not avoided:continue
            with self.subTest(rule=rule_id):
                output=mod.plan({'task_types':[family],'properties':properties,
                    'summary':' '.join(avoided*20),'required_capabilities':avoided},CARDS)
                self.assertFalse(set(avoided)&set(selected(output)))
                self.assertEqual(output['status'],'REVIEW_REQUIRED')

    def test_global_budget_and_no_duplicate_cards_for_11_families(self):
        profile={'task_types':sorted(mod.VALID_TYPES),
            'summary':'API role browser CSV join statistics image physics graph document policy report integration security'}
        for limit in range(2,7):
            with self.subTest(limit=limit):
                output=mod.plan(profile,CARDS,limit)
                ids=selected(output)
                self.assertLessEqual(len(ids),limit)
                self.assertEqual(len(ids),len(set(ids)))
                self.assertEqual(output['selection_summary']['total_cards'],len(ids))
                self.assertEqual(set(output['validators']),mod.VALID_TYPES)

    def test_directionality_does_not_override_vehicle_count(self):
        for count,correct,wrong in [('one','traveling-salesman','vehicle-routing'),('multiple','vehicle-routing','traveling-salesman')]:
            with self.subTest(count=count):
                output=mod.plan({'task_types':['optimization'],'summary':wrong,
                    'properties':{'problem_structure':'routing','vehicle_count':count,'travel_cost_directional':True}},CARDS)
                self.assertIn(correct,selected(output));self.assertNotIn(wrong,selected(output))
                self.assertNotEqual(output['status'],'REVIEW_REQUIRED')

    def test_negative_edges_contradiction_requires_review(self):
        output=mod.plan({'task_types':['optimization'],'summary':'Dijkstra shortest path',
            'properties':{'problem_structure':'shortest_path','edge_weight_type':'nonnegative','has_negative_edges':True}},CARDS)
        self.assertEqual(output['status'],'REVIEW_REQUIRED')
        self.assertNotIn('weighted-shortest',selected(output))

    def test_unknown_edge_weights_do_not_choose_algorithm(self):
        output=mod.plan({'task_types':['optimization'],'summary':'가중치 최단 경로 Dijkstra BFS',
            'properties':{'problem_structure':'shortest_path','edge_weight_type':'unknown'}},CARDS)
        self.assertFalse({'weighted-shortest','unweighted-shortest','negative-shortest'}&set(selected(output)))
        self.assertTrue(any('edges' in question for question in output['questions']))

    def test_continuous_does_not_imply_linear_or_integer_solver(self):
        output=mod.plan({'task_types':['optimization'],'summary':'LP mixed integer resource allocation',
            'properties':{'problem_structure':'resource_allocation','decision_variable_type':'continuous'}},CARDS)
        self.assertFalse({'linear-programming','mixed-integer','constraint-sat'}&set(selected(output)))
        self.assertTrue(any('linear' in question for question in output['questions']))

    def test_no_model_does_not_fill_with_arbitrary_algorithms(self):
        output=mod.plan({'task_types':['optimization'],'summary':'make something impressive'},CARDS)
        self.assertEqual(output['status'],'NEEDS_CLASSIFICATION')
        self.assertEqual(selected(output),['intake-requirements'])

    def test_permission_disagreement_uses_restrictive_branch(self):
        output=mod.plan({'task_types':['documents_search'],'environment':{'network_allowed':False},
            'properties':{'network_allowed':True},'summary':'semantic retrieval'},CARDS)
        self.assertEqual(output['status'],'REVIEW_REQUIRED')
        self.assertNotIn('semantic-retrieval',selected(output))
        self.assertIn('offline-no-external',[rule['id'] for rule in output['decision_gates_applied']])

class PatternAndEnvironmentTests(unittest.TestCase):
    def test_existing_node_permission_fix_never_recommends_python_or_new_react(self):
        profile={'task_types':['web_app','quality_security'],
            'summary':'Fix server-side permissions in existing Node application; viewer cannot mutate protected state',
            'hard_constraints':['Preserve existing Node framework','Python unavailable','No additional service'],
            'environment':{'existing_stack':'Node.js application; framework unknown','python_available':False,'network_allowed':False},
            'properties':{'requires_role_authorization':True}}
        output=mod.plan(profile,CARDS)
        self.assertNotIn('api-python',selected(output))
        self.assertNotIn('frontend-react',selected(output))
        self.assertIn('role-access',selected(output))
        self.assertFalse(any(name in card['why'] for cards in output['recommended'].values() for card in cards
                             for name in ['Python available','React available']))

    def test_negative_shortest_path_does_not_offer_greedy_or_integer_templates(self):
        output=mod.plan({'task_types':['optimization'],
            'summary':'Directed shortest path with negative edge costs and negative-cycle detection',
            'properties':{'problem_structure':'shortest_path','edge_weight_type':'may_be_negative'}},CARDS)
        self.assertIn('negative-shortest',selected(output))
        self.assertFalse({'opt-greedy-check','opt-ortools','graph-stdlib'}&
                         {item['id'] for item in output['code_pattern_candidates']})

    def test_node_backend_preserved_over_python_keyword(self):
        output=mod.plan({'task_types':['web_app'],'summary':'Python API calculation',
            'environment':{'existing_stack':'Node/Express','node_available':True,'python_available':False},
            'properties':{'requires_api_calculation':True}},CARDS)
        self.assertIn('api-node',selected(output));self.assertNotIn('api-python',selected(output))
        self.assertEqual(output['code_pattern_candidates'][0]['id'],'node-vanilla')
        self.assertTrue(all(item['status']=='REFERENCE_PATTERN_NOT_EXECUTABLE' and item['implemented'] is False
                            for item in output['code_pattern_candidates']))

    def test_python_backend_does_not_add_node_server(self):
        output=mod.plan({'task_types':['web_app'],'summary':'Node API',
            'environment':{'existing_stack':'FastAPI','python_available':True},
            'properties':{'requires_api_calculation':True}},CARDS)
        self.assertIn('api-python',selected(output));self.assertNotIn('api-node',selected(output))
        self.assertNotIn('node-vanilla',[item['id'] for item in output['code_pattern_candidates']])

    def test_static_ui_does_not_force_new_runtime_or_react(self):
        output=mod.plan({'task_types':['web_app'],'summary':'Static information page'},CARDS)
        self.assertEqual(output['code_pattern_candidates'],[])

    def test_absent_libraries_exclude_optional_pattern(self):
        profile={'task_types':['data_pipeline'],'environment':{'python_available':True,
                 'installed_libraries':['Python stdlib'],'library_inventory_complete':True}}
        self.assertNotIn('pandas-duckdb',[item['id'] for item in mod.plan(profile,CARDS)['code_pattern_candidates']])
        self.assertEqual(mod._library_state(profile,'pandas'),'UNAVAILABLE')

    def test_unreported_libraries_are_unknown_not_present(self):
        self.assertEqual(mod._library_state({'environment':{'installed_libraries':['numpy']}},'pandas'),'UNKNOWN')
        self.assertEqual(mod._library_state({'environment':{'installed_libraries':['scipy']}},'scipy.integrate'),'REPORTED_PRESENT_VERIFY')
        self.assertEqual(mod._library_state({'environment':{'installed_libraries':['scipythings']}},'scipy'),'UNKNOWN')

    def test_numpy_alone_is_not_scipy(self):
        profile={'task_types':['scientific_computing'],'environment':{'python_available':True,'installed_libraries':['numpy']}}
        self.assertEqual(mod._library_state(profile,'scipy'),'UNKNOWN')
        self.assertTrue(all('availability' in item for item in mod.plan(profile,CARDS)['code_pattern_candidates']))

    def test_docker_and_mcp_not_recommended_from_name_only(self):
        output=mod.plan({'task_types':['integration'],'summary':'Docker MCP microservice'},CARDS)
        self.assertFalse({'container-optional','mcp-local-optional'}&{item['id'] for item in output['code_pattern_candidates']})

    def test_conflicting_runtime_or_library_claim_requires_review(self):
        for env in [{'existing_stack':'Node/Express','node_available':False},
                    {'installed_libraries':['pandas'],'unavailable_libraries':['pandas']}]:
            with self.subTest(env=env):
                self.assertEqual(mod.plan({'task_types':['integration'],'environment':env},CARDS)['status'],'REVIEW_REQUIRED')

class StrictInputTests(unittest.TestCase):
    def test_nested_profiles_reject_bad_shape_bool_numbers_and_unknown_fields(self):
        examples=[{'environment':{'installed_libraries':'numpy'}},{'environment':{'network_allowed':0}},
            {'environment':{'network_allowed':'false'}},{'properties':{'has_resource_constraints':1}},
            {'properties':{'edge_weight_type':['nonnegative']}},{'objective':[]},{'evaluation':[]},
            {'evaluation':{'metrics':'accuracy'}},{'data':{'rows':True}}, {'data':{'rows':-1}},
            {'performance':{'time_budget_s':True}}, {'performance':{'time_budget_s':float('nan')}},
            {'signals':[{}]},{'required_capabilities':[False]},{'user_roles':'admin'},
            {'environment':{'secret_command':'echo nope'}},{'task_types':['web_app','web_app']},
            {'properties':{'requires_role_authorization':False,'extra_fact':True}}]
        for extra in examples:
            with self.subTest(extra=repr(extra)):
                self.assertTrue(mod.validate_profile({'task_types':['web_app'],**extra}))

    def test_strict_json_duplicate_nonfinite_and_underflow(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'profile.json'
            for text in ['{"task_types":[],"task_types":["optimization"]}',
                         '{"task_types":[],"performance":{"time_budget_s":NaN}}',
                         '{"task_types":[],"performance":{"time_budget_s":1e999}}',
                         '{"task_types":[],"performance":{"time_budget_s":1e-999}}']:
                with self.subTest(text=text):
                    path.write_text(text,encoding='utf-8')
                    with self.assertRaises(ValueError):mod.read_profile(path)

    def test_catalog_rejects_nested_shapes_and_path_ids(self):
        for key,value in [('signals','foo'),('signals',[{}]),('task_types',[[]]),('libraries',[True]),('family',[]),
                          ('verified_commands','pytest'),('id','../outside'),('id','C:/outside'),('id','a/b')]:
            bad=copy.deepcopy(CARDS);bad[0][key]=value
            with self.subTest(key=key,value=value):self.assertTrue(mod.validate_catalog(bad))
        self.assertTrue(mod.validate_catalog([False]));self.assertTrue(mod.validate_catalog({}))

    def test_related_catalog_bad_references_and_boolean_rule_types(self):
        original=mod.read_json
        for path,key in [(mod.DECISIONS,'rules'),(mod.CODE_PATTERNS,'patterns'),(mod.ALIASES,'aliases')]:
            raw=copy.deepcopy(original(path))
            if key=='rules':raw[key][0]['when']={'network_allowed':0}
            elif key=='patterns':raw[key][0]['implemented']=True
            else:raw[key][0]['capability_ids']=['not-a-card']
            def fake(requested,**kwargs):return raw if Path(requested)==path else original(requested,**kwargs)
            with self.subTest(asset=key),patch.object(mod,'read_json',side_effect=fake):
                with self.assertRaises(ValueError):mod._asset_rows(CARDS)

    def test_catalog_paths_cannot_escape_and_deep_json_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'external.json';path.write_text('{}',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'escapes'):mod.read_json(path,internal=True)
            path.write_text('['*2000+'0'+']'*2000,encoding='utf-8')
            with self.assertRaises(ValueError):mod.read_profile(path)

    def test_numeric_boolean_cannot_activate_any_boolean_rule(self):
        for rule_id,family,properties,_ in CASES:
            for field,value in properties.items():
                if type(value) is bool:
                    bad={**properties,field:int(value)}
                    with self.subTest(rule=rule_id,field=field),self.assertRaises(ValueError):
                        mod.match_decision_rules({'task_types':[family],'properties':bad})

    def test_budget_and_empty_query_rejected(self):
        for limit in [True,0,1,7,2.5,'6']:
            with self.subTest(limit=limit),self.assertRaises(ValueError):mod.plan({'task_types':[]},CARDS,limit)
        for query in ['', '   ',None,'x'*2001]:
            with self.subTest(query_type=type(query).__name__),self.assertRaises(ValueError):mod.search_cards(CARDS,query)

    def test_cli_compact_search_and_show_details_ascii_transport(self):
        env={**os.environ,'PYTHONIOENCODING':'ascii'}
        completed=subprocess.run([sys.executable,str(SCRIPT),'search','버스 노선 최적화','--json'],
            capture_output=True,env=env,timeout=30)
        self.assertEqual(completed.returncode,0,completed.stderr)
        data=json.loads(completed.stdout.decode('utf-8'))
        self.assertLessEqual(len(data),6);self.assertNotIn('baseline',data[0])
        shown=subprocess.run([sys.executable,str(SCRIPT),'show',data[0]['id']],capture_output=True,env=env,timeout=30)
        self.assertIn('baseline',json.loads(shown.stdout.decode('utf-8')))

if __name__=='__main__':unittest.main()
