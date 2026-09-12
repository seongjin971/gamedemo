using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public sealed class VesperSmokeProbe:MonoBehaviour {
    readonly List<string> errors=new List<string>();readonly List<float> samples=new List<float>();string destination;RenderTexture target;Camera renderCamera;
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Install(){string p=Environment.GetEnvironmentVariable("VESPER_PLAY_SMOKE");if(!string.IsNullOrEmpty(p)){var probe=new GameObject("Temporary migration smoke probe").AddComponent<VesperSmokeProbe>();probe.destination=p;}}
    void OnEnable(){Application.logMessageReceived+=Log;}void OnDisable(){Application.logMessageReceived-=Log;}
    void Log(string condition,string stack,LogType type){if(type==LogType.Error||type==LogType.Exception||type==LogType.Assert)errors.Add(condition);}
    void Update(){samples.Add(Time.unscaledDeltaTime);}
    void LateUpdate(){if(renderCamera&&target){RenderPipeline.SubmitRenderRequest(renderCamera,new UniversalRenderPipeline.SingleCameraRequest{destination=target});}}
    IEnumerator Start(){yield return null;var knight=FindAnyObjectByType<VesperKnight>();renderCamera=Camera.main;target=new RenderTexture(1037,739,24,RenderTextureFormat.ARGB32);target.Create();renderCamera.aspect=1037f/739;Vector3 start=knight.transform.position;knight.Walk(new Vector3(-3.08f,0,5.21f));yield return new WaitForSecondsRealtime(8);
      Vector3 arrived=knight.transform.position;float moved=Vector3.Distance(start,arrived);if(moved<1)errors.Add("Knight did not move");if(!new VesperNavigation().Valid(arrived))errors.Add("Knight left valid courtyard");
      var reflection=FindAnyObjectByType<Vesper.VesperPlanarReflection>();if(!reflection||reflection.RenderedFrameCount<2)errors.Add("Planar reflection did not update");
      var result=new Result{movedDistance=moved,validPosition=new VesperNavigation().Valid(arrived),reflectionFrames=reflection?reflection.RenderedFrameCount:0,frames=samples.Count,errors=errors.ToArray(),note="Scripted Unity Editor Play with explicit render requests. Not direct user input or presented FPS acceptance."};File.WriteAllText(destination,JsonUtility.ToJson(result,true));Debug.Log("VESPER_PLAY_SMOKE_SAVED");target.Release();target=null;
    }
    [Serializable]class Result{public float movedDistance;public bool validPosition;public int reflectionFrames,frames;public string[] errors;public string note;}
}
