#if UNITY_EDITOR
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using W10 = Vesper.Expansion.WeatherW10;

namespace Vesper.Expansion.WeatherW11 {
    // Explicit batch-only probe. It exercises the real scene, navigation and animation;
    // it does not establish that Wwise received events or produced audible output.
    public sealed class WeatherW11StateProbe : MonoBehaviour {
        [Serializable] public class Sample {
            public float progress, timeOfDay, rainIntensity;
            public string surface, area;
            public bool grounded;
        }
        [Serializable] public class Report {
            public string scope = "Unity Editor Play Mode at a controlled 60 Hz simulation step: game-state inputs and foot contacts; no audible playback or rendering verification";
            public string unityVersion;
            public int failures, walkContacts, runContacts;
            public float[] calibratedPhases;
            public string[] checks, errors;
            public Sample[] samples;
            public Movement[] movements;
        }
        [Serializable] public class Movement {
            public bool running;
            public Vector3 finalPosition;
            public float target, maxRunBlend;
            public int safetyStops;
            public string lastReject;
            public float[] contactTimes;
        }
        readonly List<string> checks = new List<string>(), errors = new List<string>();
        readonly List<Sample> samples = new List<Sample>();
        readonly List<Movement> movements = new List<Movement>();
        readonly List<float> contactTimes = new List<float>();
        readonly List<SurfaceType> contactSurfaces = new List<SurfaceType>();
        readonly Report report = new Report();
        WorldAudioState state;
        WorldFootsteps feet;
        WwiseAudioBridge bridge;
        W10.WorldMotor motor;
        W10.WorldRunInput run;
        W10.WorldCamera cameraControl;
        string output;
        float deadline;
        bool finished;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Install() {
            var args = Environment.GetCommandLineArgs();
            int index = Array.IndexOf(args, "-w11StateQA");
            if (index < 0) return;
            if (index + 1 >= args.Length || args[index + 1].StartsWith("-", StringComparison.Ordinal)) {
                Debug.LogError("Missing -w11StateQA output path."); EditorApplication.Exit(1); return;
            }
            var probe = new GameObject("W11 state validation").AddComponent<WeatherW11StateProbe>();
            probe.output = Path.GetFullPath(args[index + 1]);
            Directory.CreateDirectory(Path.GetDirectoryName(probe.output));
            probe.deadline = Time.realtimeSinceStartup + 120;
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void OnDisable() {
            Application.logMessageReceived -= Log;
            if (feet) feet.Contact -= Contact;
        }
        void Log(string message, string stack, LogType type) {
            if (type == LogType.Error || type == LogType.Exception || type == LogType.Assert) errors.Add(message);
        }
        void Update() {
            if (!finished && output != null && Time.realtimeSinceStartup > deadline) {
                Check(false, "Probe completed within 120 seconds"); Finish();
            }
        }
        void Contact(SurfaceType surface) { contactTimes.Add(Time.time); contactSurfaces.Add(surface); }
        void Check(bool ok, string message) {
            checks.Add((ok ? "PASS " : "FAIL ") + message);
            if (!ok) report.failures++;
        }
        void Finish() {
            if (finished) return;
            finished = true;
            report.unityVersion = Application.unityVersion;
            report.checks = checks.ToArray(); report.errors = errors.ToArray(); report.samples = samples.ToArray();
            report.movements = movements.ToArray();
            File.WriteAllText(output, JsonUtility.ToJson(report, true));
            Debug.Log($"W11 state probe: {checks.Count} checks, {report.failures} failures, {errors.Count} errors. {output}");
            EditorApplication.Exit(report.failures == 0 && errors.Count == 0 ? 0 : 1);
        }
        IEnumerator Place(float progress) {
            motor.Stop(); motor.transform.SetPositionAndRotation(W10.WorldLayout.Point(progress), Quaternion.Euler(0, 180, 0));
            Physics.SyncTransforms(); cameraControl.SnapToPlayer();
            yield return null; yield return null;
            state.Refresh();
        }
        IEnumerator SampleState(float progress, SurfaceType surface, AudioArea area) {
            yield return Place(progress);
            var value = state.Current;
            samples.Add(new Sample { progress = progress, surface = value.surface.ToString(), area = value.area.ToString(),
                grounded = value.grounded, timeOfDay = value.timeOfDay, rainIntensity = value.rainIntensity });
            Check(state.Valid && value.grounded, $"Ground support at {progress}m");
            Check(value.surface == surface && value.area == area, $"{surface}/{area} at {progress}m");
            Check(value.timeOfDay >= 0 && value.timeOfDay < 24 && value.rainIntensity >= 0 && value.rainIntensity <= 1,
                $"RTPC ranges at {progress}m");
        }
        IEnumerator Move(bool running, float target) {
            yield return Place(192);
            run.SetRunning(running);
            contactTimes.Clear(); contactSurfaces.Clear();
            int stops = motor.SafetyStops;
            bool accepted = motor.Walk(W10.WorldLayout.Point(target));
            Check(accepted, (running ? "Run" : "Walk") + " route accepted: " + motor.LastReject);
            float until = Time.realtimeSinceStartup + 20;
            float maxRunBlend = 0;
            while (motor.IsWalking && Time.realtimeSinceStartup < until) {
                yield return null;
                maxRunBlend = Mathf.Max(maxRunBlend, feet.animationSource.RunBlend);
            }
            movements.Add(new Movement { running = running, finalPosition = motor.transform.position, target = target,
                maxRunBlend = maxRunBlend, safetyStops = motor.SafetyStops - stops, lastReject = motor.LastReject,
                contactTimes = contactTimes.ToArray() });
            Check(Vector3.Distance(motor.transform.position, W10.WorldLayout.Point(target)) < .4f && motor.SafetyStops == stops,
                (running ? "Run" : "Walk") + " arrived on supported ground: " + motor.LastReject);
            if (running) Check(maxRunBlend > .5f, "Movement actually entered the run animation");
            int count = contactTimes.Count;
            if (running) report.runContacts = count; else report.walkContacts = count;
            Check(count >= 2 && count < 40, (running ? "Run" : "Walk") + " produces bounded foot contacts");
            Check(contactSurfaces.TrueForAll(s => s == SurfaceType.Rock), "Moving contacts use the abbey stone surface");
            bool distinct = true;
            for (int i = 1; i < count; i++) distinct &= contactTimes[i] - contactTimes[i - 1] > .06f;
            Check(distinct, "Left/right contacts occur at distinct instants");
            motor.Stop(); int stopped = feet.ContactCount;
            yield return new WaitForSecondsRealtime(.5f);
            Check(feet.ContactCount == stopped, "Stopping movement stops contact emission");
        }
        IEnumerator Start() {
            // Null graphics can otherwise run at thousands of FPS, where the inherited
            // motor's initial displacement rounds to zero at large world coordinates.
            Time.captureDeltaTime = 1f / 60;
            yield return null;
            state = FindAnyObjectByType<WorldAudioState>(); feet = FindAnyObjectByType<WorldFootsteps>();
            bridge = FindAnyObjectByType<WwiseAudioBridge>(); cameraControl = FindAnyObjectByType<W10.WorldCamera>();
            if (!state || !feet || !bridge || !cameraControl) { Check(false, "W11 runtime references exist"); Finish(); yield break; }
            motor = state.motor; run = motor.GetComponent<W10.WorldRunInput>();
            cameraControl.nativeInput = false; run.keyboardEnabled = false; feet.Contact += Contact;
            var p = state.profile;
            report.calibratedPhases = new[] { p.leftWalkContact, p.rightWalkContact, p.leftRunContact, p.rightRunContact };
            Check(p.contactsCalibrated && feet.leftFoot && feet.rightFoot, "Actual animation clips and foot bones calibrated");
            Check(Mathf.Abs(p.leftWalkContact - p.rightWalkContact) > .2f && Mathf.Abs(p.leftRunContact - p.rightRunContact) > .2f,
                "Left and right foot contacts have distinct phases");
            yield return SampleState(0, SurfaceType.Gravel, AudioArea.Forest);
            yield return SampleState(25, SurfaceType.Rock, AudioArea.Forest);
            Check(Vector3.Distance(bridge.lakeEmitter.transform.position, new Vector3(0, W10.WorldLayout.WaterHeight, -25)) < .01f,
                "Lake emitter remains at the surveyed water position");
            float distance = Vector3.Distance(bridge.listener.transform.position, bridge.lakeEmitter.transform.position);
            cameraControl.SetZoom(cameraControl.Zoom + 3);
            cameraControl.HandleKeys(false, true, false, 0, .05f);
            yield return new WaitForSecondsRealtime(.3f);
            Check(Mathf.Abs(Vector3.Distance(bridge.listener.transform.position, bridge.lakeEmitter.transform.position) - distance) < .001f &&
                Quaternion.Angle(bridge.listener.transform.rotation, cameraControl.transform.rotation) < .01f,
                "Camera zoom/orbit preserves player-based listener distance and follows camera orientation");
            yield return SampleState(150, SurfaceType.Mud, AudioArea.Forest);
            Check(state.Current.rainIntensity > .5f, "Rain grows in Rainwood");
            yield return SampleState(192, SurfaceType.Rock, AudioArea.Forest);
            Check(state.Current.rainIntensity > .99f, "Global rain remains active at the abbey");
            yield return SampleState(323, SurfaceType.Snow, AudioArea.SnowMountain);
            Check(state.Current.rainIntensity < .01f, "Rain clears in the snow region");
            yield return Place(270);
            Check(state.Current.area == AudioArea.SnowMountain, "Area stays SnowMountain inside hysteresis band");
            yield return Place(268);
            Check(state.Current.area == AudioArea.Forest, "Area returns to Forest past lower boundary");
            yield return Place(271);
            Check(state.Current.area == AudioArea.Forest, "Area stays Forest inside hysteresis band");
            yield return Place(273);
            Check(state.Current.area == AudioArea.SnowMountain, "Area enters SnowMountain past upper boundary");
            motor.ResetPosition(); Physics.SyncTransforms(); yield return null; yield return null;
            Check(state.Current.area == AudioArea.Forest && state.Current.rainIntensity == 0, "R reset refreshes area and weather");
            int idle = feet.ContactCount;
            yield return new WaitForSecondsRealtime(.5f);
            Check(feet.ContactCount == idle, "Idle animation does not emit footsteps");
            motor.transform.position += Vector3.up * 3; Physics.SyncTransforms(); yield return null; yield return null;
            Check(!state.Current.grounded, "No false ground support while airborne");
            yield return Move(false, 198);
            yield return Move(true, 204);
            Finish();
        }
    }
}
#endif
