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

namespace Vesper.Expansion {
    // Opt-in actual player recording/functional checks. Normal launch does not install this.
    public sealed class AdventurerRunProbe : MonoBehaviour {
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
        AdventurerMotor motor; AdventurerCamera cameraControl;
        AdventurerRunInput input; AdventurerRunAnimation animation;
        Transform leftFoot, rightFoot, leftToe, rightToe;
        VesperNavigation nav;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install() {
            var args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, "-runMotionQA");
            if (i < 0 || i + 1 >= args.Length) return;
            var p = new GameObject("Temporary run QA").AddComponent<AdventurerRunProbe>();
            p.output = args[i + 1]; Directory.CreateDirectory(p.output);
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void OnDisable() { Application.logMessageReceived -= Log; }
        void Log(string m, string s, LogType t) { if (t == LogType.Error || t == LogType.Exception) lock (errorLock) errors.Add(m); }
        void Check(bool condition, string name) { if (condition) passed.Add(name); else errors.Add(name); }
        void Route(Vector3 p) { Check(motor.Walk(p), "Accept route " + stage + " " + p); }
        IEnumerator Start() {
            motor = FindAnyObjectByType<AdventurerMotor>(); input = motor.GetComponent<AdventurerRunInput>();
            animation = motor.GetComponentInChildren<AdventurerRunAnimation>(); cameraControl = Camera.main.GetComponent<AdventurerCamera>();
            input.keyboardEnabled = false; input.SetRunning(false); nav = new VesperNavigation();
            var ts = motor.GetComponentsInChildren<Transform>();
            leftFoot = ts.First(t => t.name == "LeftFoot"); rightFoot = ts.First(t => t.name == "RightFoot");
            leftToe = ts.First(t => t.name == "LeftToeBase"); rightToe = ts.First(t => t.name == "RightToeBase");
            yield return new WaitForSecondsRealtime(4);
            foreach (var name in new[] { "idle", "walk-to-run", "run-to-walk", "run-stop", "run-reversal", "run-near-root", "orbit", "zoom", "reset" }) {
                stage = name; cameraControl.ResetView(); input.SetRunning(false);
                yield return new WaitForSecondsRealtime(.5f);
                float seconds = 3;
                if (name == "walk-to-run") { Route(new Vector3(4, 0, 6.7f)); seconds = 5; }
                if (name == "run-to-walk") { input.SetRunning(true); Route(new Vector3(4, 0, 6.7f)); seconds = 5; }
                if (name == "run-stop" || name == "run-reversal") { input.SetRunning(true); Route(new Vector3(4, 0, 6.7f)); seconds = name == "run-stop" ? 5 : 7; }
                if (name == "run-near-root") { input.SetRunning(true); cameraControl.SetZoom(8.8f); Route(new Vector3(3.4f, 0, 3.7f)); seconds = 10; }
                if (name == "orbit" || name == "zoom") seconds = 5;
                if (name == "reset") { input.SetRunning(true); Route(new Vector3(4, 0, 6.7f)); }
                var before = motor.transform.position; float start = Time.realtimeSinceStartup, next = start;
                bool changed = false, reversed = false; int waypoint = 0;
                while (Time.realtimeSinceStartup - start < seconds) {
                    float t = Time.realtimeSinceStartup - start;
                    if (name == "walk-to-run" && t > .65f && !changed) { input.SetRunning(true); changed = true; }
                    if (name == "run-to-walk" && t > .85f && !changed) { input.SetRunning(false); changed = true; }
                    if (name == "run-reversal" && t > 1.05f && !reversed) { Route(motor.home); reversed = true; }
                    if (name == "run-near-root" && !motor.IsWalking && waypoint < 2) { waypoint++; Route(waypoint == 1 ? new Vector3(4, 0, 6.7f) : new Vector3(6, 0, 7.4f)); }
                    if (name == "orbit") cameraControl.Orbit(Time.unscaledDeltaTime * .1f, 0);
                    if (name == "zoom") cameraControl.SetZoom(10.4f + Mathf.Sin(t * 1.2f) * 2.9f);
                    if (name == "reset" && t > .8f && !changed) { cameraControl.ResetView(); before = motor.transform.position; changed = true; }
                    distance += Vector3.Distance(before, motor.transform.position); before = motor.transform.position;
                    peakSpeed = Mathf.Max(peakSpeed, motor.Speed);
                    if (!nav.Valid(before) && !errors.Contains("Courtyard clearance violation")) errors.Add("Courtyard clearance violation");
                    if (Time.realtimeSinceStartup >= next) { yield return new WaitForEndOfFrame(); Capture(); next = Time.realtimeSinceStartup + 1f / 12; }
                    else yield return null;
                }
                Check(!motor.IsWalking, name + " ends stationary");
                if (name == "walk-to-run" || name == "run-stop") Check(frames.Any(f => f.stage == name && f.runBlend > .98f && f.speed > input.runningSpeed * .96f), name + " reaches full run");
                if (name == "run-to-walk") Check(frames.Any(f => f.stage == name && !f.requested && f.speed > 2.1f && f.speed < 2.4f && f.runBlend < .05f), "Shift release returns to walk while moving");
                if (name == "reset") Check(Vector3.Distance(motor.transform.position, motor.home) < .001f && animation.Blend < .001f, "Reset clears run route and animation");
            }
            Check(frames.All(f => f.speed > .02f || f.runBlend < .05f || f.blend < .95f), "No sustained stationary running");
            while (Volatile.Read(ref pending) > 0) yield return null;
            File.WriteAllText(Path.Combine(output, "motion-report.json"), JsonUtility.ToJson(new Report {
                width = Screen.width, height = Screen.height, skipped = skipped, distance = distance, peakSpeed = peakSpeed,
                frames = frames.ToArray(), passed = passed.ToArray(), errors = errors.ToArray()
            }, true));
            Application.Quit(errors.Count == 0 ? 0 : 1);
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
