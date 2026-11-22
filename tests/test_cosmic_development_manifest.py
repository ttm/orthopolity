"""Retained source evidence for the numerical development request list."""
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DevelopmentManifestTests(unittest.TestCase):
    def test_manifest_is_bound_to_retained_metadata_and_head_evidence(self):
        config = json.loads((ROOT / 'configs/cosmic-development-2026-11-20.json').read_text())
        self.assertTrue(config['development_only'])
        self.assertFalse(config['validation_target_assigned'])
        for source in config['sources']:
            self.assertEqual(hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest(),
                             source['sha256'], source['path'])
        head = json.loads((ROOT / 'data/cosmic-source-qualification/2026-11-20/'
                          'tng-selected-file-headers/acquisition.json').read_text())
        head_source = ROOT / ('data/cosmic-source-qualification/2026-11-20/'
                              'tng-selected-file-headers/acquisition_source.py')
        self.assertEqual(hashlib.sha256(head_source.read_bytes()).hexdigest(),
                         head['source_sha256'])
        self.assertFalse(head['api_key_forwarded_to_data_host'])
        self.assertFalse(head['redirect_queries_retained'])
        self.assertEqual(len(head['requests']), len(config['files']))
        for item in config['files']:
            record = next(row for row in head['requests'] if row['url'] == item['url'])
            self.assertEqual(record['body_bytes_read'], 0)
            self.assertEqual(record['redirect_path'], item['redirect_path'])
            observed = (int(record['content_length'])
                        if record.get('data_http_status') == 200 else None)
            self.assertEqual(item['observed_head_content_length'], observed)
            if observed is not None:
                self.assertLess(observed, item['byte_cap'])
        self.assertEqual(config['uncompressed_id_payload_bytes'],
                         len(config['outputs']) * config['expected']['num_dm'] * 8)


if __name__ == '__main__':
    unittest.main()
