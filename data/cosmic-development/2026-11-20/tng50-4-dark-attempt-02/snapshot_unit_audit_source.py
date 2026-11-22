"""Check every retained ID chunk's unit factors against the passed bootstrap."""
import hashlib,json
from pathlib import Path
import h5py
b=Path('data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02')
source=Path(__file__).read_bytes()
bootstrap=json.loads((b/'bootstrap-validation.json').read_text())
keys=['UnitLength_in_cm','UnitMass_in_g','UnitVelocity_in_cm_per_s']
with h5py.File(b/'raw/particle_ids-97-0.hdf5','r') as f:
 reference={k:float(f['Header'].attrs[k]) for k in keys}
rows=[]
for output in [97,98,99]:
 for chunk in range(4):
  path=b/'raw'/f'particle_ids-{output}-{chunk}.hdf5'
  with h5py.File(path,'r') as f:units={k:float(f['Header'].attrs[k]) for k in keys}
  rows.append({'output':output,'chunk':chunk,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'units':units,'identical_to_bootstrap':units==reference})
r={'kind':'All-chunk unit consistency audit','source_sha256':hashlib.sha256(source).hexdigest(),'bootstrap_validation_sha256':hashlib.sha256((b/'bootstrap-validation.json').read_bytes()).hexdigest(),'reference':reference,'chunks':rows,'outcome':'passed' if all(x['identical_to_bootstrap'] for x in rows) else 'failed','note':'Exact equality to already verified bootstrap cgs code-unit factors. Documented cosmological h and scale-factor conventions remain separate.'}
for name,data in [('snapshot-unit-audit.json',(json.dumps(r,indent=2)+'\n').encode()),('snapshot_unit_audit_source.py',source)]:
 with (b/name).open('xb') as f:f.write(data)
print(r['outcome'],len(rows),'unit headers')
