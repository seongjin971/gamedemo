#if UNITY_EDITOR && VESPER_WWISE
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Vesper.Expansion.WeatherW11.Editor {
    // Opt-in checks run on an isolated checkout, then start the existing real-engine probe.
    public static class VesperBootstrapValidation {
        [Serializable] sealed class Report {
            public string scope = "Fresh relocated checkout without Library or UserSettings; automatic setup, missing SDK define recovery, Authoring unavailable, followed by actual Wwise Play Mode validation";
            public string unityVersion;
            public string[] checks;
            public int failures;
        }
        static readonly List<string> checks = new List<string>();
        static void Check(bool ok, string message) {
            if (!ok) throw new InvalidOperationException(message);
            checks.Add("PASS " + message);
        }

        public static void ValidateAuthoringDiscoveryBatch() {
            try {
                var report = VesperProjectBootstrap.Apply();
                Check(report.ready, "Existing project remains ready after setup");
                Check(!string.IsNullOrEmpty(report.authoringPath) &&
                    VesperProjectBootstrap.ValidateAuthoring(report.authoringPath, VesperProjectBootstrap.IsMac) == report.authoringPath,
                    "Installed matching Authoring is discovered and version-checked");
                Check(AkWwiseEditorSettings.Instance.WwiseInstallationPath == report.authoringPath,
                    "Official Integration receives the local Authoring path");
                var xml = new XmlDocument { XmlResolver = null }; xml.Load(WwiseSettings.Path);
                Check(string.IsNullOrEmpty(xml.SelectSingleNode("/WwiseSettings/WwiseInstallationPathMac").InnerText) &&
                    string.IsNullOrEmpty(xml.SelectSingleNode("/WwiseSettings/WwiseInstallationPathWindows").InnerText),
                    "Authoring discovery leaves shared installation paths empty");
                var saved = File.ReadAllBytes(WwiseSettings.Path);
                var second = VesperProjectBootstrap.Apply();
                Check(second.ready && second.authoringPath == report.authoringPath && saved.SequenceEqual(File.ReadAllBytes(WwiseSettings.Path)),
                    "Repeated Authoring discovery preserves shared settings");
                var data = new Report { scope = "Installed Authoring discovery on " + Application.platform + "; no Authoring launch or Windows execution",
                    unityVersion = Application.unityVersion, checks = checks.ToArray(), failures = 0 };
                File.WriteAllText(Path.GetFullPath("../../Audio/authoring-discovery-validation.json"), JsonUtility.ToJson(data, true));
                EditorApplication.Exit(0);
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }

        public static void CompleteFreshClone() {
            try {
                Check(Environment.GetCommandLineArgs().Contains("-vesperNoAuthoring"), "Authoring discovery is disabled for the fresh-checkout test");
                var report = VesperProjectBootstrap.LastReport;
                Check(report != null && report.ready && report.errors.Length == 0, "Automatic post-import setup completes");
                Check(string.IsNullOrEmpty(report.authoringPath), "Gameplay setup succeeds without a Wwise Authoring executable");
                Check(PlayerSettings.GetScriptingDefineSymbols(UnityEditor.Build.NamedBuildTarget.Standalone).Split(';').Contains("VESPER_WWISE"), "SDK define is restored automatically after importing");
                Check(SceneManager.GetActiveScene().path == WeatherW11Setup.ScenePath, "Fresh project automatically opens W11");
                Check(File.Exists(VesperProjectBootstrap.WwiseProjectPath), "Relative Wwise project path resolves in a relocated folder with spaces");
                Check(AkWwiseEditorSettings.WwiseProjectAbsolutePath == VesperProjectBootstrap.WwiseProjectPath, "Official Integration uses the relocated Wwise project");
                Check(!AkWwiseEditorSettings.Instance.GenerateSoundBanksAsPreBuildStep && !AkWwiseEditorSettings.Instance.CopySoundBanksAsPreBuildStep, "Bundled banks need no Authoring or copy step");
                foreach (var platform in new[] { "Mac", "Windows" }) {
                    WeatherW11Setup.ValidateBanks(platform); Check(true, "Bundled " + platform + " bank chunks are complete");
                }
                WeatherW11Setup.ValidateScene(); Check(true, "W11 initializer, listener, emitters and game-state references are valid");
                byte[] settings = File.ReadAllBytes(WwiseSettings.Path);
                byte[] scene = File.ReadAllBytes(WeatherW11Setup.ScenePath);
                byte[] playerSettings = File.ReadAllBytes("ProjectSettings/ProjectSettings.asset");
                var repeated = VesperProjectBootstrap.Apply();
                Check(repeated.ready && settings.SequenceEqual(File.ReadAllBytes(WwiseSettings.Path)) &&
                    scene.SequenceEqual(File.ReadAllBytes(WeatherW11Setup.ScenePath)) &&
                    playerSettings.SequenceEqual(File.ReadAllBytes("ProjectSettings/ProjectSettings.asset")), "Repeated setup leaves shared settings and authored scene unchanged");
                var xml = new XmlDocument { XmlResolver = null }; xml.Load(WwiseSettings.Path);
                Check(string.IsNullOrEmpty(xml.SelectSingleNode("/WwiseSettings/WwiseInstallationPathMac").InnerText) &&
                    string.IsNullOrEmpty(xml.SelectSingleNode("/WwiseSettings/WwiseInstallationPathWindows").InnerText), "Shared XML contains no machine-specific installation paths");

                var bad = new WwiseSettings { WwiseProjectPath = "/old/computer/missing.wproj", RootOutputPath = "old/banks",
                    WwiseStreamingAssetsPath = "wrong", CopySoundBanksAsPreBuildStep = true, GenerateSoundBanksAsPreBuildStep = true,
                    CreateWwiseGlobal = true, CreateWwiseListener = true, WaapiPort = "8095", UseWaapi = false, ShowMissingRigidBodyWarning = false };
                Check(VesperProjectBootstrap.NormalizeSettings(bad), "Stale computer paths and conflicting auto-generation are repaired");
                Check(bad.WwiseProjectPath == VesperProjectBootstrap.ProjectRelativePath && bad.WwiseStreamingAssetsPath == VesperProjectBootstrap.BankPath &&
                    bad.RootOutputPath == "StreamingAssets/" + VesperProjectBootstrap.BankPath && !bad.CopySoundBanksAsPreBuildStep &&
                    !bad.GenerateSoundBanksAsPreBuildStep && !bad.CreateWwiseGlobal && !bad.CreateWwiseListener, "Repaired settings use bundled banks and the authored player listener");
                Check(bad.WaapiPort == "8095" && !bad.UseWaapi && !bad.ShowMissingRigidBodyWarning, "Unrelated developer preferences are preserved");
                Check(!VesperProjectBootstrap.NormalizeSettings(bad), "Portable settings normalization is idempotent");

                var initialScenes = EditorBuildSettings.scenes;
                try {
                    EditorBuildSettings.scenes = new EditorBuildSettingsScene[0];
                    VesperProjectBootstrap.EnsureDefaultBuildScene();
                    Check(EditorBuildSettings.scenes.Single().path == WeatherW11Setup.ScenePath, "Empty build list is initialized to W11");
                    EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene("Assets/CustomScene.unity", true) };
                    VesperProjectBootstrap.EnsureDefaultBuildScene();
                    Check(EditorBuildSettings.scenes.Single().path == "Assets/CustomScene.unity", "A developer's custom build list is preserved");
                } finally { EditorBuildSettings.scenes = initialScenes; }
                var active = SceneManager.GetActiveScene();
                EditorSceneManager.MarkSceneDirty(active);
                Check(!VesperProjectBootstrap.CanOpenInitialScene(), "Unsaved scene work is never replaced automatically");
                // Reload this test checkout's unchanged saved scene; never save test-only dirtiness.
                EditorSceneManager.OpenScene(WeatherW11Setup.ScenePath);
                Check(!VesperProjectBootstrap.CanOpenInitialScene(), "An existing saved scene is preserved on later opens");

                string temp = Path.Combine(Path.GetTempPath(), "vesper authoring fixture " + Guid.NewGuid());
                try {
                    string app = Path.Combine(temp, "Wwise.app");
                    Directory.CreateDirectory(Path.Combine(app, "Contents/Tools"));
                    File.WriteAllText(Path.Combine(app, "Contents/Tools/WwiseConsole.sh"), "fixture only");
                    string plist = Path.Combine(app, "Contents/Info.plist");
                    File.WriteAllText(plist, "<plist><dict><key>CFBundleVersion</key><string>2024.1.0.0</string></dict></plist>");
                    Check(VesperProjectBootstrap.ValidateAuthoring(temp, true) == null, "A mismatched Authoring version is rejected");
                    File.WriteAllText(plist, "<plist><dict><key>CFBundleVersion</key><string>2025.1.10.9233</string></dict></plist>");
                    Check(VesperProjectBootstrap.ValidateAuthoring(temp, true) == app, "Matching Authoring can be found in a custom path with spaces");
                    Check(VesperProjectBootstrap.ValidateAuthoring(temp + "/missing", true) == null, "A missing Authoring installation is not treated as installed");
                } finally { if (Directory.Exists(temp)) Directory.Delete(temp, true); }
                Check(VesperProjectBootstrap.QuoteArgument("C:\\Team Project\\Audio\\VesperAudio.wproj") == "\"C:\\Team Project\\Audio\\VesperAudio.wproj\"", "Windows paths with spaces are passed as one argument");

                Write(0);
                WeatherW11Setup.ValidateStateBatch();
            } catch (Exception e) { checks.Add("FAIL " + e.Message); Write(1); Debug.LogException(e); EditorApplication.Exit(1); }
        }
        static void Write(int failures) {
            var report = new Report { unityVersion = Application.unityVersion, checks = checks.ToArray(), failures = failures };
            string output = Path.GetFullPath("../../Audio/bootstrap-validation.json");
            File.WriteAllText(output, JsonUtility.ToJson(report, true));
            Debug.Log("Vesper bootstrap validation: " + checks.Count + " checks, " + failures + " failures.");
        }
    }
}
#endif
