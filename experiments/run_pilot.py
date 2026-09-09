"""Reproduce the exploratory analyses from frozen source files."""
from pathlib import Path
import sys,json,hashlib,platform,wave
import numpy as np
import pandas as pd
import scipy
from scipy.stats import linregress
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from orthopolity import resource_spectrum,bounded_power_mle,mean_resource_exponent,rounded_gr_b,residual_audio

RAW=ROOT/'data'/'raw'; OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
SPEC=json.loads((ROOT/'configs'/'pilot.json').read_text())
RNG=np.random.default_rng(SPEC['seed']);B=SPEC['bootstrap_replicates']

def interval(x):
    x=np.asarray(x,float);x=x[np.isfinite(x)]
    return list(np.quantile(x,[.025,.975])) if len(x) else [None,None]

def frame(s):
    return pd.DataFrame({k:v for k,v in s.items() if isinstance(v,np.ndarray)})

def resample_blocks(df,col):
    blocks=[g for _,g in df.groupby(col,sort=True)]
    return pd.concat([blocks[i] for i in RNG.integers(len(blocks),size=len(blocks))],ignore_index=True)

def slope_of(s):
    # Empty bins stay in the exported spectrum; the slope is unavailable if any
    # are empty. Never silently drop them to improve a fit.
    if np.any(s['phi']<=0):return np.nan
    return float(linregress(np.log(s['center']),np.log(s['phi'])).slope)

def solar():
    a=pd.concat([pd.read_csv(RAW/f'noaa_{y}.csv').assign(year=y) for y in [2022,2023,2024]],ignore_index=True)
    if a.flare_id.duplicated().any():raise ValueError('Duplicate flare identifiers')
    a['month']=pd.to_datetime(a.time).dt.strftime('%Y-%m')
    a['duration_s']=(pd.to_datetime(a.end_time)-pd.to_datetime(a.start_time)).dt.total_seconds()
    a['k']=a.xrsb_irrad
    ok=np.isfinite(a.k)&(a.k>0)&(a.peak_saturated==0)
    a=a[ok].copy()
    summary={'catalog_n':len(a),'end_fluence_missing_n':int(a.integrated_irrad_end.isna().sum()),'cases':[]}
    sens=[]
    for resource in ['integrated_irrad_end','integrated_irrad_peak']:
        a['q']=a[resource]
        valid=np.isfinite(a.q)&(a.q>0)
        if resource=='integrated_irrad_end':valid &= a.duration_s>0
        for lo in [1e-6,5e-6,1e-5,3e-5]:
            hi=1e-3
            selected=a[(a.k>=lo)&(a.k<=hi)].copy()
            pair=a[valid&(a.k>=lo)&(a.k<=hi)].copy()
            train=pair[pair.year==2022];ev=pair[pair.year>=2023]
            d,A=mean_resource_exponent(train.k,train.q,reference=lo)
            alpha=bounded_power_mle(ev.k,lo,hi)
            bins=int(np.ceil(np.log10(hi/lo)*4))
            edges=np.geomspace(lo,hi,bins+1)
            s=resource_spectrum(ev.k,ev.q,edges)
            rec=dict(resource=resource,lo=lo,hi=hi,selected_n=len(selected),paired_n=len(pair),train_n=len(train),evaluation_n=len(ev),missing_fraction=1-len(pair)/len(selected),d_train=d,alpha_predicted=d+1,alpha_evaluation=alpha,gap=alpha-d-1,spectrum_slope=slope_of(s),phi_min=float(s['phi'].min()),phi_max=float(s['phi'].max()))
            if lo==1e-5:
                draws=[];phis=[]
                for _ in range(B):
                    tr=resample_blocks(train,'month');te=resample_blocks(ev,'month')
                    bd,_=mean_resource_exponent(tr.k,tr.q,reference=lo)
                    ba=bounded_power_mle(te.k,lo,hi)
                    bs=resource_spectrum(te.k,te.q,edges)
                    draws.append([bd,ba,ba-bd-1,slope_of(bs)])
                    phis.append(bs['phi'])
                draws=np.asarray(draws);phis=np.asarray(phis)
                rec.update(d_train_ci=interval(draws[:,0]),alpha_evaluation_ci=interval(draws[:,1]),gap_ci=interval(draws[:,2]),spectrum_slope_ci=interval(draws[:,3]),bootstrap_B=B,valid_slope_bootstraps=int(np.isfinite(draws[:,3]).sum()))
                f=frame(s);f['phi_ci_low'],f['phi_ci_high']=np.quantile(phis,[.025,.975],axis=0)
                ev_all=selected[selected.year>=2023]
                f['all_event_count']=np.histogram(ev_all.k,bins=edges)[0]
                f['missing_resource_count']=f.all_event_count-f['count']
                short='end' if resource.endswith('end') else 'rise'
                f.to_csv(OUT/f'noaa_{short}_spectrum.csv',index=False)
                pd.DataFrame(draws,columns=['d_train','alpha_evaluation','gap','spectrum_slope']).to_csv(OUT/f'noaa_{short}_bootstrap.csv',index=False)
                if short=='end':
                    pair[['flare_id','year','month','k','q','duration_s']].to_csv(OUT/'noaa_pairs.csv',index=False)
                    plot_solar(train,ev,f,d,A,lo,hi)
            sens.append(rec);summary['cases'].append(rec)
    pd.DataFrame(sens).to_csv(OUT/'noaa_sensitivity.csv',index=False)
    return summary

