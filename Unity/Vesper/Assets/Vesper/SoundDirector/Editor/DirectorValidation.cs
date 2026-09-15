using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Vesper.SoundDirector.Editor {
    public static class DirectorValidation {
        [Serializable] sealed class Report {
            public string scope = "Real Unity scene/asset transactions and planner contract tests using an injected fake HTTP transport. No live model call.";
            public string unityVersion;
            public bool liveAIValidated = false;
            public int failures;
            public string[] checks;
        }
        static readonly List<string> checks = new List<string>();
        static int failures;
        static void Check(bool value, string message) { checks.Add((value ? "PASS " : "FAIL ") + message); if (!value) failures++; }
        static void Throws(Action action, string message) { bool threw = false; try { action(); } catch { threw = true; } Check(threw, message); }
        static DirectionPlan Clone(DirectionPlan plan) => JsonUtility.FromJson<DirectionPlan>(JsonUtility.ToJson(plan));
        public static void PrepareAndValidateBatch() {
            try {
                checks.Clear(); failures = 0;
                Directory.CreateDirectory("../../Audio/Director");
                EditorSceneManager.OpenScene(DirectorScene.W11); DirectorScene.PrepareCurrent();
                var player = DirectorScene.Player();
                var catalog = SoundCatalog.Load(); var snapshot = DirectorScene.Capture();
                var fixture = DirectorExamples.Create(snapshot, true);
                Check(snapshot.targets.Length == 7, "W11 has six authored regions and the actual water emitter");
                Check(catalog.sounds.Length == 23 && catalog.sounds.Sum(s => s.files.Length) == 76, "Catalog covers all 76 existing WAVs in 23 pools");
                Check(catalog.sounds.Count(s => s.available) == 17, "17 environment pools are executable; footsteps and unsynchronized thunder are excluded");
                Check(DirectorRules.Validate(fixture.plan, snapshot, catalog).Length == 0, "Rehearsal plan is valid and explicitly labeled as non-AI");
                Check(fixture.source.Contains("Example") && fixture.model == "authored-fixture", "Rehearsal provenance is explicit");
                Action<Action<DirectionPlan>, string> invalid = (edit, message) => { var plan = Clone(fixture.plan); edit(plan); Check(DirectorRules.Validate(plan, snapshot, catalog).Length > 0, message); };
                invalid(p => p.layers[0].soundId = "invented_dragon", "Reject hallucinated sound ID");
                invalid(p => p.layers[0].soundId = "footstep_rock", "Reject requests that change preserved footsteps");
                invalid(p => p.layers[0].soundId = "thunder", "Reject unsynchronized thunder");
                invalid(p => p.layers[0].targetId = "missing-target", "Reject unknown scene target");
                invalid(p => p.layers[0].gainDb = 12, "Reject unsafe gain");
                invalid(p => p.layers[0].gainDb = float.NaN, "Reject nonfinite gain");
                invalid(p => p.layers[0].radius = 0, "Reject zero radius");
                invalid(p => p.layers[0].fadeSeconds = -1, "Reject negative fade");
                invalid(p => p.layers[0].intervalSeconds = 0, "Reject unbounded one-shot rate");
                invalid(p => p.layers = p.layers.Concat(new[] { p.layers[0] }).ToArray(), "Reject duplicate target/sound layer");
                invalid(p => p.layers = Array.Empty<DirectionLayer>(), "Reject empty plan");
                invalid(p => p.sceneRevision = "old", "Reject stale scene revision");
                invalid(p => p.version = 2, "Reject unknown protocol version");
                invalid(p => p.layers[0].reason = "", "Require per-layer rationale");
                Check(DirectorRules.DistanceGain(0, 10) == 1 && DirectorRules.DistanceGain(10, 10) == 0 && DirectorRules.DistanceGain(100, 10) == 0,
                    "Spatial envelope is full at center and silent at/beyond radius");
                Check(DirectorRules.DistanceGain(4, 10) > DirectorRules.DistanceGain(8, 10), "Spatial envelope falls off monotonically");
                Check(DirectorRules.Db(0) == -96 && Mathf.Abs(DirectorRules.Db(.5f) + 6.0206f) < .001f, "Amplitude to Wwise dB conversion");
                TestPlanner(snapshot, catalog, fixture.plan);
                Check(DirectorReview.Preflight(snapshot, fixture.plan, true).Length == 0, "Mac/Windows Director event banks and scene references pass preflight");
                string original = JsonUtility.ToJson(player.profile.plan);
                string footProfile = File.ReadAllText("Assets/Vesper/Expansion/WeatherW11/W11AudioProfile.asset");
                string oldSource = player.profile.source;
                var targetObject = player.SceneTargets()[0]; var originalPosition = targetObject.transform.position;
                targetObject.transform.position += Vector3.right;
                Throws(() => DirectorReview.Apply(fixture), "Applying after a target moved is rejected");
                Check(JsonUtility.ToJson(player.profile.plan) == original, "Rejected transaction does not mutate profile");
                targetObject.transform.position = originalPosition;
                DirectorReview.Apply(fixture);
                Check(player.profile.source == fixture.source && player.profile.plan.layers.Length == fixture.plan.layers.Length, "Apply saves the full reviewed plan and provenance");
                Check(DirectorReview.WriteReport().passed, "Applied plan passes static validation");
                DirectorReview.Restore();
                Check(JsonUtility.ToJson(player.profile.plan) == original && player.profile.source == oldSource, "Restore recovers previous plan and provenance");
                Check(File.ReadAllText("Assets/Vesper/Expansion/WeatherW11/W11AudioProfile.asset") == footProfile, "Original footstep/time/weather profile is byte-for-byte unchanged");
                snapshot = DirectorScene.Capture(); DirectorReview.Apply(DirectorExamples.Create(snapshot, true));
                EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
                File.WriteAllText("../../Audio/Director/w11-scene.json", JsonUtility.ToJson(snapshot, true));
                DirectorScene.OpenLab();
                DirectorScene.PrepareCurrent();
                var lab = DirectorScene.Capture();
                Check(lab.targets.Length == 3, "Independent lab discovers pond, grove and ruins from actual object names");
                Check(lab.targets.All(t => !snapshot.targets.Any(w => w.id == t.id)), "Second scene uses its own stable target IDs");
                Check(DirectorRules.Validate(fixture.plan, lab, catalog).Length > 0, "A W11 plan cannot be applied to a different scene");
                var labPlan = DirectorExamples.Create(lab, true);
                Check(DirectorRules.Validate(labPlan.plan, lab, catalog).Length == 0, "Same planner contract and executor support the second scene");
                DirectorReview.Apply(labPlan); EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
                File.WriteAllText("../../Audio/Director/lab-scene.json", JsonUtility.ToJson(lab, true));
                // Leave the main playable world ready, with clear rehearsal provenance.
                EditorSceneManager.OpenScene(DirectorScene.W11); AssetDatabase.SaveAssets();
                File.WriteAllText("../../Audio/Director/editor-validation.json", JsonUtility.ToJson(new Report {
                    unityVersion = Application.unityVersion, failures = failures, checks = checks.ToArray() }, true));
                Debug.Log("DIRECTOR_EDITOR_CHECKS " + checks.Count + " checks / " + failures + " failures");
                EditorApplication.Exit(failures == 0 ? 0 : 1);
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
        static void TestPlanner(DirectorSnapshot snapshot, SoundCatalog catalog, DirectionPlan plan) {
            string wire = "{\"status\":\"completed\",\"model\":\"contract-fixture\",\"output\":[{\"type\":\"message\",\"content\":[{\"type\":\"output_text\",\"text\":" + DirectorPlanner.Quote(JsonUtility.ToJson(plan)) + "}]}]}";
            var parsed = DirectorPlanner.ParseResponse(wire, out string model);
            Check(DirectorRules.Validate(parsed, snapshot, catalog).Length == 0 && model == "contract-fixture", "Parse structured Responses wire envelope");
            Throws(() => DirectorPlanner.ParseResponse("{\"status\":\"incomplete\"}", out _), "Reject incomplete model response");
            Throws(() => DirectorPlanner.ParseResponse("{\"status\":\"completed\",\"output\":[{\"type\":\"message\",\"content\":[{\"type\":\"refusal\",\"refusal\":\"test\"}]}]}", out _), "Handle model refusal without applying a plan");
            Throws(() => DirectorPlanner.ParseResponse("{\"status\":\"completed\",\"output\":[]}", out _), "Reject completed response without output text");
            string prompt = "물소리만 \"가까이\"\n나머지는 그대로. `literal` \\ 한글";
            var request = DirectorPlanner.BuildRequest(prompt, snapshot, catalog, DirectorPlanner.DefaultModel);
            File.WriteAllText("../../Audio/Director/request-contract.json", request);
            Check(!request.Contains("Bearer") && request.Contains("\"store\":false"), "API request body contains no credential and disables response storage");
            int calls = 0;
            Func<string, string, CancellationToken, Task<string>> transport = (body, key, token) => { calls++; return Task.FromResult(wire); };
            var result = DirectorPlanner.Generate(prompt, snapshot, catalog, DirectorPlanner.DefaultModel, "unit-test-placeholder", CancellationToken.None, transport).GetAwaiter().GetResult();
            Check(calls == 1 && result.attempts == 1 && result.plan.layers.Length == plan.layers.Length, "Planner uses validated HTTP response, not a keyword preset");
            var bad = Clone(plan); bad.layers[0].gainDb = 10;
            string badWire = wire.Replace(DirectorPlanner.Quote(JsonUtility.ToJson(plan)), DirectorPlanner.Quote(JsonUtility.ToJson(bad)));
            calls = 0; bool feedback = false;
            transport = (body, key, token) => { calls++; feedback |= body.Contains("previous plan was rejected"); return Task.FromResult(calls == 1 ? badWire : wire); };
            result = DirectorPlanner.Generate(prompt, snapshot, catalog, DirectorPlanner.DefaultModel, "unit-test-placeholder", CancellationToken.None, transport).GetAwaiter().GetResult();
            Check(calls == 2 && result.attempts == 2 && feedback, "Invalid numeric plan triggers one bounded repair request with validator feedback");
            calls = 0;
            transport = (body, key, token) => { calls++; return Task.FromResult(badWire); };
            Throws(() => DirectorPlanner.Generate(prompt, snapshot, catalog, DirectorPlanner.DefaultModel, "unit-test-placeholder", CancellationToken.None, transport).GetAwaiter().GetResult(), "Two invalid responses fail without a fake successful fallback");
            Check(calls == 2, "Repair loop has a strict two-call limit");
            calls = 0;
            using (var cancel = new CancellationTokenSource()) {
                cancel.Cancel();
                Throws(() => DirectorPlanner.Generate(prompt, snapshot, catalog, DirectorPlanner.DefaultModel, "unit-test-placeholder", cancel.Token, transport).GetAwaiter().GetResult(), "Canceled request cannot apply a result");
                Check(calls == 0, "Already canceled request does not contact the provider");
            }
            Throws(() => DirectorPlanner.Generate(prompt, snapshot, catalog, DirectorPlanner.DefaultModel, "", CancellationToken.None, transport).GetAwaiter().GetResult(), "Missing API key is an explicit error");
        }
        public static void RunPlaybackBatch() {
            try {
                bool lab = Environment.GetCommandLineArgs().Contains("-directorLab");
                EditorSceneManager.OpenScene(lab ? DirectorScene.Lab : DirectorScene.W11);
                EditorApplication.EnterPlaymode();
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
        public static void BuildWindowsBatch() {
            try {
                EditorSceneManager.OpenScene(DirectorScene.W11);
                Directory.CreateDirectory("Builds/VesperSoundDirector");
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { DirectorScene.W11 }, target = BuildTarget.StandaloneWindows64,
                    locationPathName = "Builds/VesperSoundDirector/VesperDirector.exe", options = BuildOptions.StrictMode
                });
                bool success = report.summary.result == UnityEditor.Build.Reporting.BuildResult.Succeeded;
                Debug.Log("DIRECTOR_WINDOWS_BUILD " + report.summary.result);
                EditorApplication.Exit(success ? 0 : 1);
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
        public static void RunOriginalRegressionBatch() {
            try {
                EditorSceneManager.OpenScene(DirectorScene.W11);
                DirectorScene.Player().gameObject.SetActive(false);
                EditorApplication.EnterPlaymode();
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
    }
}
