import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

from workbench.documents import extract_to_index, extract_units, load_index, search_chunks
from workbench.optimization import solve_assignment, validate_assignment
from workbench.reporting import normalize_report


class OptionalRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_docx_preserves_tabs_and_line_breaks(self):
        path = self.root / 'spacing.docx'
        xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
               '<w:body><w:p><w:r><w:t>A</w:t><w:tab/><w:t>B</w:t>'
               '<w:br/><w:t>C</w:t><w:cr/><w:t>D</w:t></w:r></w:p></w:body></w:document>')
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('word/document.xml', xml)
        self.assertEqual(extract_units(path)[0]['text'], 'A\tB\nC\nD')

    def test_extraction_refuses_chunks_its_loader_cannot_read(self):
        source = self.root / 'long-line.txt'
        source.write_text('a' * 200_001, encoding='utf-8')
        output = self.root / 'index.jsonl'
        with self.assertRaisesRegex(ValueError, '[Cc]hunk'):
            extract_to_index([str(source)], str(output))
        self.assertFalse(output.exists())

    def test_index_rejects_duplicate_json_keys(self):
        index = self.root / 'index.jsonl'
        index.write_text('{"id":"first","id":"second","text":"content",'
                         '"source_file":"source","source_sha256":"abc","locator":"text"}',
                         encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '[Dd]uplicate'):
            load_index(index)

    def test_casefold_expansion_does_not_displace_search_snippet(self):
        chunks = [{'id': '1', 'text': '\u00df' * 2_000 + 'needle', 'source_file': 'source',
                   'source_sha256': 'abc', 'locator': 'text'}]
        result = search_chunks(chunks, 'needle')
        self.assertIn('needle', result['hits'][0]['snippet'])

    def test_assignment_preserves_cost_difference_beyond_28_digits(self):
        expensive = '10000000000000000000000000001'
        cheaper = '10000000000000000000000000000'
        spec = {'items': [{'id': 'a'}], 'options': [
            {'id': 'expensive', 'unit_cost': expensive},
            {'id': 'cheaper', 'unit_cost': cheaper},
        ]}
        self.assertEqual(validate_assignment(spec, {'a': 'expensive'})['recomputed_cost'], expensive)
        result = solve_assignment(spec)
        self.assertEqual(result['status'], 'OPTIMAL_ENUMERATED')
        self.assertEqual(result['assignment'], {'a': 'cheaper'})
        self.assertEqual(result['cost'], cheaper)

    def test_validation_cannot_bypass_status_with_free_text(self):
        with self.assertRaises(ValueError):
            normalize_report({'title': 'Report', 'validation': 'All checks passed.'})

    def test_executed_validation_requires_nonblank_text_evidence(self):
        for evidence in [' ', 123, ['test.log']]:
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                normalize_report({'title': 'Report', 'validation': [{
                    'check': 'Example', 'expected': '1', 'actual': '1',
                    'status': 'pass', 'evidence': evidence,
                }]})

    @unittest.skipUnless(importlib.util.find_spec('PIL'), 'Pillow unavailable')
    def test_transparency_does_not_silently_disappear(self):
        from PIL import Image
        from workbench.images import difference
        reference = self.root / 'transparent.png'
        target = self.root / 'opaque.png'
        Image.new('RGBA', (2, 2), (0, 0, 0, 0)).save(reference)
        Image.new('RGBA', (2, 2), (0, 0, 0, 255)).save(target)
        output = self.root / 'mask.png'
        with self.assertRaisesRegex(ValueError, '[Tt]ransparen'):
            difference(str(reference), str(target), str(output))
        self.assertFalse(output.exists())

    @unittest.skipUnless(importlib.util.find_spec('PIL'), 'Pillow unavailable')
    def test_luminance_metric_is_difference_of_luminance(self):
        from PIL import Image
        from workbench.images import difference
        reference = self.root / 'red.png'
        target = self.root / 'green.png'
        Image.new('RGB', (2, 2), (255, 0, 0)).save(reference)
        Image.new('RGB', (2, 2), (0, 130, 0)).save(target)
        result = difference(str(reference), str(target), str(self.root / 'mask.png'))
        self.assertEqual(result['mean_absolute_luminance_difference'], 0)
        self.assertEqual(result['changed_pixel_count'], 4)


if __name__ == '__main__':
    unittest.main()
