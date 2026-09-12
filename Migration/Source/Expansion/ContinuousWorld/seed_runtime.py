"""Create independent ContinuousWorld controls from the preserved P2 controls."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
SRC=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/P2/Runtime'
DST=ROOT/'Unity/Vesper/Assets/Vesper/Expansion/ContinuousWorld/Runtime'
for name in ['Animation','RunInput','Camera']:
    text=(SRC/f'P2{name}.cs').read_text(encoding='utf-8-sig')
    text=text.replace('Vesper.Expansion.P2','Vesper.Expansion.ContinuousWorld').replace('P2Motor','WorldMotor').replace('P2RunInput','WorldRunInput').replace('P2Animation','WorldAnimation').replace('P2Camera','WorldCamera')
    text=text.replace('(P2World.Instance && P2World.Instance.Busy)','false')
    text=text.replace('if(P2World.Instance && P2World.Instance.Busy)','if(false)').replace('if (P2World.Instance && P2World.Instance.Busy)','if (false)')
    text=text.replace('P2 walk and run','Continuous world walk and run').replace('-p2InputTrace','-worldInputTrace').replace('P2 INPUT','WORLD INPUT')
    if name=='Camera':
        text=text.replace('new Vector3(.75f, 1, .75f)','Vector3.one')
        text=text.replace('var follow = homeTarget + (player ? Vector3.Scale(player.transform.position - initialPlayer, (MatchP1Framing ? Vector3.one * .24f : Vector3.one)) : Vector3.zero);','var follow = player ? player.transform.position + Vector3.up * 1.2f : homeTarget;')
        text=text.replace('target = homeTarget; Zoom = homeSize;', 'target = player ? player.transform.position + Vector3.up * 1.2f : homeTarget; Zoom = homeSize;')
        text=text.replace('7.5f','6.5f').replace('Mathf.Clamp(value, 6.5f, 14)','Mathf.Clamp(value, 6.5f, 18)')
        text=text.replace('Application.targetFrameRate = 60','Application.targetFrameRate = 120')
    (DST/f'World{name}.cs').write_text(text,encoding='utf-8')
print('Independent animation, run input, camera created')
