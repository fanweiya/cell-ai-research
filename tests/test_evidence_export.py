import json
import tempfile
import unittest
from pathlib import Path
from evidence_export import export_evidence


class EvidenceExportTests(unittest.TestCase):
    def test_exact_text_roundtrip_and_content_versioned_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache, out = root / 'cache', root / 'out'
            cache.mkdir()
            text = ('Method. Table 2: 147 patients, no self-intersections.\n' * 110).strip()
            (cache / 'test.txt').write_text(text, encoding='utf-8')
            records = [{'arxiv_id': 'test'}, {'arxiv_id': '../escape'}, {'arxiv_id': 'missing'}]
            manifest = export_evidence(records, cache, out)
            self.assertEqual(list(manifest), ['test'])
            data = json.loads((out / Path(manifest['test']).name).read_text(encoding='utf-8'))
            self.assertEqual(''.join(c['text'] for c in data['chunks']), text)
            self.assertEqual(manifest, export_evidence(records, cache, out))
            versioned = export_evidence([{'arxiv_id': 'testv1'}], cache, out)
            self.assertIn('testv1', versioned)
            (cache / 'test.txt').write_text(text + ' updated', encoding='utf-8')
            self.assertNotEqual(manifest, export_evidence(records, cache, out))

    def test_null_or_numeric_arxiv_id_and_non_utf8_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache, out = root / 'cache', root / 'out'
            cache.mkdir()
            (cache / 'valid.txt').write_text('valid content', encoding='utf-8')
            (cache / 'bad.txt').write_bytes(b'\x80\x81\xff\xfe')
            records = [
                {'arxiv_id': None},
                {'arxiv_id': 12345},
                {'arxiv_id': 'bad'},
                {'arxiv_id': 'valid'}
            ]
            manifest = export_evidence(records, cache, out)
            self.assertEqual(list(manifest), ['valid'])
