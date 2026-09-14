using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using W10 = Vesper.Expansion.WeatherW10;

namespace Vesper.Expansion.WeatherW11.Editor {
    public static class WeatherW11Setup {
        public const string ScenePath = "Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W11.unity";
        public const string ProfilePath = "Assets/Vesper/Expansion/WeatherW11/W11AudioProfile.asset";
        const string SourceScene = "Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W10.unity";

        [MenuItem("Vesper/W11 Audio/1 Prepare or Open Scene")]
        public static void Prepare() {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            if (File.Exists(ScenePath)) { EditorSceneManager.OpenScene(ScenePath); ValidateScene(); return; }
            if (!AssetDatabase.CopyAsset(SourceScene, ScenePath)) throw new InvalidOperationException("Could not copy W10 scene.");
            var scene = EditorSceneManager.OpenScene(ScenePath);
            var motor = UnityEngine.Object.FindAnyObjectByType<W10.WorldMotor>();
            var environment = UnityEngine.Object.FindAnyObjectByType<W10.WorldEnvironment>();
            var animation = UnityEngine.Object.FindAnyObjectByType<W10.WorldAnimation>();
            if (!motor || !environment || !animation) throw new InvalidOperationException("W10 game components were not found.");
            var profile = AssetDatabase.LoadAssetAtPath<WorldAudioProfile>(ProfilePath);
            if (!profile) { profile = ScriptableObject.CreateInstance<WorldAudioProfile>(); AssetDatabase.CreateAsset(profile, ProfilePath); }
            var root = new GameObject("W11 Audio");
            var state = root.AddComponent<WorldAudioState>();
            state.motor = motor; state.environment = environment; state.profile = profile;
            var feet = root.AddComponent<WorldFootsteps>();
            feet.state = state; feet.animationSource = animation;
            feet.leftFoot = FindFoot(animation.animator.transform, "LeftFoot");
            feet.rightFoot = FindFoot(animation.animator.transform, "RightFoot");
            var bridge = root.AddComponent<WwiseAudioBridge>();
            bridge.state = state; bridge.footsteps = feet;
            bridge.playerEmitter = Child("Player Audio Emitter", motor.transform);
            bridge.ambienceEmitter = Child("World Ambience Emitter", root.transform);
            bridge.lakeEmitter = Child("Lake Ambience Emitter", root.transform);
            // Surveyed W10: bridge spans the water at world z=-25; river level is -0.55.
            bridge.lakeEmitter.transform.position = new Vector3(0, W10.WorldLayout.WaterHeight, -25);
            bridge.listener = Child("Player Audio Listener", root.transform);
            var follow = bridge.listener.AddComponent<WorldAudioListener>();
            follow.player = motor.transform; follow.view = Camera.main;
            bridge.listener.transform.position = motor.transform.position + Vector3.up;
            if (Camera.main) bridge.listener.transform.rotation = Camera.main.transform.rotation;
            var deck = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true))
                .FirstOrDefault(t => t.name == "Linear bridge deck");
            if (!deck) throw new InvalidOperationException("The surveyed stone bridge collider is missing.");
            deck.gameObject.AddComponent<SurfaceAudioTag>().surface = SurfaceType.Rock;
            var debug = root.AddComponent<WorldAudioDebug>(); debug.state = state; debug.footsteps = feet; debug.bridge = bridge;
            Calibrate(animation, profile);
            ConnectComponents(bridge);
            EditorUtility.SetDirty(profile); AssetDatabase.SaveAssets(); EditorSceneManager.SaveScene(scene);
            Debug.Log("Created W11 audio scene. Original W10 assets and controls are referenced without modification.");
        }

        static GameObject Child(string name, Transform parent) {
            var go = new GameObject(name); go.transform.SetParent(parent, false); return go;
        }
        static Transform FindFoot(Transform root, string suffix) {
            return root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name.EndsWith(suffix, StringComparison.OrdinalIgnoreCase));
        }
        static void Calibrate(W10.WorldAnimation source, WorldAudioProfile profile) {
            if (!source.animator || !source.walkClip || !source.runClip) return;
            var clone = UnityEngine.Object.Instantiate(source.animator.gameObject);
            clone.name = "Temporary W11 contact calibration"; clone.hideFlags = HideFlags.HideAndDontSave;
            clone.SetActive(false);
            try {
                var left = FindFoot(clone.transform, "LeftFoot"); var right = FindFoot(clone.transform, "RightFoot");
                if (!left || !right) { Debug.LogWarning("Foot bones not found: contact phases need manual calibration."); return; }
                profile.leftWalkContact = LowestPhase(source.walkClip, clone, left);
                profile.rightWalkContact = LowestPhase(source.walkClip, clone, right);
                profile.leftRunContact = LowestPhase(source.runClip, clone, left);
                profile.rightRunContact = LowestPhase(source.runClip, clone, right);
                profile.contactsCalibrated = true;
            } finally { UnityEngine.Object.DestroyImmediate(clone); }
        }
        static float LowestPhase(AnimationClip clip, GameObject rig, Transform foot) {
            float min = float.PositiveInfinity, phase = 0;
            for (int i = 0; i < 120; i++) {
                float sample = i / 120f; clip.SampleAnimation(rig, sample * clip.length);
                float height = rig.transform.InverseTransformPoint(foot.position).y;
                if (height < min) { min = height; phase = sample; }
            }
            return phase;
        }

        [MenuItem("Vesper/W11 Audio/Recalibrate Foot Contacts")]
        public static void RecalibrateContacts() {
            if (SceneManager.GetActiveScene().path != ScenePath) throw new InvalidOperationException("Open W11 first.");
            var source = UnityEngine.Object.FindAnyObjectByType<W10.WorldAnimation>();
            var profile = AssetDatabase.LoadAssetAtPath<WorldAudioProfile>(ProfilePath);
            if (!source || !profile) throw new InvalidOperationException("W11 animation or profile is missing.");
            Calibrate(source, profile); EditorUtility.SetDirty(profile); AssetDatabase.SaveAssets();
        }

        [MenuItem("Vesper/W11 Audio/2 Enable Wwise SDK")]
        public static void EnableSdk() {
            if (!AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetType("AkUnitySoundEngine") != null))
                throw new InvalidOperationException("Install the official Wwise Unity Integration before enabling this feature.");
            var target = NamedBuildTarget.Standalone;
            var symbols = PlayerSettings.GetScriptingDefineSymbols(target).Split(';').Where(s => !string.IsNullOrWhiteSpace(s)).ToList();
            if (!symbols.Contains("VESPER_WWISE")) { symbols.Add("VESPER_WWISE"); PlayerSettings.SetScriptingDefineSymbols(target, string.Join(";", symbols)); }
            Debug.Log("Wwise enabled. After compilation, use '3 Connect Wwise Components'.");
        }

        [MenuItem("Vesper/W11 Audio/3 Connect Wwise Components")]
        public static void Connect() {
            if (SceneManager.GetActiveScene().path != ScenePath) throw new InvalidOperationException("Open W11 first.");
            var bridge = UnityEngine.Object.FindAnyObjectByType<WwiseAudioBridge>();
            if (!bridge) throw new InvalidOperationException("Prepare W11 first.");
#if !VESPER_WWISE
            throw new InvalidOperationException("Enable the installed Wwise SDK and wait for compilation first.");
#else
            ConnectComponents(bridge); EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
#endif
        }
        static void ConnectComponents(WwiseAudioBridge bridge) {
#if VESPER_WWISE
            if (!UnityEngine.Object.FindAnyObjectByType<AkInitializer>()) bridge.gameObject.AddComponent<AkInitializer>();
            foreach (var emitter in new[] { bridge.playerEmitter, bridge.ambienceEmitter, bridge.lakeEmitter, bridge.listener })
                if (!emitter.GetComponent<AkGameObj>()) emitter.AddComponent<AkGameObj>();
            foreach (var other in UnityEngine.Object.FindObjectsByType<AkAudioListener>(FindObjectsSortMode.None))
                if (other.gameObject != bridge.listener) UnityEngine.Object.DestroyImmediate(other);
            if (!bridge.listener.GetComponent<AkAudioListener>()) bridge.listener.AddComponent<AkAudioListener>();
#endif
        }

        [MenuItem("Vesper/W11 Audio/4 Build Windows Player")]
        public static void BuildWindows() {
            ValidateBanks("Windows");
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Standalone, BuildTarget.StandaloneWindows64))
                throw new InvalidOperationException("Install Windows Build Support for this Unity Editor.");
            Directory.CreateDirectory("Builds/VesperWeatherWorld_W11");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { ScenePath }, target = BuildTarget.StandaloneWindows64,
                locationPathName = "Builds/VesperWeatherWorld_W11/VesperAudio.exe", options = BuildOptions.StrictMode
            });
            if (report.summary.result != BuildResult.Succeeded) throw new InvalidOperationException("W11 build failed: " + report.summary.result);
        }
        public static void ValidateBanks(string platform) {
#if !VESPER_WWISE
            throw new BuildFailedException("W11 sound build requires the Wwise SDK. The no-SDK editor mode is a state preview only.");
#else
            var profile = AssetDatabase.LoadAssetAtPath<WorldAudioProfile>(ProfilePath);
            if (!profile || !profile.Validate(out _)) throw new BuildFailedException("Invalid W11 audio profile.");
            string dir = "Assets/StreamingAssets/Audio/GeneratedSoundBanks/" + platform;
            foreach (var name in new[] { "Init", profile.bankName })
                if (!File.Exists(dir + "/" + name + ".bnk")) throw new BuildFailedException("Missing bank: " + dir + "/" + name + ".bnk");
#endif
        }

        public static void PrepareBatch() {
            try { Prepare(); ValidateScene(); EditorApplication.Exit(0); }
            catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
        public static void ValidateScene() {
            var scene = SceneManager.GetActiveScene();
            if (scene.path != ScenePath) throw new InvalidOperationException("W11 is not open.");
            var all = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
            foreach (var t in all) if (GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject) != 0)
                throw new InvalidOperationException("Missing script: " + t.name);
            var bridge = UnityEngine.Object.FindAnyObjectByType<WwiseAudioBridge>();
            if (!bridge || !bridge.state || !bridge.footsteps || !bridge.playerEmitter || !bridge.lakeEmitter || !bridge.listener)
                throw new InvalidOperationException("Incomplete audio references.");
            if (!bridge.state.profile.Validate(out var error)) throw new InvalidOperationException(error);
            Debug.Log("W11 scene references validated. Wwise playback is a separate runtime check.");
        }
    }

    public sealed class WeatherW11BuildGuard : IProcessSceneWithReport {
        public int callbackOrder => 0;
        public void OnProcessScene(Scene scene, BuildReport report) {
            if (report == null || scene.path != WeatherW11Setup.ScenePath) return;
            WeatherW11Setup.ValidateBanks(report.summary.platform == BuildTarget.StandaloneWindows64 ? "Windows" : "Mac");
        }
    }
}
