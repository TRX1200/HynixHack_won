import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('verify_release_v2',ROOT/'tools/verify_release.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DistributionTests(unittest.TestCase):
    def test_source_and_archive_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'a.txt').write_bytes(b'source')
            data={'files':[{'path':'a.txt','bytes':6,'sha256':hashlib.sha256(b'source').hexdigest()}]}
            (root/'RELEASE_MANIFEST.json').write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(mod.verify(root),[])
            (root/'toolkit-source.zip').write_bytes(b'archive')
            (root/'CHECKSUMS.sha256').write_text(hashlib.sha256(b'archive').hexdigest()+'  toolkit-source.zip\n',encoding='utf-8')
            self.assertEqual(mod.verify(root),[])
            (root/'toolkit-source.zip').write_bytes(b'tampered')
            self.assertTrue(any('checksum' in error for error in mod.verify(root)))
            (root/'a.txt').write_bytes(b'changed')
            self.assertTrue(any('Changed file' in error for error in mod.verify(root)))

    def test_unexpected_private_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'RELEASE_MANIFEST.json').write_text('{"files":[]}',encoding='utf-8')
            (root/'unlisted.txt').write_text('local output',encoding='utf-8')
            self.assertIn('Unexpected file (do not publish): unlisted.txt',mod.verify(root))


if __name__=='__main__':unittest.main()