def plot_solar(train,ev,f,d,A,lo,hi):
    fig,axs=plt.subplots(2,2,figsize=(10,7.4),layout='constrained')
    x=np.geomspace(lo,hi,100)
    ax=axs[0,0];ax.scatter(train.k,train.q,s=5,alpha=.3,color='#4b5563',rasterized=True)
    ax.plot(x,A*(x/lo)**d,color='black',label=f'Arithmetic mean model: d = {d:.2f}')
    ax.set(xscale='log',yscale='log',xlabel='Peak irradiance (W/m²)',ylabel='End fluence (J/m²)',title='2022: resource scaling');ax.legend(fontsize=8)
    ax=axs[0,1];k=np.sort(ev.k.to_numpy());ax.step(k,np.arange(len(k),0,-1)/len(k),where='post',color='black')
    # Predicted conditional CCDF on the same bounded domain.
    t=d;pred=((x/lo)**(-t)-(hi/lo)**(-t))/(1-(hi/lo)**(-t)) if abs(t)>1e-7 else np.log(hi/x)/np.log(hi/lo)
    ax.plot(x,pred,'--',color='#627c90',label='Exponent predicted from 2022 resource fit')
    ax.set(xscale='log',yscale='log',xlabel='Peak irradiance (W/m²)',ylabel='Fraction at or above peak',title='2023–2024: observed abundance');ax.legend(fontsize=8)
    ax=axs[1,0];ax.axhline(1,color='#777',ls='--');ax.plot(f.center,f.phi,'o-',color='black')
    ax.fill_between(f.center,f.phi_ci_low,f.phi_ci_high,alpha=.2,color='#627c90')
    ax.set(xscale='log',xlabel='Peak irradiance (W/m²)',ylabel='Normalized resource per log interval',title='2023–2024: resource occupancy')
    ax=axs[1,1];ax.bar(np.arange(len(f)),f.missing_resource_count/f.all_event_count,color='#777')
    ax.set(xticks=np.arange(len(f)),xticklabels=[f'{z:.1e}' for z in f.center],ylabel='Fraction missing end fluence',title='Missingness in the evaluation sample')
    ax.tick_params(axis='x',labelrotation=45);ax.set_xlabel('Peak irradiance bin center (W/m²)')
    for ax in axs.flat:ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'noaa_pilot.png',dpi=180);plt.close(fig)

