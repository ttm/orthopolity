"""Local interactive scientific viewer; no browser server or account required.

python experiments/explore.py
python experiments/explore.py --smoke-test  # headless interaction checks
"""
from pathlib import Path
import sys,json,argparse,wave
import numpy as np
import pandas as pd
import matplotlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from orthopolity import resource_spectrum,residual_audio

def build_viewer():
    import matplotlib.pyplot as plt
    from matplotlib.widgets import RadioButtons,Slider,Button
    noaa=pd.read_csv(ROOT/'results/noaa_pairs.csv');noaa=noaa[noaa.year>=2023]
    quakes=pd.read_csv(ROOT/'results/usgs_selected.csv')
    ocean=pd.read_csv(ROOT/'results/ocean_reexpression.csv')
    fig=plt.figure(figsize=(11,7))
    ax=fig.add_axes([.1,.36,.85,.55])
    radio=RadioButtons(fig.add_axes([.10,.08,.32,.19]),['NOAA end fluence','USGS energy proxy','Ocean reconstruction'])
    slider=Slider(fig.add_axes([.55,.23,.37,.04]),'Log bins',5,20,valinit=8,valstep=1)
    save=Button(fig.add_axes([.58,.10,.31,.07]),'Export view + sound')
    status=fig.text(.1,.02,'Exploration only. Bin changes do not constitute a new hypothesis test.',fontsize=9)
    current={}
    def redraw(_=None):
        ax.clear();mode=radio.value_selected
        if mode=='NOAA end fluence':
            s=resource_spectrum(noaa.k,noaa.q,np.geomspace(1e-5,1e-3,int(slider.val)+1))
            x=np.log10(s['center']);phi=s['phi'];label='Log10 peak irradiance (W/m²)'
            caption='NOAA 2023–2024 complete cases; no completeness correction'
        elif mode=='USGS energy proxy':
            e=quakes.energy_proxy_J
            s=resource_spectrum(e,e,np.geomspace(10**(4.8+1.5*5.45),10**(4.8+1.5*9.45),int(slider.val)+1))
            x=np.log10(s['center']);phi=s['phi'];label='Log10 magnitude-derived energy proxy (J)'
            caption='USGS 2010–2024; energy is inferred from magnitude'
        else:
            x=ocean.log10_mass_g.to_numpy();phi=ocean.phi.to_numpy();label='Log10 body mass (g)'
            caption='Published upper-200-m reconstruction; fixed original bins'
        ax.axhline(1,color='#999',ls='--',label='Equal resource per log interval')
        ax.plot(x,phi,'o-',color='black',label='Selected data')
        ax.set(xlabel=label,ylabel='Resource occupancy / domain mean',title=caption,ylim=(0,max(1.5,float(max(phi))*1.15)))
        ax.spines[['top','right']].set_visible(False);ax.legend(fontsize=9)
        current.update(mode=mode,x=np.asarray(x),phi=np.asarray(phi))
        fig.canvas.draw_idle()
    def export(_=None):
        out=ROOT/'results'/'exploration';out.mkdir(exist_ok=True)
        payload=dict(dataset=current['mode'],x=current['x'].tolist(),phi=current['phi'].tolist(),bins=len(current['phi']),
                     mapping='Equal duration per log bin; pitch=440*clip(Phi,0.25,4) Hz; zero/empty bins silent; no statistical meaning assigned to consonance')
        (out/'view.json').write_text(json.dumps(payload,indent=2))
        fig.savefig(out/'view.png',dpi=160)
        a=residual_audio(current['phi'])
        with wave.open(str(out/'residual.wav'),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes((a*32767).astype('<i2').tobytes())
        status.set_text('Exported results/exploration/view.json, view.png and residual.wav. Sound does not autoplay.')
        fig.canvas.draw_idle()
    radio.on_clicked(redraw);slider.on_changed(redraw);save.on_clicked(export)
    redraw()
    return fig,radio,slider,current,export

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--smoke-test',action='store_true');args=ap.parse_args()
    if args.smoke_test:matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,radio,slider,state,export=build_viewer()
    if args.smoke_test:
        slider.set_val(12);assert len(state['phi'])==12
        radio.set_active(1);assert state['mode']=='USGS energy proxy'
        radio.set_active(2);assert len(state['phi'])==23
        radio.set_active(0);slider.set_val(8);export()
        print('All dataset selectors, bin control and export exercised with a headless backend.')
        plt.close(fig)
    else:plt.show()
