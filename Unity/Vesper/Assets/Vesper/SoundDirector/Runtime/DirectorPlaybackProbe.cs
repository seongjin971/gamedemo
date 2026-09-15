#if UNITY_EDITOR
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using W10 = Vesper.Expansion.WeatherW10;

namespace Vesper.SoundDirector {
    // Opt-in real Wwise integration test; never runs for a normal player or editor session.
    public sealed class DirectorPlaybackProbe : MonoBehaviour {
        [Serializable] sealed class Report {
            public string scope = "Real Unity Editor + native Wwise: bank loading, events, per-object RTPC, A/B and isolated water distance captures. No live AI call or human listening.";
            public string scene, unityVersion;
            public int failures, postedEvents;
            public string[] checks, errors, captures;
        }
        readonly List<string> checks = new List<string>(), errors = new List<string>(), captures = new List<string>();
        int failures;
        string output;
        SoundDirectorPlayer player;
        SoundDirectionProfile original, temporary;
        float deadline;
        bool finished, capturing;
#if VESPER_WWISE
        bool previousSuspend;
#endif
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Install() {
            var args = Environment.GetCommandLineArgs(); int index = Array.IndexOf(args, "-directorQA");
            if (index < 0) return;
            if (index + 1 >= args.Length) { EditorApplication.Exit(1); return; }
            var probe = new GameObject("Director playback verification").AddComponent<DirectorPlaybackProbe>();
            probe.output = Path.GetFullPath(args[index + 1]); probe.deadline = Time.realtimeSinceStartup + 90;
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void Log(string message, string stack, LogType type) { if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) errors.Add(message); }
        void Check(bool pass, string message) { checks.Add((pass ? "PASS " : "FAIL ") + message); if (!pass) failures++; }
        void Update() { if (!finished && output != null && Time.realtimeSinceStartup > deadline) { Check(false, "Playback probe completed before timeout"); Finish(); } }
        IEnumerator Start() {
            player = UnityEngine.Object.FindAnyObjectByType<SoundDirectorPlayer>();
            if (!player) { Check(false, "Director player exists"); Finish(); yield break; }
            original = player.profile;
            float until = Time.realtimeSinceStartup + 22;
            while (!player.Ready && Time.realtimeSinceStartup < until) yield return null;
            Check(player.Ready && player.ErrorCount == 0, "Native Wwise initialized and all Director loops posted");
            if (!player.Ready) { Finish(); yield break; }
#if VESPER_WWISE
            previousSuspend = AkWwiseInitializationSettings.ActivePlatformSettings.SuspendAudioDuringFocusLoss;
            AkWwiseInitializationSettings.ActivePlatformSettings.SuspendAudioDuringFocusLoss = false;
            AkUnitySoundEngine.WakeupFromSuspend();
            Check(player.LayerCount == original.plan.layers.Length, "Every planned layer has its own registered emitter");
            player.useDirection = true; yield return new WaitForSecondsRealtime(3);
            Check(player.Mix == 1, "B audition reaches full direction mix");
            int before = player.PostedEvents;
            yield return Capture("full-direction", 3);
            player.useDirection = false; yield return new WaitForSecondsRealtime(1.2f);
            Check(player.Mix == 0, "A audition restores original ambience");
            int kind = 2; // AK::Query::RTPCValue_GameObject (1 would read the global/default value).
            var result = AkUnitySoundEngine.GetRTPCValue("SD_Gain", player.LayerEmitter(0), 0, out float gain, ref kind);
            Check(result == AKRESULT.AK_Success && gain <= -95, "A audition actually mutes Director output in Wwise");
            Check(player.PostedEvents == before, "A/B switching does not repost continuous loops");
            if (player.existingAudio) {
                Check(player.existingAudio.Ready && player.existingAudio.ErrorCount == 0, "Existing footsteps and weather bridge remain healthy");
                yield return Capture("original", 2);
            }
            var water = original.plan.layers.First(l => l.soundId == "river");
            temporary = UnityEngine.Object.Instantiate(original);
            temporary.plan = JsonUtility.FromJson<DirectionPlan>(JsonUtility.ToJson(original.plan));
            temporary.plan.layers = new[] { new DirectionLayer { targetId = water.targetId, soundId = "river", gainDb = -8,
                radius = 20, fadeSeconds = .25f, intervalSeconds = 30, reason = "isolated real-audio distance test" } };
            player.profile = temporary; player.useDirection = true; player.Reload();
            until = Time.realtimeSinceStartup + 10; while (!player.Ready && Time.realtimeSinceStartup < until) yield return null;
            Check(player.Ready && player.LayerCount == 1, "A second valid plan reloads as a single isolated water layer");
            if (!player.Ready) { Finish(); yield break; }
            var target = player.SceneTargets().First(t => t.id == water.targetId);
            if (player.existingAudio) {
                var motor = player.existingAudio.state.motor; motor.Stop(); motor.transform.position = W10.WorldLayout.Point(25);
            } else player.listener.position = target.transform.position + Vector3.up * 2;
            yield return new WaitForSecondsRealtime(2);
            kind = 2; result = AkUnitySoundEngine.GetRTPCValue("SD_Gain", player.LayerEmitter(0), 0, out gain, ref kind);
            Check(result == AKRESULT.AK_Success && gain > -30, "Near water: real per-emitter RTPC is audible; " + result + ", " + gain + " dB, distance " + Vector3.Distance(player.listener.position, target.transform.position) + ", envelope " + player.LayerEnvelope(0) + ", mix " + player.Mix);
            yield return Capture("water-near", 3);
            if (player.existingAudio) {
                var motor = player.existingAudio.state.motor; motor.Stop(); motor.transform.position = W10.WorldLayout.Point(140);
            } else player.listener.position = target.transform.position + Vector3.right * 50 + Vector3.up * 2;
            yield return new WaitForSecondsRealtime(2);
            kind = 2; result = AkUnitySoundEngine.GetRTPCValue("SD_Gain", player.LayerEmitter(0), 0, out gain, ref kind);
            Check(result == AKRESULT.AK_Success && gain <= -95, "Beyond water radius: real per-emitter RTPC reaches silence");
            yield return Capture("water-far", 2);
            player.enabled = false; yield return null;
            Check(!player.Ready && player.LayerCount == 0, "Disabling releases owned voices and restores baseline");
            player.profile = original; player.enabled = true;
            until = Time.realtimeSinceStartup + 10; while (!player.Ready && Time.realtimeSinceStartup < until) yield return null;
            Check(player.Ready && player.LayerCount == original.plan.layers.Length && player.ErrorCount == 0, "Re-enable rebuilds the plan without duplicate voices or Wwise errors");
#else
            Check(false, "Wwise SDK is enabled");
#endif
            Finish();
        }
        IEnumerator Capture(string suffix, float seconds) {
#if VESPER_WWISE
            string path = Path.ChangeExtension(output, null) + "-" + suffix + ".wav";
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var result = AkUnitySoundEngine.StartOutputCapture(path);
            capturing = result == AKRESULT.AK_Success;
            Check(capturing, "Start real Wwise output capture: " + suffix);
            if (capturing) {
                yield return new WaitForSecondsRealtime(seconds);
                AkUnitySoundEngine.StopOutputCapture(); capturing = false; captures.Add(path);
            }
#else
            yield return null;
#endif
        }
        void Finish() {
            if (finished) return; finished = true;
#if VESPER_WWISE
            if (capturing) AkUnitySoundEngine.StopOutputCapture();
            AkWwiseInitializationSettings.ActivePlatformSettings.SuspendAudioDuringFocusLoss = previousSuspend;
#endif
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            File.WriteAllText(output, JsonUtility.ToJson(new Report { scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().path,
                unityVersion = Application.unityVersion, failures = failures, postedEvents = player ? player.PostedEvents : 0,
                checks = checks.ToArray(), errors = errors.ToArray(), captures = captures.ToArray() }, true));
            Debug.Log("DIRECTOR_PLAYBACK_CHECKS " + checks.Count + " checks / " + failures + " failures / " + errors.Count + " errors");
            int code = failures == 0 && errors.Count == 0 ? 0 : 1;
            EditorApplication.CallbackFunction exit = null;
            exit = () => { if (EditorApplication.isPlayingOrWillChangePlaymode) return; EditorApplication.update -= exit; EditorApplication.Exit(code); };
            EditorApplication.update += exit; EditorApplication.ExitPlaymode();
        }
        void OnDisable() {
            Application.logMessageReceived -= Log;
            if (player && original) player.profile = original;
            if (temporary) Destroy(temporary);
        }
    }
}
#endif
