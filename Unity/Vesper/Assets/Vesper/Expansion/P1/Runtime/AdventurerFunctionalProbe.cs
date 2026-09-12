using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Vesper.Expansion {
    public sealed class AdventurerFunctionalProbe : MonoBehaviour {
        [Serializable] class Report { public string note = "Automated commands to actual runtime components; not mouse/keyboard injection."; public string[] passed, errors; public float traveled; public int frames; }
        readonly List<string> passed = new List<string>(), errors = new List<string>();
        AdventurerMotor motor; AdventurerCamera camera; string output; int frames; float traveled;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Install() {
            var args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, "-p1FunctionalQA"); if (i < 0 || i + 1 >= args.Length) return;
            var p = new GameObject("P1 temporary functional verification").AddComponent<AdventurerFunctionalProbe>(); p.output = args[i + 1]; Directory.CreateDirectory(p.output);
        }
        void OnEnable() { Application.logMessageReceived += Log; }
        void OnDisable() { Application.logMessageReceived -= Log; }
        void Log(string message, string stack, LogType type) { if (type == LogType.Error || type == LogType.Exception) errors.Add(message); }
        void Check(bool value, string name) { if (value) passed.Add(name); else errors.Add(name); }
        void LateUpdate() { if (motor) { frames++; traveled += motor.Distance; } }
        IEnumerator Start() {
            motor = FindAnyObjectByType<AdventurerMotor>(); camera = Camera.main.GetComponent<AdventurerCamera>();
            var navigation = new VesperNavigation(); yield return new WaitForSecondsRealtime(2);
            Check(FindObjectsByType<AdventurerMotor>().Length == 1 && FindObjectsByType<VesperKnight>().Length == 0, "Exactly one P1 motor, no knight");
            Check(motor.GetComponentInChildren<SkinnedMeshRenderer>() && motor.GetComponentInChildren<Animator>(), "Skinned mesh and Animator present");
            foreach (var point in new[] { new Vector3(-3.08f, 0, 5.21f), new Vector3(3.4f, 0, 3.7f), new Vector3(4, 0, 6.7f), new Vector3(6, 0, 7.4f) }) {
                Check(motor.Walk(point), "Accept destination " + point);
                float start = Time.realtimeSinceStartup; bool clearance = true;
                while (motor.IsWalking && Time.realtimeSinceStartup - start < 16) { clearance &= navigation.Valid(motor.transform.position); yield return null; }
                Check(!motor.IsWalking && Vector3.Distance(motor.transform.position, point) < .5f, "Arrive " + point);
                Check(clearance, "Route preserves courtyard clearance " + point);
            }
            var before = motor.transform.position;
            Check(!motor.Walk(new Vector3(40, 0, 40)), "Reject outside courtyard");
            yield return new WaitForSecondsRealtime(.5f); Check(Vector3.Distance(before, motor.transform.position) < .001f, "Rejected command does not move player");
            motor.Walk(new Vector3(-3.08f, 0, 5.21f)); yield return new WaitForSecondsRealtime(.4f);
            Check(motor.Walk(new Vector3(3.4f, 0, 3.7f)), "Accept mid-walk destination change");
            camera.SetZoom(-20); camera.Orbit(-20, 20); yield return new WaitForSecondsRealtime(1);
            Check(Mathf.Abs(camera.Zoom - 7.5f) < .001f && camera.Angle >= -.051f && camera.Elevation <= 1.141f, "Close/rotation camera clamps");
            camera.SetZoom(40); camera.Orbit(40, -40); yield return new WaitForSecondsRealtime(1);
            Check(Mathf.Abs(camera.Zoom - 14) < .001f && camera.Angle <= 1.101f && camera.Elevation >= .479f, "Wide/rotation camera clamps");
            camera.ResetView(); yield return new WaitForSecondsRealtime(1);
            Check(Vector3.Distance(motor.home, motor.transform.position) < .001f && !motor.IsWalking, "R handler resets position and clears route");
            Check(Mathf.Abs(camera.Zoom - camera.homeSize) < .001f && Mathf.Abs(camera.Angle - .46f) < .01f, "R handler resets camera");
            File.WriteAllText(Path.Combine(output, "functional-report.json"), JsonUtility.ToJson(new Report { passed = passed.ToArray(), errors = errors.ToArray(), frames = frames, traveled = traveled }, true));
            Application.Quit();
        }
    }
}
