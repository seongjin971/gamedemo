"""Authored loopable environmental beds; no speech, music, stock recordings or external source.
Periodic spectral synthesis yields continuous boundaries. They remain authored synthetic ambience,
not field recordings. Output levels reserve headroom for the environment mixer.
"""
from pathlib import Path
import numpy as np
import wave,json
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Art/Audio'
OUT.mkdir(parents=True,exist_ok=True)
RATE=22050; SECONDS=32; N=RATE*SECONDS
rng=np.random.default_rng(1973)
t=np.arange(N)/RATE
freq=np.fft.rfftfreq(N,1/RATE)
def bed(low,high,rolloff=0.5):
    amp=1/np.maximum(freq,low)**rolloff
    amp*=np.minimum(1,(freq/max(1,low))**2)
    amp*=np.exp(-(freq/high)**4);amp[0]=0
    spectrum=amp*np.exp(1j*rng.uniform(0,2*np.pi,len(freq)))
    value=np.fft.irfft(spectrum,n=N);return value/np.std(value)
water=.38*bed(110,3100,.6)+.12*bed(1800,8000,.15)
water*=.78+.13*np.sin(2*np.pi*t/16)+.09*np.sin(2*np.pi*t/8+.7)
# Broad irregular splashes are a quiet continuous stream texture, not identifiable hard clicks.
for i in range(55):
    at=rng.uniform(0,SECONDS);width=rng.uniform(.04,.24);d=(t-at+SECONDS/2)%SECONDS-SECONDS/2
    envelope=np.exp(-(d/width)**2)
    water+=envelope*.14*np.sin(2*np.pi*rng.uniform(250,1350)*d)*np.exp(-np.abs(d)*15)
rain=.35*bed(350,7600,.35)+.15*bed(150,2300,.65)
rain*=.85+.1*np.sin(2*np.pi*t/16+.8)+.05*np.sin(2*np.pi*t/4)
wind=bed(35,1100,1)*(.27+.12*np.sin(2*np.pi*t/16)+.09*np.sin(2*np.pi*t/8+.9))
stats={}
for name,data in [('River',water),('Rain',rain),('PassWind',wind)]:
    data=data-np.mean(data);data=data/max(1,np.max(np.abs(data))/.65)
    pcm=np.clip(data*32767,-32768,32767).astype('<i2')
    with wave.open(str(OUT/(name+'.wav')),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm.tobytes())
    stats[name]={'samples':N,'seconds':SECONDS,'rate':RATE,'peak':float(np.max(np.abs(data))),'rms':float(np.sqrt(np.mean(data**2))),'loopSampleDelta':int(pcm[0])-int(pcm[-1]),'source':'Authored periodic environmental synthesis'}
(OUT/'provenance.json').write_text(json.dumps(stats,indent=2))
print(json.dumps(stats,indent=2))
