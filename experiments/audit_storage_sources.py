"""Verify retained candidate archives and reproduce schemas, without outcomes."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

from numpy.lib.format import read_magic, read_array_header_1_0


def main():
    root = Path(__file__).resolve().parents[1] / 'data/physics-candidates/2026-10-25/storage'
    receipt = json.loads((root / 'acquisition.json').read_text())
    for record in receipt['files']:
        path = root / record['file']
        if path.parent != root:
            raise ValueError('Expected a source basename')
        data = path.read_bytes()
        assert len(data) == record['bytes']
        assert hashlib.sha256(data).hexdigest() == record['sha256']
        if 'md5' in record:
            assert hashlib.md5(data).hexdigest() == record['md5']

    hotbox = []
    with zipfile.ZipFile(root / 'hotbox-dataset.zip') as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            with archive.open(member) as raw:
                rows = csv.reader(io.TextIOWrapper(raw), delimiter='\t')
                header = next(rows)
                assert header[0] == 'Time'
                assert all(any(c.isalpha() for c in h) for h in header)
                count, widths = 0, set()
                # Cell tokens are never converted to numbers or reported.
                for row in rows:
                    count += 1
                    widths.add(len(row))
            hotbox.append(dict(name=member.filename, n_rows=count,
                               n_columns=len(header), row_widths=sorted(widths), header=header))
    assert hotbox == json.loads((root / 'hotbox-inventory.json').read_text())

    electrical = []
    with tarfile.open(root / 'topological-data_codes.tar.xz') as archive:
        for member in archive.getmembers():
            if not (member.name.startswith('data_codes/data_exp/') and member.name.endswith('.npy')):
                continue
            with archive.extractfile(member) as raw:
                assert read_magic(raw) == (1, 0)
                shape, fortran, dtype = read_array_header_1_0(raw)
                # Do not read the array payload, even when string-encoded.
            electrical.append(dict(file=member.name, shape=list(shape), dtype=str(dtype), fortran=fortran))
    assert electrical == json.loads((root / 'topological-inventory.json').read_text())
    print(json.dumps(dict(verified_retained_files=len(receipt['files']),
                          thermal_tables=len(hotbox), electrical_array_headers=len(electrical),
                          numerical_experimental_values_converted_or_reported=False), indent=2))


if __name__ == '__main__':
    main()
