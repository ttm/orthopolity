"""Acquire/verify the pinned RM8850 archive; audit schema without uptake values."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shlex
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/adsorption/2026-10-13'
RECORD='17604326'
EXTRA={
 'paper.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11571112/fullTextXML',
 'CO2-properties.html':'https://coolprop.org/fluid_properties/fluids/CarbonDioxide.html',
 'CH4-properties.html':'https://coolprop.org/fluid_properties/fluids/Methane.html',
 'cubic-methods.html':'https://idaes-pse.readthedocs.io/en/stable/explanations/components/property_package/general/eos/cubic.html',
}

def encode(value):
 return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()


def aif_schema(path):
 headers={};loops=[];columns=[];rows=0;in_loop=False
 for raw in path.read_text(encoding='utf-8-sig').splitlines():
  line=raw.strip()
  if not line or line.startswith('#'):continue
  if line=='loop_':
   if in_loop:loops.append(dict(columns=columns,n_rows=rows))
   in_loop=True;columns=[];rows=0
  elif line.startswith('_'):
   tokens=shlex.split(line)
   if in_loop and len(tokens)==1:columns.append(tokens[0])
   else:headers[tokens[0]]=' '.join(tokens[1:])
  elif in_loop: rows+=1
 if in_loop:loops.append(dict(columns=columns,n_rows=rows))
 return dict(headers=headers,loops=loops,uptake_values_inspected=False)


def audit():
 rec=json.loads((BASE/'record.json').read_text())
 return dict(record=RECORD,doi=rec['metadata']['doi'],license=rec['metadata']['license'],
  files={p.name:aif_schema(p) for p in sorted(BASE.glob('*.aif'))},
  exposure='Methods and published findings known; AIF header and row-count audit does not inspect numerical uptake responses.')


def verify():
 receipt=json.loads((BASE/'acquisition.json').read_text())
 rec=json.loads((BASE/'record.json').read_text())
 expected={'record.json',*EXTRA,*[e['key'] for e in rec['files']]}
 if str(rec['id'])!=RECORD or not receipt['complete'] or {e['name'] for e in receipt['files']}!=expected:raise ValueError('Incomplete inventory')
 for e in receipt['files']:
  body=(BASE/e['name']).read_bytes()
  if len(body)!=e['bytes'] or hashlib.sha256(body).hexdigest()!=e['sha256']:raise ValueError('Changed source '+e['name'])
 for e in rec['files']:
  body=(BASE/e['key']).read_bytes()
  if e['checksum']!='md5:'+hashlib.md5(body).hexdigest() or e['size']!=len(body):raise ValueError('Publisher checksum mismatch')
 if (BASE/'metadata-audit.json').read_bytes()!=encode(audit()):raise ValueError('Changed schema audit')
 return dict(verified=True,publisher_files=len(rec['files']),source_files=len(expected),response_values_reported=False)


def acquire():
 BASE.mkdir(parents=True,exist_ok=True)
 rp=BASE/'acquisition.json'
 receipt=json.loads(rp.read_text()) if rp.exists() else dict(complete=False,record=RECORD,files=[])
 if receipt['complete']:return verify()
 inventory={e['name']:e for e in receipt['files']}
 ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
 def fetch(item):
  name,url=item;path=BASE/name
  if name in inventory:
   e=inventory[name]
   if hashlib.sha256(path.read_bytes()).hexdigest()!=e['sha256']:raise ValueError('Changed retained source')
   return e
  started=dt.datetime.now(dt.timezone.utc).isoformat()
  req=urllib.request.Request(url,headers={'User-Agent':'OrthopolityResearch/1.0'})
  with urllib.request.urlopen(req,context=ctx,timeout=45) as res:
   body=res.read(4_000_001)
   if len(body)>4_000_000:raise ValueError('Unexpected large source')
   e=dict(name=name,path=path.relative_to(ROOT).as_posix(),requested_url=url,final_url=res.url,
      retrieval_started_utc=started,retrieval_completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
      http_status=res.status,headers=dict(res.headers),bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),tls_certificate_verification=True)
  if path.exists() and path.read_bytes()!=body:raise ValueError('Refusing changed source overwrite')
  path.write_bytes(body);return e
 e=fetch(('record.json',f'https://zenodo.org/api/records/{RECORD}'))
 if 'record.json' not in inventory:receipt['files'].append(e);inventory['record.json']=e
 rp.write_bytes(encode(receipt))
 rec=json.loads((BASE/'record.json').read_text())
 if str(rec['id'])!=RECORD:raise ValueError('Wrong version')
 requests=[(e['key'],e['links']['self']) for e in rec['files']]+list(EXTRA.items())
 with ThreadPoolExecutor(max_workers=3) as pool:
  for e in pool.map(fetch,requests):
   if e['name'] not in inventory:receipt['files'].append(e);inventory[e['name']]=e
   rp.write_bytes(encode(receipt))
 (BASE/'metadata-audit.json').write_bytes(encode(audit()))
 receipt['complete']=True;rp.write_bytes(encode(receipt))
 return verify()


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['acquire','verify'],default='verify');args=p.parse_args()
 print(json.dumps(acquire() if args.stage=='acquire' else verify(),indent=2))
