from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
new=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherW08/Runtime/WeatherW08Probe.cs'
if new.exists():raise SystemExit('Do not overwrite W08 probe')
s=(ROOT/'Unity/Vesper/Assets/Vesper/Expansion/WeatherW07/Runtime/WeatherW07Probe.cs').read_text()
s=s.replace('namespace Vesper.Expansion.WeatherW07 {','using Vesper.Expansion.WeatherW07;\nnamespace Vesper.Expansion.WeatherW08 {').replace('WeatherW07Probe','WeatherW08Probe').replace('-w07','-w08').replace('W07 targeted','W08 targeted').replace('W07-normal','W08-normal').replace('W07-flash','W08-flash').replace('W07-strong','W08-strong').replace('canopy-W07-','canopy-W08-')
new.write_text(s,encoding='utf-8')
runner=ROOT/'Migration/Source/Expansion/WeatherW08/run_w08.ps1'
s=(ROOT/'Migration/Source/Expansion/WeatherW07/run_w07.ps1').read_text().replace('w07','w08').replace('W07','W08').replace("'Inspect','Prepare','Build'","'PrepareAndBuild'").replace("'Inspect','Prepare','Build','Capture'","'PrepareAndBuild','Capture'")
runner.write_text(s,encoding='utf-8')
(ROOT/'Migration/Evidence/Expansion/WeatherWorld/W08').mkdir(exist_ok=False)
print('W08 isolated screen-effect candidate prepared')
