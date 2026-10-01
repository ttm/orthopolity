"""Immutable registration, prospective lineage, and metadata privacy checks."""
import copy
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from orthopolity.run_registry import (
    archive_reference, collect_hardware_metadata, file_reference, hash_file, register_run, verify_registry,
    _hardware_details, _runtime_threads,
)


class RunRegistryChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name, text in [('source.py', 'source version one\n'),
                           ('config.json', '{"seed": 17}\n'),
                           ('result.json', '{"completed": true}\n')]:
            (self.root / name).write_text(text)
        self.entry = dict(schema_version=1, run_id='baseline', evidence_kind='actual_measurement',
            resources=[dict(name='CPU', definition='Measured user plus system task CPU', units='seconds')],
            data_inputs=[], generated_seeds=dict(workload=17),
            algorithms=[dict(name='actual computation', sources=[file_reference(self.root, 'source.py')])],
            configs=[file_reference(self.root, 'config.json')],
            artifacts=[file_reference(self.root, 'result.json')], relationships=[],
            hardware_metadata=dict(recording_scope='test fixture'),
            summary=dict(completed=True))

    def registry_bytes(self):
        return (self.root / 'results/run-registry.jsonl').read_bytes()

    def test_repeat_is_idempotent_and_preserves_exact_registry_bytes(self):
        first = register_run(self.root, self.entry)
        before = self.registry_bytes()
        # Dictionary insertion order is not a change to the scientific entry.
        repeat = register_run(self.root, dict(reversed(list(self.entry.items()))))
        self.assertTrue(first['appended']); self.assertFalse(repeat['appended'])
        self.assertEqual(first['entry_sha256'], repeat['entry_sha256'])
        self.assertEqual(before, self.registry_bytes())
        audit = verify_registry(self.root)
        self.assertEqual(audit['run_ids'], ['baseline']); self.assertEqual(audit['file_references'], 3)

    def test_changed_summary_with_same_id_is_rejected_without_rewriting(self):
        register_run(self.root, self.entry); before = self.registry_bytes()
        changed = copy.deepcopy(self.entry); changed['summary']['completed'] = False
        with self.assertRaisesRegex(ValueError, 'Conflicting immutable run_id'):
            register_run(self.root, changed)
        self.assertEqual(before, self.registry_bytes())

    def test_altered_recorded_file_blocks_repeat_and_new_run(self):
        register_run(self.root, self.entry); before = self.registry_bytes()
        (self.root / 'result.json').write_text('{"completed": false}\n')
        for entry in (self.entry, dict(self.entry, run_id='new')):
            with self.assertRaisesRegex(ValueError, 'Changed registered file'):
                register_run(self.root, entry)
        with self.assertRaisesRegex(ValueError, 'Changed registered file'):
            verify_registry(self.root)
        self.assertEqual(before, self.registry_bytes())

    def test_lineage_requires_existing_parent_and_survives_hash_audit(self):
        child = copy.deepcopy(self.entry); child['run_id'] = 'replication'
        child['relationships'] = [dict(run_id='baseline', type='transfer_replication')]
        with self.assertRaisesRegex(ValueError, 'must already be registered'):
            register_run(self.root, child)
        register_run(self.root, self.entry); baseline = self.registry_bytes()
        register_run(self.root, child)
        self.assertTrue(self.registry_bytes().startswith(baseline))
        self.assertEqual(verify_registry(self.root)['run_ids'], ['baseline', 'replication'])
        child['run_id'] = 'self'; child['relationships'][0]['run_id'] = 'self'
        with self.assertRaises(ValueError): register_run(self.root, child)

    def test_unsafe_paths_and_digest_mismatch_are_rejected(self):
        for unsafe in ('../outside', '/etc/passwd', 'a/../source.py', './source.py', 'a\\source.py'):
            with self.assertRaises(ValueError): hash_file(self.root, unsafe)
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'private'; target.write_text('unregistered external data')
            (self.root / 'escaped').symlink_to(target)
            with self.assertRaises(ValueError): hash_file(self.root, 'escaped')
        changed = copy.deepcopy(self.entry); changed['artifacts'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Changed registered file'): register_run(self.root, changed)
        nonfinite = copy.deepcopy(self.entry); nonfinite['summary']['error'] = float('nan')
        with self.assertRaises(ValueError): register_run(self.root, nonfinite)

    def test_modified_registry_payload_and_partial_line_are_not_accepted(self):
        register_run(self.root, self.entry)
        path = self.root / 'results/run-registry.jsonl'; original = path.read_text()
        payload = json.loads(original); payload['summary']['completed'] = False
        path.write_text(json.dumps(payload) + '\n')
        with self.assertRaisesRegex(ValueError, 'entry digest'): verify_registry(self.root)
        path.write_text(original.rstrip('\n'))
        with self.assertRaisesRegex(ValueError, 'incomplete'): register_run(self.root, self.entry)

    def test_source_archive_allows_new_version_without_changing_previous_run(self):
        first = archive_reference(self.root, 'source.py')
        self.assertEqual(first, archive_reference(self.root, 'source.py'))
        self.entry['algorithms'][0]['sources'] = [first]
        self.entry['configs'] = [archive_reference(self.root, 'config.json')]
        register_run(self.root, self.entry); before = self.registry_bytes()
        (self.root / 'source.py').write_text('source version two\n')
        (self.root / 'config.json').write_text('{"seed": 19}\n')
        self.assertTrue(verify_registry(self.root)['valid'])
        second = copy.deepcopy(self.entry); second['run_id'] = 'version-two'
        second['algorithms'][0]['sources'] = [archive_reference(self.root, 'source.py')]
        second['configs'] = [archive_reference(self.root, 'config.json')]
        second['relationships'] = [dict(type='algorithm_revision', run_id='baseline')]
        register_run(self.root, second)
        self.assertTrue(self.registry_bytes().startswith(before))
        self.assertNotEqual(first['path'], second['algorithms'][0]['sources'][0]['path'])
        self.assertEqual((self.root / first['path']).read_text(), 'source version one\n')

    def test_corrupted_source_archive_is_detected_and_never_overwritten(self):
        reference = archive_reference(self.root, 'source.py')
        archived = self.root / reference['path']; archived.write_text('tampered archive\n')
        with self.assertRaisesRegex(ValueError, 'Conflicting immutable source archive'):
            archive_reference(self.root, 'source.py')
        self.assertEqual(archived.read_text(), 'tampered archive\n')

    def test_darwin_collector_uses_only_explicit_nonidentifying_sysctl_keys(self):
        values = {'machdep.cpu.brand_string':'Apple test CPU', 'hw.memsize':'17179869184',
                  'kern.osversion':'test-build'}
        calls = []
        def sysctl(key): calls.append(key); return values[key]
        with patch('orthopolity.run_registry._sysctl', side_effect=sysctl), \
             patch('orthopolity.run_registry.platform.node', side_effect=AssertionError('hostname forbidden')):
            details = _hardware_details('Darwin')
        self.assertEqual(set(calls), set(values))
        self.assertEqual(details['total_ram_bytes'], 16 * 1024**3)
        self.assertEqual(details['cpu_model'], 'Apple test CPU')

    def test_linux_collector_does_not_copy_serial_or_machine_identifiers(self):
        def read(path, *args, **kwargs):
            if path.name == 'cpuinfo':
                return 'Serial: SECRET_SERIAL\nmodel name: Generic CPU\n'
            if path.name == 'meminfo': return 'MemTotal: 1024 kB\n'
            raise AssertionError('unexpected broad hardware read')
        with patch.object(Path, 'read_text', read): details = _hardware_details('Linux')
        self.assertEqual(details['total_ram_bytes'], 1024**2)
        self.assertNotIn('SECRET_SERIAL', json.dumps(details))

    def test_requested_environment_is_not_accelerate_runtime_verification(self):
        fake = types.ModuleType('threadpoolctl')
        fake.threadpool_info = lambda: [dict(user_api='openmp', internal_api='openmp',
            num_threads=1, filepath='/Users/SECRET_USER/local/library.dylib')]
        with patch.dict('sys.modules', {'threadpoolctl':fake}): runtime = _runtime_threads('accelerate')
        self.assertTrue(runtime['inspection_available'])
        self.assertFalse(runtime['thread_count_verified']); self.assertFalse(runtime['verified_single_thread'])
        self.assertNotIn('SECRET_USER', json.dumps(runtime))
        with patch('orthopolity.run_registry._hardware_details', return_value=dict(
                cpu_model='Generic CPU', total_ram_bytes=1024, os_build='build')), \
             patch('orthopolity.run_registry._numpy_metadata', return_value=dict(
                available=True, version='2', blas=dict(name='accelerate', version=None))), \
             patch('orthopolity.run_registry._runtime_threads', return_value=runtime), \
             patch('orthopolity.run_registry.platform.node', side_effect=AssertionError('hostname forbidden')):
            metadata = collect_hardware_metadata({'VECLIB_MAXIMUM_THREADS':'1'})
        self.assertEqual(metadata['requested_thread_environment'], {'VECLIB_MAXIMUM_THREADS':'1'})
        self.assertFalse(metadata['runtime_thread_verification']['thread_count_verified'])
        self.assertFalse(any(key in json.dumps(metadata).lower() for key in ('hostname', 'serial_number', 'username')))
        json.dumps(metadata, allow_nan=False)


if __name__ == '__main__': unittest.main()
