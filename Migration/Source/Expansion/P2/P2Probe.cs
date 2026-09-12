using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Experimental.Rendering;

namespace Vesper.Expansion.P2 {
    // Opt-in actual player recording/functional checks. Normal launch does not install this.
    public sealed class P2Probe : MonoBehaviour {
        [Serializable] public class Frame {
            public string file, stage; public float time, speed, blend, runBlend, phase;
            public Vector3 player, leftFoot, rightFoot, leftToe, rightToe;
            public bool focused, requested;
        }
        [Serializable] public class Report {
            public string note = "Actual standalone frames with automatic commands, not direct input or performance. JPEG95 requested at12Hz. Toe/ankle points are not exact sole contacts.";
            public int width, height, skipped; public float distance, peakSpeed;
            public Frame[] frames; public string[] passed, errors;
        }
        readonly List<Frame> frames = new List<Frame>();
        readonly List<string> passed = new List<string>(), errors = new List<string>();
        readonly object errorLock = new object();
        string output, stage; int pending, skipped;
        float distance, peakSpeed;
        P2Motor motor; P2Camera cameraControl;
        P2RunInput input; P2Animation animation;
        Transform leftFoot, rightFoot, leftToe, rightToe;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install() {
            var args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, "-p2QA");
            if (i < 0 || i + 1 >= args.Length) return;
            var p = new GameObject("Temporary run QA").AddComponent<P2Probe>();
            p.output = args[i + 1]; Directory.CreateDirectory(p.output);
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void OnDisable() { Application.logMessageReceived -= Log; }
        void Log(string m, string s, LogType t) { if (t == LogType.Error || t == LogType.Exception) lock (errorLock) errors.Add(m); }
        void Check(bool condition, string name) { if (condition) passed.Add(name); else errors.Add(name); }
        void Route(Vector3 p) { Check(motor.Walk(p), "Accept route " + stage + " " + p); }
        P2World world;
        IEnumerator Record(float seconds) {
            float start=Time.realtimeSinceStartup,next=start;
            while(Time.realtimeSinceStartup-start<seconds){
                distance+=motor.Distance;peakSpeed=Mathf.Max(peakSpeed,motor.Speed);
                if(Time.realtimeSinceStartup>=next){yield return new WaitForEndOfFrame();Capture();next=Time.realtimeSinceStartup+.12f;}else yield return null;
            }
        }
        IEnumerator Travel(Vector3 point,string label,bool run) {
            stage=label;input.SetRunning(run);Route(point);
            float start=Time.realtimeSinceStartup;
            do{yield return Record(.2f);}while(motor.IsWalking && Time.realtimeSinceStartup-start<20 && !world.Busy);
            if(!world.Busy)Check(Vector3.Distance(motor.transform.position,point)<.24f,"Arrived "+label);
            yield return Record(.4f);
        }
        IEnumerator Portal(Vector3 point,int zone,string label) {
            stage=label;input.SetRunning(true);Route(point);float start=Time.realtimeSinceStartup;
            while((world.Zone!=zone || world.Busy) && Time.realtimeSinceStartup-start<15)yield return Record(.25f);
            Check(world.Zone==zone && !world.Busy,"Portal completed "+label);
            yield return Record(1.2f);
            Check(FindObjectsByType<P2Motor>().Length==1,"One player "+label);
            Check(FindObjectsByType<P2Camera>().Length==1,"One gameplay camera "+label);
            Check(world.courtyard.activeSelf!=world.connection.activeSelf,"One active area "+label);
            var active=zone==0?world.courtyard:world.connection;
            Check(FindObjectsByType<Light>().Length==active.GetComponentsInChildren<Light>().Length,"No old-area lights "+label);
            Check(FindObjectsByType<VesperAtmosphereMotion>().Length==(zone==0?1:0),"No old-area atmosphere "+label);
            Check(FindObjectsByType<Camera>().Count(c=>c.GetComponent<P2Camera>())==1 && FindObjectsByType<Camera>().Length<=(zone==0?2:1),"No orphan cameras "+label);
            Check(FindObjectsByType<VesperPlanarReflection>().Length==(zone==0?1:0),"Reflection ownership "+label);
            Check(Vector3.Distance(motor.transform.position,motor.home)<.01f,"Entrance spawn "+label);
        }
        IEnumerator Start() {
            motor=FindAnyObjectByType<P2Motor>();input=motor.GetComponent<P2RunInput>();animation=motor.GetComponentInChildren<P2Animation>();cameraControl=Camera.main.GetComponent<P2Camera>();world=P2World.Instance;
            input.keyboardEnabled=false;input.SetRunning(false);
            var ts=motor.GetComponentsInChildren<Transform>();leftFoot=ts.First(t=>t.name=="LeftFoot");rightFoot=ts.First(t=>t.name=="RightFoot");leftToe=ts.First(t=>t.name=="LeftToeBase");rightToe=ts.First(t=>t.name=="RightToeBase");
            yield return new WaitForSecondsRealtime(4);
            stage="courtyard-idle";yield return Record(1);
            yield return Travel(new Vector3(4,0,6.7f),"courtyard-walk",false);
            yield return Travel(new Vector3(-2.25f,0,7.5f),"courtyard-run",true);
            for(int trip=1;trip<=3;trip++){
                yield return Portal(world.courtyardGate,1,"outbound-"+trip);
                stage="rejection-"+trip;
                Check(!motor.Click(new Ray(new Vector3(5,8,-2),Vector3.down)),"Water rejected "+trip);
                Check(!motor.Click(new Ray(new Vector3(.25f,8,-7.1f),Vector3.down)),"Obstacle top rejected "+trip);
                Check(!motor.Click(new Ray(new Vector3(6,8,-7),Vector3.down)),"Disconnected high ledge rejected "+trip);
                Check(!motor.Click(new Ray(new Vector3(-6,2,8),Vector3.right)),"Side wall rejected "+trip);
                Check(motor.Click(new Ray(new Vector3(0,8,-2.5f),Vector3.down)),"Bridge ray chooses upper deck "+trip);
                stage="bridge-click-"+trip;yield return Record(.3f);
                yield return Travel(new Vector3(0,1.6f,-2.5f),"ramp-bridge-"+(trip==2?"run-":"walk-")+trip,trip==2);
                Check(Mathf.Abs(motor.transform.position.y-1.6f)<.04f,"Bridge height "+trip);
                var screen=Camera.main.WorldToScreenPoint(new Vector3(0,1.6f,-2.5f));
                Check(motor.Click(Camera.main.ScreenPointToRay(screen)),"Game camera bridge click "+trip);
                yield return Travel(new Vector3(-2,1.6f,-9.2f),"upper-obstacle-run-"+trip,true);
                cameraControl.Orbit(.35f,.1f);cameraControl.SetZoom(7.5f);stage="upper-orbit-zoom-"+trip;yield return Record(1);
                yield return Travel(new Vector3(1.2f,0,8.2f),"bridge-ramp-"+(trip==2?"walk-":"run-")+"down-"+trip,trip!=2);
                Check(Mathf.Abs(motor.transform.position.y)<.04f,"Lower height "+trip);
                stage="connection-reset-"+trip;cameraControl.ResetView();yield return Record(.6f);
                Check(Vector3.Distance(motor.transform.position,world.connectionSpawn)<.01f && !motor.IsWalking,"R current connection entrance "+trip);
                yield return Portal(world.connectionGate,0,"return-"+trip);
                yield return Travel(new Vector3(-2.25f,0,7.5f),"return-courtyard-walk-"+trip,false);
                stage="courtyard-reset-"+trip;cameraControl.ResetView();yield return Record(.6f);
                Check(Vector3.Distance(motor.transform.position,world.returnSpawn)<.01f,"R current courtyard entrance "+trip);
            }
            Check(world.Transitions==6,"Three round trips");
            Check(frames.Any(f=>f.stage.StartsWith("ramp-bridge") && f.player.y>.2f && f.player.y<1.4f),"Intermediate ramp height observed");
            Check(frames.Any(f=>f.stage.StartsWith("bridge-ramp-run") && f.speed>5.1f),"Downhill reaches running speed");
            while(Volatile.Read(ref pending)>0)yield return null;
            File.WriteAllText(Path.Combine(output,"motion-report.json"),JsonUtility.ToJson(new Report{width=Screen.width,height=Screen.height,skipped=skipped,distance=distance,peakSpeed=peakSpeed,frames=frames.ToArray(),passed=passed.ToArray(),errors=errors.ToArray()},true));
            Application.Quit(errors.Count==0?0:1);
        }
        void Capture() {
            if (Volatile.Read(ref pending) >= 4) { skipped++; return; }
            string file = frames.Count.ToString("D4") + ".jpg", path = Path.Combine(output, file);
            int width = Screen.width, height = Screen.height; bool flip = SystemInfo.graphicsUVStartsAtTop;
            var target = RenderTexture.GetTemporary(width, height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            ScreenCapture.CaptureScreenshotIntoRenderTexture(target); Interlocked.Increment(ref pending);
            frames.Add(new Frame { file = file, stage = stage, time = Time.realtimeSinceStartup, speed = motor.Speed,
                blend = animation.Blend, runBlend = animation.RunBlend, phase = animation.Phase, requested = input.Requested,
                player = motor.transform.position, focused = Application.isFocused, leftFoot = leftFoot.position, rightFoot = rightFoot.position,
                leftToe = leftToe.position, rightToe = rightToe.position });
            AsyncGPUReadback.Request(target, 0, TextureFormat.RGBA32, request => {
                if (request.hasError) { lock (errorLock) errors.Add("Readback failed " + file); RenderTexture.ReleaseTemporary(target); Interlocked.Decrement(ref pending); return; }
                byte[] pixels = request.GetData<byte>().ToArray(); RenderTexture.ReleaseTemporary(target);
                Task.Run(() => {
                    try {
                        if (flip) { int stride = width * 4; var reversed = new byte[pixels.Length]; for (int row = 0; row < height; row++) Buffer.BlockCopy(pixels, row * stride, reversed, (height - 1 - row) * stride, stride); pixels = reversed; }
                        File.WriteAllBytes(path, ImageConversion.EncodeArrayToJPG(pixels, GraphicsFormat.R8G8B8A8_UNorm, (uint)width, (uint)height, 0, 95));
                    } catch (Exception e) { lock (errorLock) errors.Add(e.Message); } finally { Interlocked.Decrement(ref pending); }
                });
            });
        }
    }
}
