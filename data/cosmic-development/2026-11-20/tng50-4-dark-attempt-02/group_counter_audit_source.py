"""Retain observed catalogue counter layout without assigning undocumented meanings."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np
b=Path('data/cosmic-development/2026-11-20/tng50-4-dark-attempt-02')
source=Path(__file__).read_bytes()
r={'kind':'Development schema audit; no scientific acceptance threshold','source_sha256':hashlib.sha256(source).hexdigest(),'outputs':[]}
for output in [97,98,99]:
 rows=[]
 for chunk in range(4):
  p=b/'raw'/f'groupcat-{output}-{chunk}.hdf5'
  with h5py.File(p,'r') as f:
   rows.append({'chunk':chunk,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'groups_this_file':int(f['Header'].attrs['Ngroups_ThisFile']),'sum_group_lengths':int(np.sum(f['Group/GroupLenType'][:,1],dtype=np.int64)),'Nids_ThisFile':int(f['Header'].attrs['Nids_ThisFile']),'Nids_Total':int(f['Header'].attrs['Nids_Total'])})
 r['outputs'].append({'output':output,'chunks':rows,'sum_group_lengths':sum(x['sum_group_lengths'] for x in rows),'sum_Nids_ThisFile':sum(x['Nids_ThisFile'] for x in rows),'all_Nids_Total':sorted(set(x['Nids_Total'] for x in rows))})
r['finding']='Per-chunk Nids_ThisFile differs from the membership sum of groups stored in that groupcat chunk. Their whole-output sums agree exactly with each Nids_Total. The per-chunk header semantics are not assumed.'
for name,data in [('group-counter-audit.json',(json.dumps(r,indent=2)+'\n').encode()),('group_counter_audit_source.py',source)]:
 with (b/name).open('xb') as f:f.write(data)
print('Retained all12 catalogue counter observations and hashes.')
