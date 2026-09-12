from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
new=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherW09/Runtime/WeatherW09Probe.cs'
if new.exists():raise SystemExit('Do not overwrite W09 probe')
new.parent.mkdir(parents=True,exist_ok=True)
s=(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherW08/Runtime/WeatherW08Probe.cs').read_text().replace('WeatherW08Probe','WeatherW09Probe').replace('namespace Vesper.Expansion.WeatherW08','namespace Vesper.Expansion.WeatherW09').replace('-w08','-w09').replace('W08 targeted','W09 targeted').replace('W08-normal','W09-normal').replace('W08-flash','W09-flash').replace('W08-strong','W09-strong').replace('canopy-W08-','canopy-W09-')
new.write_text(s,encoding='utf-8')
runner=ROOT/'Migration/Source/Expansion/WeatherW09/run_w09.ps1'
runner.write_text((ROOT/'Migration/Source/Expansion/WeatherW08/run_w08.ps1').read_text().replace('w08','w09').replace('W08','W09'),encoding='utf-8')
checker=ROOT/'Migration/Source/Expansion/WeatherW09/check_w09.py'
checker.write_text((ROOT/'Migration/Source/Expansion/WeatherW08/check_w08.py').read_text().replace('W08','W09'),encoding='utf-8')
(ROOT/'Migration/Evidence/Expansion/WeatherWorld/W09').mkdir(exist_ok=False)
print('W09 preserves W08 geometry and flash; includes transparent cutaway shader variant')