def earthquakes():
    a=pd.read_csv(RAW/'usgs_2010_2024.csv')
    a['date']=pd.to_datetime(a.time,utc=True)
    a=a[a.date<pd.Timestamp('2025-01-01',tz='UTC')].copy()
    nraw=len(a);a=a[a.magType.str.startswith('mw',na=False)].copy();a['year']=a.date.dt.year
    records=[]
    for cutoff in [5.5,6.,6.5]:
        b,n=rounded_gr_b(a.mag,cutoff)
        draws=[rounded_gr_b(resample_blocks(a,'year').mag,cutoff)[0] for _ in range(B)]
        ci=interval(draws)
        records.append(dict(cutoff=cutoff,n=n,b=b,b_ci=ci,energy_proxy_slope=1-b/1.5,energy_proxy_slope_ci=[1-ci[1]/1.5,1-ci[0]/1.5],predicted_equal_resource_b=1.5))
    a['energy_proxy_J']=10**(4.8+1.5*a.mag)
    # Display rounding bins by using half-step outer boundaries.
    mag_edges=np.array([5.45,5.95,6.45,6.95,7.45,7.95,8.45,8.95,9.45])
    s=resource_spectrum(a.energy_proxy_J,a.energy_proxy_J,10**(4.8+1.5*mag_edges))
    f=frame(s);f['magnitude_center']=(mag_edges[1:]+mag_edges[:-1])/2
    f.to_csv(OUT/'usgs_spectrum.csv',index=False)
    a[['id','year','mag','magType','energy_proxy_J']].to_csv(OUT/'usgs_selected.csv',index=False)
    fig,axs=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    m=np.sort(a.mag);axs[0].step(m,np.arange(len(m),0,-1)/len(m),where='post',color='black',label='Observed Mw catalog')
    x=np.linspace(5.5,9.1,100)
    axs[0].plot(x,10**(-records[0]['b']*(x-5.5)),color='#627c90',label=f"GR fit b = {records[0]['b']:.2f}")
    axs[0].plot(x,10**(-1.5*(x-5.5)),'--',color='#999',label='Equal-energy prediction b = 1.5')
    axs[0].set(yscale='log',xlabel='Moment magnitude',ylabel='Fraction at or above magnitude',title='USGS earthquakes, 2010–2024');axs[0].legend(fontsize=8)
    axs[1].plot(f.magnitude_center,f.phi,'o-',color='black');axs[1].axhline(1,ls='--',color='#999')
    axs[1].set(xlabel='Moment-magnitude bin center',ylabel='Normalized proxy energy per log interval',title='Estimated energy occupancy')
    for ax in axs:ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'usgs_pilot.png',dpi=180);plt.close(fig)
    return dict(catalog_n=nraw,mw_n=len(a),rounded_to_step=.1,cases=records,energy_is_proxy=True)

def ocean():
    a=pd.read_csv(RAW/'sheldon_summary_biomass_top200_table_long.csv')
    f=a.groupby('log10_Size_Midpoint_g',as_index=False)['Biomass_Pg_wet_weight_estimate'].sum()
    f.columns=['log10_mass_g','biomass_Pg']
    f['phi']=f.biomass_Pg/f.biomass_Pg.mean()
    f['log10_abundance_proxy']=np.log10(f.biomass_Pg*1e15)-f.log10_mass_g
    # Published reconstruction. Bin-midpoint conversion is approximate and
    # cannot recreate individual-organism observations.
    slope=float(linregress(f.log10_mass_g,f.log10_abundance_proxy).slope)
    f.to_csv(OUT/'ocean_reexpression.csv',index=False)
    fig,ax=plt.subplots(figsize=(10,3.2),layout='constrained')
    ax.plot(f.log10_mass_g,f.phi,'o-',color='black');ax.axhline(1,ls='--',color='#777')
    ax.set(xlabel='Log10 body-mass bin midpoint (g)',ylabel='Biomass / mean biomass per decade',title='Published ocean reconstruction: equal biomass is approximate')
    ax.spines[['top','right']].set_visible(False);fig.savefig(OUT/'ocean_reexpression.png',dpi=180);plt.close(fig)
    return dict(bins=len(f),slope_abundance=slope,slope_biomass=slope+1,phi_min=float(f.phi.min()),phi_max=float(f.phi.max()),source_kind='Published model-assisted reconstruction; not new observations')

def main():
    plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','axes.titleweight':'normal'})
    results={'protocol':SPEC,'noaa':solar(),'usgs':earthquakes(),'ocean':ocean(),
             'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__}}
    (OUT/'results.json').write_text(json.dumps(results,indent=2))
    files=[]
    for p in sorted(RAW.iterdir()):
        if p.is_file():files.append(dict(file=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'checksums.json').write_text(json.dumps(files,indent=2))
    s=pd.read_csv(OUT/'noaa_end_spectrum.csv')
    audio=residual_audio(s.phi)
    with wave.open(str(OUT/'noaa_residual_sonification.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes((audio*32767).astype('<i2').tobytes())
    print(json.dumps({'noaa_primary':[r for r in results['noaa']['cases'] if r['lo']==1e-5],'usgs':results['usgs'],'ocean':results['ocean']},indent=2))

if __name__=='__main__':main()
