"""Retrieve sources and verify them against the delivered snapshot checksums.

Existing matching files are reused. Changed remote data are downloaded to a
.changed file and cause failure; they never silently replace the frozen data.
"""
from pathlib import Path
import urllib.request,json,hashlib

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw';RAW.mkdir(parents=True,exist_ok=True)
base='https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/multi/l2/data/xrsf-l2-flrpt_science/csv/'
sha='d8af6567faf1912862650423e392e1b3195a8732'
shel=f'https://raw.githubusercontent.com/ryanheneghan/sheldon_revisited/{sha}/output/summary_output/summary_tables/'
glo='https://raw.githubusercontent.com/zeynepersoy/GLOSSAQUA_dataset/HEAD/data/'
URLS={**{f'noaa_{y}.csv':base+f'sci_xrsf-l2-flrpt_geo_y{y}_v1-0-1.csv' for y in (2022,2023,2024)},
 'noaa_metadata.json':base+'sci_xrsf-l2-flrpt_geo_metadata.json',
 'usgs_2010_2024.csv':'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2010-01-01&endtime=2025-01-01&minmagnitude=5.5&eventtype=earthquake&orderby=time-asc',
 'sheldon_summary_biomass_top200_table_long.csv':shel+'summary_biomass_top200_table_long.csv',
 'sheldon_summary_biomass_allwater_table_long.csv':shel+'summary_biomass_table_long.csv',
 'sheldon_group_standard_errors.csv':shel+'group_standard_errors.csv',
 **{f'GLOSSAQUA_{n}.txt':glo+f'GLOSSAQUA_{n}.txt' for n in ('Size','Sample','DataSource')}}
# GLOSSAQUA is pinned to HEAD rather than a commit: the upstream repository
# publishes no tags. The checksums below freeze the snapshot regardless, and a
# changed remote file raises rather than replacing it.

if __name__=='__main__':
    expected={r['file']:r['sha256'] for r in json.loads((ROOT/'data'/'snapshot_checksums.json').read_text())}
    for name,url in URLS.items():
        path=RAW/name
        if path.exists():
            b=path.read_bytes()
            if hashlib.sha256(b).hexdigest()!=expected[name]:raise RuntimeError(f'Local snapshot modified: {name}')
            print(f'Verified {name}');continue
        b=urllib.request.urlopen(url,timeout=45).read()
        if hashlib.sha256(b).hexdigest()!=expected[name]:
            path.with_suffix(path.suffix+'.changed').write_bytes(b)
            raise RuntimeError(f'Remote source changed: {name}. Restore the delivered snapshot or explicitly create a new analysis version.')
        path.write_bytes(b);print(f'Restored {name}')
