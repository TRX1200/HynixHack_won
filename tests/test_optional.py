import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from workbench.documents import extract_units

class OptionalTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def image(self,name,size=(64,64),color='white'):
        from PIL import Image
        p=self.root/name;Image.new('RGB',size,color).save(p);return str(p)
    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow unavailable')
    def test_contact_sheet(self):
        from workbench.images import contact_sheet
        r=contact_sheet([self.image('a.png'),self.image('b.png')],str(self.root/'sheet.png'))
        self.assertEqual(len(r['mapping']),2);self.assertTrue((self.root/'sheet.png').exists())
    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow unavailable')
    def test_crop_coords(self):
        from workbench.images import crop_image
        r=crop_image(self.image('a.png'),[5,6,25,26],str(self.root/'crop.png'))
        self.assertEqual(r['box_xyxy_half_open'],[5,6,25,26])
    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow unavailable')
    def test_crop_rejects_bounds(self):
        from workbench.images import crop_image
        with self.assertRaises(ValueError):crop_image(self.image('a.png'),[0,0,100,100],str(self.root/'out.png'))
    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow unavailable')
    def test_diff_identical(self):
        from workbench.images import difference
        a=self.image('a.png');r=difference(a,a,str(self.root/'mask.png'))
        self.assertEqual(r['changed_pixel_count'],0)
    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow unavailable')
    def test_diff_size_mismatch(self):
        from workbench.images import difference
        with self.assertRaises(ValueError):difference(self.image('a.png'),self.image('b.png',(32,32)),str(self.root/'mask.png'))
    @unittest.skipUnless(importlib.util.find_spec('PIL'),'Pillow unavailable')
    def test_annotation(self):
        from workbench.images import annotate
        r=annotate(self.image('a.png'),[{'box':[1,2,20,30],'observation':'synthetic'}],str(self.root/'annotated.png'))
        self.assertEqual(len(r['regions']),1)
    @unittest.skipUnless(importlib.util.find_spec('fitz'),'PyMuPDF unavailable')
    def test_pdf_text_and_empty_page(self):
        import fitz
        p=self.root/'synthetic.pdf';d=fitz.open();page=d.new_page();page.insert_text((72,72),'Synthetic rule X.');d.new_page();d.save(p);d.close()
        units=extract_units(p);self.assertEqual(len(units),2);self.assertIn('Synthetic',units[0]['text']);self.assertIn('NO_TEXT_LAYER',units[1]['warning'])
    def test_docx_body_only(self):
        p=self.root/'synthetic.docx'
        xml='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Example</w:t></w:r></w:p></w:body></w:document>'
        with zipfile.ZipFile(p,'w') as z:z.writestr('word/document.xml',xml)
        self.assertEqual(extract_units(p)[0]['text'],'Example')

if __name__=='__main__':unittest.main()
