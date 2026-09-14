#!/usr/bin/env python3
"""Apply the W11 mix to the explicitly selected scaffold project via Wwise 2025.1 WAAPI.

Re-running updates only the named W11 containers. Source-library pools are moved once.
This edits authoring data; bank generation is a separate command.
"""
import argparse,json,pathlib
from prepare_wwise import native_project_path
from waapi import WaapiClient
ROOT=pathlib.Path(__file__).resolve().parents[1]; A=r'\Containers\Vesper_W11'; W=A+r'\World_Ambience'; F=W+r'\Forest'; M=W+r'\SnowMountain'; L=A+r'\Source_Library'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project',type=pathlib.Path,required=True)
parser.add_argument('--url',default='ws://127.0.0.1:8080/waapi')
args=parser.parse_args()
with WaapiClient(args.url,allow_exception=True) as c:
 project=c.call('ak.wwise.core.object.get',{'from':{'ofType':['Project']}},options={'return':['id','filePath']})['return'][0]
 if native_project_path(project['filePath']).resolve()!=args.project.resolve():raise RuntimeError('The explicitly requested Wwise project must be open.')
 def call(uri,**args):
  r=c.call('ak.wwise.core.'+uri,args)
  if r is None:raise RuntimeError(uri+' '+str(args))
  return r
 def sets(obj,**props):return call('object.set',objects=[dict(object=obj,**{'@'+k:v for k,v in props.items()})])
 def get(path):return c.call('ak.wwise.core.object.get',{'waql':'$ where path = '+chr(34)+path+chr(34)},options={'return':['id','path']})['return']
 def rtpcs(obj,curves):
  items=[{'type':'RTPC','name':'','@PropertyName':'Volume','@ControlInput':r'\Game Parameters\Vesper_W11'+'\\'+par,'@Curve':{'type':'Curve','points':[{'x':x,'y':y,'shape':'Linear'} for x,y in points]}} for par,points in curves]
  call('object.set',objects=[{'object':obj,'listMode':'replaceAll','@RTPC':items}])
 for o in c.call('ak.wwise.core.object.get',{'waql':'$ from object '+chr(34)+A+chr(34)+' select descendants where type = '+chr(34)+'RandomSequenceContainer'+chr(34)},options={'return':['id']})['return']:sets(o['id'],RandomOrSequence=1,PlayMechanismStepOrContinuous=1,NormalOrShuffle=0,RandomAvoidRepeating=True,RandomAvoidRepeatingCount=1)
 sets(A+r'\Footsteps',Volume=-7)
 sets(W,SwitchBehavior=1,Volume=-10,OverrideVirtualVoice=True,BelowThresholdBehavior=2,VirtualVoiceQueueBehavior=1)
 day=[[0,-96],[5,-24],[8,0],[16,0],[19,-96],[24,-96]]
 night=[[0,0],[5,0],[8,-96],[17,-96],[20,0],[24,0]]
 rain=[[0,-96],[.15,-24],[.5,-8],[1,0]]
 dry=[[0,0],[.2,-3],[.6,-18],[1,-40]]
 for layer in json.load(open(ROOT/'Audio/wwise-authoring-plan.json'))['rtpc_volume_curves_to_author']:
  if layer['rtpc']:rtpcs(layer['object'],[(layer['rtpc'],layer['points'])])
 for name in ['Day_Wind','Night_Bed','Rain_Bed','Rain_Heavy']:sets(F+'\\'+name,Volume=-4)
 # These pools are moved, not duplicated; all source media IDs remain stable.
 schedules=[('ambience_morning_random_one_shot_bird',F,'Day_Birds',14,day,dry),('ambience_morning_random_one_shot_bug',F,'Day_Bugs',22,day,dry),('ambience_morning_random_one_shot_grass',F,'Day_Grass',28,day,dry),('ambience_morning_random_one_shot_wind',F,'Day_Gusts',32,day,dry),('ambience_night_oneshot_bug',F,'Night_Bugs',18,night,dry),('ambience_night_oneshot_owl',F,'Night_Owls',36,night,dry),('ambience_night_oneshot_wolf',F,'Night_Wolves',65,night,dry),('ambience_rainnight_random_randomgrass',F,'Rain_Grass',24,None,rain),('ambience_rainnight_random_randomwind',F,'Rain_Gusts',30,None,rain),('ambience_snow_random_randomwind',M,'Snow_Gusts',25,None,None),('ambience_snow_random_randomwolf',M,'Snow_Wolves',65,None,None)]
 for old,parent,name,delay,timecurve,raincurve in schedules:
  dest=parent+'\\'+name
  if not get(dest):
   moved=call('object.move',object=L+'\\'+old,parent=parent,onNameConflict='fail');call('object.setName',object=parent+'\\'+old,value=name)
  sets(dest,PlayMechanismStepOrContinuous=0,PlayMechanismLoop=True,PlayMechanismInfiniteOrNumberOfLoops=1,PlayMechanismSpecialTransitions=True,PlayMechanismSpecialTransitionsType=1,PlayMechanismSpecialTransitionsValue=delay,InitialDelay=delay/2,Volume=-12)
  for prop,span in [('PlayMechanismSpecialTransitionsValue',delay*.35),('InitialDelay',delay*.2)]:call('object.setRandomizer',object=dest,property=prop,enabled=True,min=-span,max=span)
  rtpcs(dest,[(p,v) for p,v in [('TimeOfDay',timecurve),('RainIntensity',raincurve)] if v])
 att=r'\Attenuations\Default Work Unit\Lake_40m'
 if not get(att):call('object.create',parent=r'\Attenuations\Default Work Unit',type='Attenuation',name='Lake_40m')
 sets(att,RadiusMax=40)
 call('object.setAttenuationCurve',object=att,curveType='VolumeDryUsage',use='Custom',points=[{'x':x,'y':y,'shape':'Linear'} for x,y in [[0,0],[8,-3],[20,-18],[40,-96]]])
 sets(A+r'\Lake_Ambience',OverridePositioning=True,ListenerRelativeRouting=True,EnableAttenuation=True,Attenuation=att,Volume=-10,OverrideVirtualVoice=True,BelowThresholdBehavior=2,VirtualVoiceQueueBehavior=1,**{'3DPosition':0,'3DSpatialization':1})
 project=c.call('ak.wwise.core.object.get',{'from':{'ofType':['Project']}},options={'return':['id','filePath']})['return'][0]
 if native_project_path(project['filePath']).resolve()!=args.project.resolve():raise RuntimeError('Wwise project changed during authoring.')
 sets(project['id'],AutoSoundBankEnabled=False,GenerateSoundBankJSON=True,GenerateSoundBankXML=True,SoundBankGenerateHeaderFile=True,SoundBankGeneratePrintGUID=True,SoundBankGeneratePrintPath=True,SoundBankGenerateMaxAttenuationInfo=True,CopyLooseStreamedMedia=True,SoundBankHeaderFilePath='../../Unity/Vesper/Assets/StreamingAssets/Audio/GeneratedSoundBanks/')
 for platform in ['Mac','Windows']:call('object.setProperty',object=project['id'],property='SoundBankPaths',platform=platform,value='../../Unity/Vesper/Assets/StreamingAssets/Audio/GeneratedSoundBanks/'+platform+'/')
 contexts=c.call('ak.wwise.core.object.get',{'waql':'$ from object '+(chr(34)+W+chr(34))+' select children select switchContainerChildContext'},options={'return':['id']})['return']
 assert len(contexts)==2
 for obj in contexts:sets(obj['id'],FadeInTime=1.5,FadeOutTime=1.5,ContinuePlay=False)
 call('project.save')
 print('Authoring mix applied.')
