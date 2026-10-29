"""Replay the bounded fragmentation source audit without numeric outcome decoding."""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import zipfile

from audit_optical_allocation_schema import inspect_workbook


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/fragmentation-candidates/2026-10-28'


def main():
    receipt = json.loads((DATA / 'source-receipt.json').read_text())
    for record in receipt['files']:
        path = DATA / record['file']
        if not path.resolve().is_relative_to(DATA.resolve()):
            raise ValueError('Source path escapes audit directory')
        raw = path.read_bytes()
        if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Source bytes changed: ' + record['file'])

    # Provider checksums are verified only for files downloaded in full.
    for folder, metadata_name, names in [
        ('lin', 'record-v2.json', ['Dataset_S1.xlsx']),
        ('rae', 'metadata.json', ['ST1_QSexp.xlsx', 'ST2_Dynexp.xlsx']),
    ]:
        metadata = json.loads((DATA / folder / metadata_name).read_text())
        by_name = {item['key']: item for item in metadata['files']}
        for name in names:
            digest = hashlib.md5((DATA / folder / name).read_bytes()).hexdigest()
            if by_name[name]['checksum'] != 'md5:' + digest:
                raise ValueError('Publisher checksum mismatch: ' + name)

    metadata = json.loads((DATA / 'deepsea/figshare-25102847.json').read_text())
    readme = next(item for item in metadata['files'] if item['name'] == 'README.zip')
    if hashlib.md5((DATA / 'deepsea/README.zip').read_bytes()).hexdigest() != readme['computed_md5']:
        raise ValueError('README publisher checksum mismatch')

    # The tail contains the complete ZIP directory and this final small member.
    # zipfile checks the member CRC. The full archive MD5 remains unverified.
    with zipfile.ZipFile(BytesIO((DATA / 'deepsea/zip-tail.bin').read_bytes())) as archive:
        member = archive.read('Sieving and Measuring/Sieving.xlsx')
        if member != (DATA / 'deepsea/Sieving.xlsx').read_bytes():
            raise ValueError('Extracted sieve workbook changed')
        archive_members = len(archive.infolist())

    schemas = json.loads((DATA / 'workbook-schemas.json').read_text())
    for expected in schemas:
        actual = inspect_workbook(DATA / expected['file'])
        actual['file'] = expected['file']
        if actual != expected:
            raise ValueError('Workbook schema changed: ' + expected['file'])
    print(json.dumps(dict(
        archive_families=receipt['archive_families'],
        verified_retained_files=len(receipt['files']),
        verified_publisher_checksums=4,
        verified_workbooks=len(schemas),
        verified_sheets=sum(len(s['sheets']) for s in schemas),
        deepsea_archive_directory_members=archive_members,
        full_deepsea_archive_hash_verified=False,
        numerical_experimental_outcomes_decoded=False,
    ), indent=2))


if __name__ == '__main__':
    main()
