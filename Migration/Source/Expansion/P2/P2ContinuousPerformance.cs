using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Vesper.Expansion.P2 {
    public sealed class P2ContinuousPerformance : MonoBehaviour {
        [Serializable] public class Stage { public string name; public int frames, unfocused; public float fps, p95Ms, distance, peakSpeed; }
        [Serializable] public class Report { public string note = "Isolated standalone natural frame cadence, continuous automatic routes, no image readback or video encoding. Not direct input or hardware presentation.", device; public int width, height; public Stage[] stages; public string[] errors; }
        string output; readonly List<Stage> stages = new List<Stage>(); readonly List<string> errors = new List<string>();
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install() {
            var args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, "-p2ContinuousPerformance");
            if (i < 0 || i + 1 >= args.Length) return;
            Application.runInBackground=true;
            var p = new GameObject("Temporary run performance").AddComponent<P2ContinuousPerformance>(); p.output = args[i + 1]; Directory.CreateDirectory(p.output);
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void OnDisable() { Application.logMessageReceived -= Log; }
        void Log(string m, string s, LogType t) { if (t == LogType.Error || t == LogType.Exception) errors.Add(m); }
        IEnumerator Start() {
            var motor = FindAnyObjectByType<P2Motor>(); var input = motor.GetComponent<P2RunInput>();
            input.keyboardEnabled = false; input.SetRunning(false);
            yield return new WaitForSecondsRealtime(5);
            foreach (string name in new[] { "walk-continuous", "run-continuous", "crossing-walk", "crossing-run" }) {
                if(name=="crossing-walk") {
                    motor.Walk(P2World.Instance.courtyardGate);float deadline=Time.realtimeSinceStartup+15;
                    while((P2World.Instance.Zone!=1 || P2World.Instance.Busy) && Time.realtimeSinceStartup<deadline)yield return null;
                    if(P2World.Instance.Zone!=1){errors.Add("Crossing performance entry failed");break;}
                    yield return new WaitForSecondsRealtime(2);
                }
                bool crossing=name.StartsWith("crossing");
                Vector3 destination=crossing?new Vector3(-2,1.6f,-9.2f):new Vector3(4,0,6.7f);
                motor.ResetPosition(); input.SetRunning(name.Contains("run"));
                motor.Walk(destination);
                var samples = new List<float>(); float start = Time.realtimeSinceStartup, distance = 0, peak = 0; int unfocused = 0; bool outbound = true;
                while (Time.realtimeSinceStartup - start < 12) {
                    if (!motor.IsWalking) { outbound = !outbound; motor.Walk(outbound ? destination : motor.home); }
                    yield return null;
                    samples.Add(Time.unscaledDeltaTime); distance += motor.Distance; peak = Mathf.Max(peak, motor.Speed); if (!Application.isFocused) unfocused++;
                }
                var sorted = samples.OrderBy(x => x).ToArray();
                stages.Add(new Stage { name = name, frames = samples.Count, unfocused = unfocused, fps = samples.Count / samples.Sum(), p95Ms = sorted[(int)((sorted.Length - 1) * .95f)] * 1000, distance = distance, peakSpeed = peak });
            }
            File.WriteAllText(Path.Combine(output, "run-performance.json"), JsonUtility.ToJson(new Report { device = SystemInfo.graphicsDeviceName,
                width = Screen.width, height = Screen.height, stages = stages.ToArray(), errors = errors.ToArray() }, true));
            Application.Quit(errors.Count == 0 ? 0 : 1);
        }
    }
}
