"""Read authorized fields from the frozen membrane-exchange archive.

The default calibration stage exposes both independent optical calibrations,
the earlier pair trajectories, and only the later pairs' initial observations.
Later positive-time responses are never converted to numbers or returned unless
``allow_target=True``. The caller must verify its committed forecast seal before
setting that flag; this module does not establish that chronological guarantee.

CSV decoding necessarily reads strings from the ZIP. This gate controls numeric
response access, not encrypted storage. Source-derived concentrations, corrected
absorbances, diffusivities, thicknesses, and unrelated ZIP members are never used.
"""

import csv
from dataclasses import dataclass
import hashlib
import io
import math
from pathlib import Path
import re
from types import MappingProxyType
from zipfile import BadZipFile, ZipFile


ARCHIVE_SHA256 = 'b50871afca499ae8d74873260a35cff5338388d1c4e6d52c4c3b53eace697c07'
CALIBRATION_RUN = '20250505'
TARGET_RUN = '20250603'
CALIBRATION_TIMES = tuple(float(t) for t in range(0, 67, 6))
TARGET_TIMES = (0.0, 4.0, 21.3, 24.0, 27.5, 45.6, 48.0, 69.6)
SAMPLE_MEMBERS = {
    CALIBRATION_RUN: 'Diffusion Testing/Sample Data/20250505_ot2_PES_PEG25_AO_metadata.csv',
    TARGET_RUN: 'Diffusion Testing/Sample Data/20250603_manual_PES_PEG25_AO_metadata.csv',
}
STANDARD_MEMBERS = {
    CALIBRATION_RUN: 'Diffusion Testing/UV_Vis_Calibration_Curves/20250505_ot2_calibration_AO.csv',
    TARGET_RUN: 'Diffusion Testing/UV_Vis_Calibration_Curves/20250603_manual_calibration_AO.csv',
}


@dataclass(frozen=True)
class OpticalStandard:
    """Prepared concentration and raw absorbance of an optical standard."""

    concentration_uM: float
    absorbance: float


@dataclass(frozen=True)
class ChamberDesign:
    time_hours: float
    sample: str
    chamber: str


@dataclass(frozen=True)
class ChamberObservation:
    """Raw absorbance; no blank subtraction or concentration conversion."""

    time_hours: float
    sample: str
    chamber: str
    absorbance: float


@dataclass(frozen=True)
class MembraneSourceData:
    archive_sha256: str
    calibration_standards: tuple[OpticalStandard, ...]
    target_standards: tuple[OpticalStandard, ...]
    calibration_observations: tuple[ChamberObservation, ...]
    target_baselines: tuple[ChamberObservation, ...]
    target_design: tuple[ChamberDesign, ...]
    target_observations: tuple[ChamberObservation, ...] | None

    @property
    def standards_by_run(self):
        """Read-only convenience mapping, keyed by the two source dates."""
        return MappingProxyType({
            CALIBRATION_RUN: self.calibration_standards,
            TARGET_RUN: self.target_standards,
        })


def _number(value, field, member, line):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'Invalid {field} in {member}, line {line}') from None
    if not math.isfinite(result):
        raise ValueError(f'Nonfinite {field} in {member}, line {line}')
    return result


def _rows(archive, member, required):
    """Yield rows as strings, checking structure without parsing other fields."""
    try:
        with archive.open(member) as binary:
            with io.TextIOWrapper(binary, encoding='utf-8-sig', newline='') as stream:
                reader = csv.DictReader(stream, strict=True)
                header = reader.fieldnames
                if (not header or len(header) != len(set(header))
                        or not set(required).issubset(header)):
                    raise ValueError(f'Invalid CSV schema in {member}')
                for row in reader:
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError(f'Malformed CSV row in {member}, line {reader.line_num}')
                    yield row, reader.line_num
    except (UnicodeError, csv.Error) as error:
        raise ValueError(f'Invalid CSV encoding or structure in {member}') from error


def _standards(archive, member):
    result = []
    seen = set()
    for row, line in _rows(archive, member, ('C_uM', 'Abs_raw')):
        concentration = _number(row['C_uM'], 'C_uM', member, line)
        if concentration < 0 or concentration in seen:
            raise ValueError(f'Negative or duplicate standard concentration in {member}')
        seen.add(concentration)
        result.append(OpticalStandard(
            concentration, _number(row['Abs_raw'], 'Abs_raw', member, line)))
    if len(result) != 5:
        raise ValueError(f'Expected five optical standards in {member}')
    return tuple(sorted(result, key=lambda row: row.concentration_uM))


