import copy
import json
import unittest
from workbench.electronics import calculate


class ElectronicsTests(unittest.TestCase):
    def test_known_ohm_value_and_direction(self):
        # 12 V across 6 ohm gives 2 A; energy loss is 24 joule per second.
        for voltage, current in [(12, 2), (-12, -2), (0, 0)]:
            with self.subTest(voltage=voltage):
                result = calculate({'calculator':'ohm','voltage_v':voltage,'resistance_ohm':6})['results']
                self.assertEqual(result['current_a'], current)
                self.assertEqual(result['power_w'], 24 if voltage else 0)

    def test_known_rc_value(self):
        # 1 kilohm * 1 microfarad = 1 millisecond; reference 159.1549431 Hz.
        result = calculate({'calculator':'rc','resistance_ohm':1000,'capacitance_f':1e-6})['results']
        self.assertAlmostEqual(result['time_constant_s'], .001)
        self.assertAlmostEqual(result['cutoff_hz'], 159.15494309189535)

    def test_known_vacuum_capacitor(self):
        # OpenStax example geometry: 1 m^2 plates with 1 mm vacuum gap, about 8.85 nF.
        result = calculate({'calculator':'parallel_plate','relative_permittivity':1,'area_m2':1,'thickness_m':.001})['results']
        self.assertAlmostEqual(result['capacitance_f']/1e-9, 8.8541878188)

    def test_known_sheet_and_rectangular_resistance(self):
        # rho=1e-6 ohm m, t=1 micrometre => 1 ohm/square; L/W=10 => 10 ohm.
        result = calculate({'calculator':'thin_film','resistivity_ohm_m':1e-6,'length_m':1e-3,'width_m':1e-4,'thickness_m':1e-6})['results']
        self.assertAlmostEqual(result['sheet_resistance_ohm_per_square'], 1)
        self.assertAlmostEqual(result['resistance_ohm'], 10)

    def test_arrhenius_known_ratio_and_inverse(self):
        # Independent 60-digit Decimal reference using exact SI k_B and e.
        # Ea=0.5 eV, 300 K -> 600 K: exp(9.6704317679584...) ~= 15842.1876961.
        spec = {'calculator':'arrhenius','activation_energy_ev':.5,'temperature_1_k':300,'temperature_2_k':600}
        warm = calculate(spec)['results']['rate_ratio_t2_over_t1']
        self.assertAlmostEqual(warm, 15842.187696085138, places=6)
        reverse = calculate({**spec,'temperature_1_k':600,'temperature_2_k':300})['results']['rate_ratio_t2_over_t1']
        self.assertAlmostEqual(warm*reverse, 1)
        self.assertEqual(calculate({**spec,'activation_energy_ev':0})['results']['rate_ratio_t2_over_t1'], 1)
        self.assertEqual(calculate({**spec,'temperature_2_k':300})['results']['rate_ratio_t2_over_t1'], 1)

    def test_known_diffusion_distance_and_time_scaling(self):
        # 2*1e-14 m^2/s*50 s = 1e-12 m^2 => 1 micrometre RMS.
        spec = {'calculator':'diffusion_1d','diffusivity_m2_per_s':1e-14,'time_s':50}
        self.assertAlmostEqual(calculate(spec)['results']['rms_displacement_m']/1e-6, 1)
        self.assertAlmostEqual(calculate({**spec,'time_s':200})['results']['rms_displacement_m']/1e-6, 2)
        self.assertEqual(calculate({**spec,'time_s':0})['results']['rms_displacement_m'], 0)

    def test_area_and_thickness_scaling(self):
        spec = {'calculator':'parallel_plate','relative_permittivity':3.9,'area_m2':1e-8,'thickness_m':1e-8}
        base = calculate(spec)['results']['capacitance_f']
        doubled_area = calculate({**spec,'area_m2':2e-8})['results']['capacitance_f']
        doubled_thickness = calculate({**spec,'thickness_m':2e-8})['results']['capacitance_f']
        self.assertAlmostEqual(doubled_area/base, 2)
        self.assertAlmostEqual(doubled_thickness/base, .5)

    def test_square_resistance_independent_of_lateral_size(self):
        spec = {'calculator':'thin_film','resistivity_ohm_m':1e-6,'length_m':1e-3,'width_m':1e-3,'thickness_m':1e-6}
        self.assertEqual(calculate(spec)['results']['resistance_ohm'], 1)
        self.assertEqual(calculate({**spec,'length_m':2e-3,'width_m':2e-3})['results']['resistance_ohm'], 1)

    def test_input_unchanged_and_json_finite(self):
        spec = {'calculator':'rc','resistance_ohm':1000,'capacitance_f':1e-6}
        original = copy.deepcopy(spec)
        output = calculate(spec)
        self.assertEqual(spec, original)
        self.assertEqual(json.loads(json.dumps(output, allow_nan=False)), output)

    def test_strict_fields_and_numeric_types(self):
        good = {'calculator':'ohm','voltage_v':12,'resistance_ohm':6}
        bad = [None, [], {}, {**good,'extra':1}, {'calculator':'unknown'},
               {**good,'resistance_ohm':0}, {**good,'resistance_ohm':-1}]
        bad.extend({**good,'voltage_v':value} for value in [True,'12',None,float('nan'),float('inf'),10**1000])
        for spec in bad:
            with self.subTest(spec_type=type(spec).__name__), self.assertRaises(ValueError):
                calculate(spec)

    def test_temperature_requires_kelvin_above_zero(self):
        for temperature in [0,-273.15]:
            with self.subTest(temperature=temperature), self.assertRaises(ValueError):
                calculate({'calculator':'arrhenius','activation_energy_ev':.5,'temperature_1_k':temperature,'temperature_2_k':600})

    def test_overflow_and_underflow_fail_explicitly(self):
        for spec in [
            {'calculator':'ohm','voltage_v':1e308,'resistance_ohm':1e-308},
            {'calculator':'rc','resistance_ohm':1e-300,'capacitance_f':1e-300},
            {'calculator':'arrhenius','activation_energy_ev':100,'temperature_1_k':1,'temperature_2_k':1000},
            {'calculator':'arrhenius','activation_energy_ev':100,'temperature_1_k':1000,'temperature_2_k':1},
        ]:
            with self.subTest(calculator=spec['calculator']), self.assertRaises(ValueError):
                calculate(spec)


if __name__ == '__main__':
    unittest.main()
