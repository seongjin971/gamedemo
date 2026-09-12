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
    // Opt-in recording only. No readback or telemetry work in the normal launcher.
    public sealed class AdventurerMotionProbe : MonoBehaviour {
        [Serializable] public class Frame {
            public string file, stage; public float time, angle, elevation, zoom, speed, blend, phase;
            public Vector3 player, camera, leftFoot, rightFoot, leftToe, rightToe; public bool focused;
        }
        [Serializable] public class Arrival { public string stage; public int destination; public float time; public Vector3 requested, actual; }
        [Serializable] public class Report {
            public string note = "Actual standalone render loop with automatic motor/camera commands. JPEG95 asynchronous readback requested at 12Hz. Not direct input, not clean FPS, not monitor presentation. Bone positions are contact diagnostics, not exact sole geometry.";
            public int width, height, skipped; public float distance;
            public Frame[] frames; public Arrival[] arrivals; public string[] errors;
        }
        string output, stage = "warmup";
        readonly List<Frame> frames = new List<Frame>(); readonly List<Arrival> arrivals = new List<Arrival>();
        readonly List<string> errors = new List<string>(); readonly object errorLock = new object();
        AdventurerMotor motor; AdventurerCamera control; AdventurerAnimation animation;
        Transform leftFoot, rightFoot, leftToe, rightToe;
        Vector3 previous; float distance; int pending, skipped;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install() {
            var args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, "-p1MotionQA");
            if (i < 0 || i + 1 >= args.Length) return;
            var probe = new GameObject("P1 temporary motion verification").AddComponent<AdventurerMotionProbe>();
            probe.output = args[i + 1]; Directory.CreateDirectory(probe.output);
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void OnDisable() { Application.logMessageReceived -= Log; }
        void Log(string message, string stack, LogType type) { if (type == LogType.Error || type == LogType.Exception) lock (errorLock) errors.Add(message); }
        IEnumerator Start() {
            motor = FindAnyObjectByType<AdventurerMotor>(); control = Camera.main.GetComponent<AdventurerCamera>();
            animation = motor.GetComponentInChildren<AdventurerAnimation>();
            var transforms = motor.GetComponentsInChildren<Transform>();
            leftFoot = transforms.First(t => t.name == "LeftFoot"); rightFoot = transforms.First(t => t.name == "RightFoot");
            leftToe = transforms.First(t => t.name == "LeftToeBase"); rightToe = transforms.First(t => t.name == "RightToeBase");
            var nav = new VesperNavigation();
            yield return new WaitForSecondsRealtime(4);
            foreach (string phase in new[] { "idle", "walk-stop", "turn", "near-root", "orbit", "zoom", "wide-limit", "close-limit" }) {
                stage = phase;
                if (phase != "walk-stop" && phase != "turn") {
                    control.ResetView(); yield return new WaitForSecondsRealtime(1);
                }
                previous = motor.transform.position;
                float start = Time.realtimeSinceStartup, next = start;
                int destination = 0; bool arrivalRecorded = false, reversed = false;
                var destinations = new[] { new Vector3(-3.08f, 0, 5.21f) };
                if (phase == "turn") destinations = new[] { new Vector3(0, 0, 10), new Vector3(-3.08f, 0, 5.21f) };
                if (phase == "near-root") destinations = new[] { new Vector3(3.4f, 0, 3.7f), new Vector3(4, 0, 6.7f), new Vector3(6, 0, 7.4f) };
                bool walking = phase == "walk-stop" || phase == "turn" || phase == "near-root";
                if (walking && !motor.Walk(destinations[0])) errors.Add("Initial route rejected: " + phase);
                if (phase == "near-root") control.SetZoom(8.8f);
                if (phase == "wide-limit") { control.SetZoom(14); control.Orbit(.64f, -.24f); }
                if (phase == "close-limit") { control.SetZoom(7.5f); control.Orbit(-.51f, .42f); }
                float seconds = phase == "near-root" ? 16 : phase == "walk-stop" || phase == "turn" ? 9 : phase == "idle" ? 3 : 6;
                while (Time.realtimeSinceStartup - start < seconds) {
                    float t = Time.realtimeSinceStartup - start;
                    if (walking && !motor.IsWalking && !arrivalRecorded) {
                        arrivals.Add(new Arrival { stage = phase, destination = destination, time = Time.realtimeSinceStartup,
                            requested = destinations[destination], actual = motor.transform.position });
                        arrivalRecorded = true;
                        if (phase == "near-root" && destination + 1 < destinations.Length) {
                            destination++; motor.Walk(destinations[destination]); arrivalRecorded = false;
                        }
                    }
                    if (phase == "turn" && t > 4 && !reversed) {
                        reversed = true; destination = 1; arrivalRecorded = false; motor.Walk(destinations[1]);
                    }
                    if (walking && !nav.Valid(motor.transform.position) && !errors.Contains("Route crossed clearance")) errors.Add("Route crossed clearance");
                    if (phase == "orbit") control.Orbit(Time.unscaledDeltaTime * .085f, Mathf.Sin(t * .9f) * Time.unscaledDeltaTime * .025f);
                    if (phase == "zoom") control.SetZoom(10.5f + Mathf.Sin(t * .85f) * 2.3f);
                    distance += Vector3.Distance(previous, motor.transform.position); previous = motor.transform.position;
                    if (Time.realtimeSinceStartup >= next) { yield return new WaitForEndOfFrame(); Capture(); next = Time.realtimeSinceStartup + 1f / 12; }
                    else yield return null;
                }
            }
            while (Volatile.Read(ref pending) > 0) yield return null;
            File.WriteAllText(Path.Combine(output, "motion-report.json"), JsonUtility.ToJson(new Report { width = Screen.width, height = Screen.height,
                skipped = skipped, distance = distance, frames = frames.ToArray(), arrivals = arrivals.ToArray(), errors = errors.ToArray() }, true));
            Application.Quit();
        }
        void Capture() {
            if (Volatile.Read(ref pending) >= 4) { skipped++; return; }
            string file = frames.Count.ToString("D4") + ".jpg", path = Path.Combine(output, file);
            int width = Screen.width, height = Screen.height; bool flip = SystemInfo.graphicsUVStartsAtTop;
            var target = RenderTexture.GetTemporary(width, height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            ScreenCapture.CaptureScreenshotIntoRenderTexture(target); Interlocked.Increment(ref pending);
            frames.Add(new Frame { file = file, stage = stage, time = Time.realtimeSinceStartup, player = motor.transform.position,
                camera = Camera.main.transform.position, angle = control.Angle, elevation = control.Elevation, zoom = Camera.main.orthographicSize,
                speed = motor.Speed, blend = animation.Blend, phase = animation.Phase, focused = Application.isFocused,
                leftFoot = leftFoot.position, rightFoot = rightFoot.position, leftToe = leftToe.position, rightToe = rightToe.position });
            AsyncGPUReadback.Request(target, 0, TextureFormat.RGBA32, request => {
                if (request.hasError) { lock (errorLock) errors.Add("Readback failed: " + file); RenderTexture.ReleaseTemporary(target); Interlocked.Decrement(ref pending); return; }
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