def _design_key(row):
    # Sample suffixes are validated against the fixed identities before sorting.
    return (int(row.sample.rsplit('_S', 1)[1]), row.chamber, row.time_hours)


def _samples(archive, run, allow_target):
    member = SAMPLE_MEMBERS[run]
    times = CALIBRATION_TIMES if run == CALIBRATION_RUN else TARGET_TIMES
    first_sample = 1 if run == CALIBRATION_RUN else 5
    expected = {
        ChamberDesign(t, f'PES_PEG25_AO_S{first_sample + h - 1}', f'H{h}_C{c}')
        for h in range(1, 5) for c in (1, 2) for t in times
    }
    seen = set()
    observations = []
    for row, line in _rows(archive, member, ('Time', 'Hcell', 'Sample', 'Abs_raw')):
        design = ChamberDesign(
            _number(row['Time'], 'Time', member, line), row['Sample'], row['Hcell'])
        if design not in expected:
            raise ValueError(f'Unexpected time or sample/chamber identity in {member}, line {line}')
        if design in seen:
            raise ValueError(f'Duplicate design row in {member}, line {line}')
        seen.add(design)
        # Keep this branch above every conversion/access of the response field.
        if run == CALIBRATION_RUN or design.time_hours == 0 or allow_target:
            observations.append(ChamberObservation(
                design.time_hours, design.sample, design.chamber,
                _number(row['Abs_raw'], 'Abs_raw', member, line)))
    if seen != expected:
        raise ValueError(f'Missing design rows in {member}')
    return tuple(sorted(seen, key=_design_key)), tuple(sorted(observations, key=_design_key))


def read_membrane_archive(path, *, allow_target=False, expected_sha256=ARCHIVE_SHA256):
    """Return the staged, validated source data from a local ZIP.

    ``allow_target`` must be a literal bool. Its default leaves the 56 later
    positive-time absorbances unparsed and sets ``target_observations=None``.
    Evaluation adds those 56 observations; all other outputs are unchanged.
    Target design includes all 64 baseline/later identities in both stages.

    The frozen SHA-256 is checked before opening the ZIP or reading any member.
    An explicit alternate digest is supported for synthetic fixtures, not as a
    hash-check bypass: it must be a 64-digit hexadecimal SHA-256 matching the
    entire supplied archive. No argument disables verification. Dataclasses can
    be serialized with ``dataclasses.asdict``. Numeric fields remain raw and
    finite; negative absorbances are preserved rather than clipped.
    """
    if type(allow_target) is not bool:
        raise ValueError('allow_target must be explicitly True or False')
    if not isinstance(expected_sha256, str) or re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha256) is None:
        raise ValueError('Expected SHA-256 must be a 64-digit hexadecimal string')
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256.lower():
        raise ValueError('Membrane archive SHA-256 mismatch')
    try:
        with ZipFile(io.BytesIO(raw)) as archive:
            names = archive.namelist()
            for member in (*SAMPLE_MEMBERS.values(), *STANDARD_MEMBERS.values()):
                if names.count(member) != 1:
                    raise ValueError(f'Missing or duplicated ZIP member: {member}')
            calibration_standards = _standards(archive, STANDARD_MEMBERS[CALIBRATION_RUN])
            target_standards = _standards(archive, STANDARD_MEMBERS[TARGET_RUN])
            _, calibration = _samples(archive, CALIBRATION_RUN, allow_target=False)
            target_design, target = _samples(archive, TARGET_RUN, allow_target=allow_target)
    except BadZipFile as error:
        raise ValueError('Invalid membrane ZIP archive') from error
    return MembraneSourceData(
        archive_sha256=digest,
        calibration_standards=calibration_standards,
        target_standards=target_standards,
        calibration_observations=calibration,
        target_baselines=tuple(row for row in target if row.time_hours == 0),
        target_design=target_design,
        target_observations=(tuple(row for row in target if row.time_hours > 0)
                             if allow_target else None),
    )
