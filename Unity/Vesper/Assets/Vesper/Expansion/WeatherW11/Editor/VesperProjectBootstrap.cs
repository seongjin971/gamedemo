using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Vesper.Expansion.WeatherW11.Editor {
    // Runs after import, never installs packages or starts Authoring to play the game.
    [InitializeOnLoad]
    public static class VesperProjectBootstrap {
        public const string UnityVersion = "6000.5.7f1";
        public const string WwiseVersion = "2025.1.10.9233";
        public const string ProjectRelativePath = "../../../Audio/VesperAudio/VesperAudio.wproj";
        public const string BankPath = "Audio/GeneratedSoundBanks";
        const string ReportPath = "UserSettings/VesperSetup.json";
        const string SeenKey = "Vesper.W11.SetupSeen.";
        public static SetupReport LastReport { get; private set; }
        static bool pending;

        [Serializable] public sealed class SetupReport {
            public bool ready, awaitingCompilation;
            public string unityVersion, platform, authoringPath;
            public string[] errors, notes;
        }

        public static string WwiseProjectPath => Path.GetFullPath(Path.Combine(Application.dataPath, ProjectRelativePath));
        public static bool IsMac => Application.platform == RuntimePlatform.OSXEditor;
        static string LocalPathKey => "Vesper.W11.Authoring." + Application.dataPath;

        static VesperProjectBootstrap() {
            if (!AssetDatabase.IsAssetImportWorkerProcess() &&
                (!Application.isBatchMode || Environment.GetCommandLineArgs().Contains("-vesperAutoSetup"))) Schedule();
        }

        public static void Schedule() {
            if (pending) return;
            pending = true;
            EditorApplication.update += Tick;
        }
        static void Tick() {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating ||
                EditorApplication.isPlayingOrWillChangePlaymode || BuildPipeline.isBuildingPlayer) return;
            EditorApplication.update -= Tick; pending = false;
            var result = Apply();
            if (result.awaitingCompilation) return; // The next domain reload resumes setup.
            bool first = !EditorPrefs.GetBool(SeenKey + Application.dataPath, false);
            if (result.ready && first && CanOpenInitialScene()) {
                EditorSceneManager.OpenScene(WeatherW11Setup.ScenePath);
                result = Apply();
            }
            if (first && !Application.isBatchMode) {
                EditorPrefs.SetBool(SeenKey + Application.dataPath, true);
                VesperSetupWindow.ShowWindow();
            }
            Debug.Log(result.ready ? "Vesper: setup ready. Open W11 and press Play; Wwise Authoring is optional."
                : "Vesper: setup needs attention. See Vesper > W11 Audio > Setup Status.");
#if VESPER_WWISE
            if (Application.isBatchMode && Environment.GetCommandLineArgs().Contains("-vesperVerifyFreshClone") &&
                !SessionState.GetBool("Vesper.FreshCloneValidationStarted", false)) {
                SessionState.SetBool("Vesper.FreshCloneValidationStarted", true);
                VesperBootstrapValidation.CompleteFreshClone();
            }
#endif
        }

        public static bool CanOpenInitialScene() {
            var scene = SceneManager.GetActiveScene();
            return SceneManager.sceneCount == 1 && !scene.isDirty && string.IsNullOrEmpty(scene.path);
        }

        public static SetupReport Apply() {
            var errors = new List<string>(); var notes = new List<string>();
            var result = new SetupReport { unityVersion = Application.unityVersion,
                platform = IsMac ? "Mac" : "Windows", authoringPath = "" };
            try {
                if (Application.platform != RuntimePlatform.OSXEditor && Application.platform != RuntimePlatform.WindowsEditor)
                    throw new InvalidOperationException("이 프로젝트는 Windows와 macOS Editor를 지원합니다.");
                if (!File.Exists(WwiseProjectPath) || !File.Exists(WeatherW11Setup.ScenePath))
                    throw new InvalidOperationException("저장소 전체가 필요합니다. feat/wwise-w11 브랜치의 Audio 및 Unity 폴더를 함께 받으세요.");
                if (!File.Exists("Assets/Wwise/Version.txt"))
                    throw new InvalidOperationException("Assets/Wwise가 누락됐습니다. 저장소 파일을 모두 내려받으세요.");
                if (!File.ReadAllText("Assets/Wwise/Version.txt").Contains("2025.1.10 Build 9233"))
                    throw new InvalidOperationException("W11에는 Wwise Integration 2025.1.10 / SDK 9233이 필요합니다.");
                if (Application.unityVersion != UnityVersion) notes.Add("검증된 Unity 버전: " + UnityVersion);
                if (BuildPipeline.GetBuildTargetGroup(EditorUserBuildSettings.activeBuildTarget) != BuildTargetGroup.Standalone)
                    throw new InvalidOperationException("Build Profiles에서 Windows 또는 macOS를 활성화한 뒤 다시 확인하세요.");
                if (EnsureDefine()) { result.awaitingCompilation = true; notes.Add("SDK 활성화 후 Unity가 다시 컴파일합니다."); }
#if VESPER_WWISE
                var settings = AkWwiseEditorSettings.Instance;
                string savedLocalPath = settings.WwiseInstallationPath;
                bool changed = NormalizeSettings(settings) || HasSavedMachinePath();
                // Shared settings stay portable; the machine's executable is injected in memory.
                if (changed) {
                    settings.WwiseInstallationPathMac = settings.WwiseInstallationPathWindows = "";
                    settings.SaveSettings();
                }
                bool noAuthoring = Environment.GetCommandLineArgs().Contains("-vesperNoAuthoring");
                result.authoringPath = noAuthoring ? "" : FindAuthoring(IsMac,
                    EditorPrefs.GetString(LocalPathKey, ""), savedLocalPath);
                settings.WwiseInstallationPath = result.authoringPath;
                if (!string.IsNullOrEmpty(result.authoringPath)) EditorPrefs.SetString(LocalPathKey, result.authoringPath);
                else notes.Add("플레이 준비에는 Wwise Authoring 설치·실행이 필요하지 않습니다. 음향 편집 시 " + WwiseVersion + "을 설치하세요.");
                EnsureBasePaths();
                foreach (var platform in new[] { "Mac", "Windows" }) WeatherW11Setup.ValidateBanks(platform);
                string native = IsMac ? "Mac/Profile/AkUnitySoundEngine.bundle/Contents/MacOS/AkUnitySoundEngine"
                    : "Windows/x86_64/Profile/AkUnitySoundEngine.dll";
                if (!File.Exists("Assets/Wwise/API/Runtime/Plugins/" + native))
                    throw new InvalidOperationException("현재 운영체제의 Wwise 네이티브 플러그인이 누락됐습니다. 저장소를 완전히 받아주세요.");
                var project = new XmlDocument { XmlResolver = null }; project.Load(WwiseProjectPath);
                if (project.DocumentElement.GetAttribute("WwiseVersion") != "v2025.1.10" || project.DocumentElement.GetAttribute("WwiseBuild") != "9233")
                    throw new InvalidOperationException("Wwise 프로젝트 버전이 연결된 SDK와 다릅니다. 자동 업그레이드는 하지 않습니다.");
                EnsureDefaultBuildScene();
                if (SceneManager.GetActiveScene().path == WeatherW11Setup.ScenePath) WeatherW11Setup.ValidateScene();
#else
                result.awaitingCompilation = true;
#endif
            } catch (Exception e) { errors.Add(e.Message); }
            result.errors = errors.ToArray(); result.notes = notes.ToArray();
            result.ready = errors.Count == 0 && !result.awaitingCompilation;
            LastReport = result;
            Directory.CreateDirectory("UserSettings");
            File.WriteAllText(ReportPath, JsonUtility.ToJson(result, true));
            return result;
        }

        internal static bool EnsureDefine() {
            string current = PlayerSettings.GetScriptingDefineSymbols(NamedBuildTarget.Standalone);
            var symbols = current.Split(';').Where(s => !string.IsNullOrWhiteSpace(s)).ToList();
            if (symbols.Contains("VESPER_WWISE")) return false;
            symbols.Add("VESPER_WWISE");
            PlayerSettings.SetScriptingDefineSymbols(NamedBuildTarget.Standalone, string.Join(";", symbols));
            return true;
        }

#if VESPER_WWISE
        internal static bool NormalizeSettings(WwiseSettings settings) {
            bool changed = settings.WwiseProjectPath != ProjectRelativePath || settings.WwiseStreamingAssetsPath != BankPath ||
                settings.RootOutputPath != "StreamingAssets/" + BankPath || settings.CopySoundBanksAsPreBuildStep ||
                settings.GenerateSoundBanksAsPreBuildStep || settings.CreateWwiseGlobal || settings.CreateWwiseListener;
            settings.WwiseProjectPath = ProjectRelativePath;
            settings.WwiseStreamingAssetsPath = BankPath;
            settings.RootOutputPath = "StreamingAssets/" + BankPath;
            settings.CopySoundBanksAsPreBuildStep = settings.GenerateSoundBanksAsPreBuildStep = false;
            settings.CreateWwiseGlobal = settings.CreateWwiseListener = false;
            return changed;
        }
        static bool HasSavedMachinePath() {
            if (!File.Exists(WwiseSettings.Path)) return true;
            var xml = new XmlDocument { XmlResolver = null }; xml.Load(WwiseSettings.Path);
            return !string.IsNullOrWhiteSpace(xml.SelectSingleNode("/WwiseSettings/WwiseInstallationPathMac")?.InnerText) ||
                !string.IsNullOrWhiteSpace(xml.SelectSingleNode("/WwiseSettings/WwiseInstallationPathWindows")?.InnerText);
        }
        static void EnsureBasePaths() {
            foreach (var name in new[] { "AkWwiseInitializationSettings", "Mac", "Windows" }) {
                var asset = AssetDatabase.LoadAssetAtPath<ScriptableObject>("Assets/Wwise/ScriptableObjects/" + name + ".asset");
                if (!asset) throw new InvalidOperationException("Wwise 초기화 설정 파일이 누락됐습니다: " + name);
                var serialized = new SerializedObject(asset);
                var path = serialized.FindProperty("UserSettings.m_BasePath");
                if (path == null) throw new InvalidOperationException("Wwise 설정의 BasePath를 찾을 수 없습니다: " + name);
                if (path.stringValue == BankPath) continue;
                path.stringValue = BankPath; serialized.ApplyModifiedPropertiesWithoutUndo(); AssetDatabase.SaveAssetIfDirty(asset);
            }
        }
#endif
        internal static void EnsureDefaultBuildScene() {
            var scenes = EditorBuildSettings.scenes;
            if (scenes.Length == 0 || (scenes.Length == 1 && scenes[0].path == "Assets/Vesper/Scenes/VesperMigrationSlice.unity"))
                EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(WeatherW11Setup.ScenePath, true) };
        }

        internal static string FindAuthoring(bool mac, params string[] preferred) {
            var candidates = new List<string>(preferred);
            string sdk = Environment.GetEnvironmentVariable("WWISESDK");
            if (!string.IsNullOrWhiteSpace(sdk)) candidates.Add(Path.GetDirectoryName(sdk.TrimEnd('/', '\\')));
            candidates.Add(Environment.GetEnvironmentVariable("WWISEROOT"));
            if (mac) {
                candidates.Add("/Applications/Audiokinetic/Wwise_" + WwiseVersion);
                candidates.Add(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Personal), "Applications/Audiokinetic/Wwise_" + WwiseVersion));
            } else {
                foreach (var variable in new[] { "ProgramFiles(x86)", "ProgramFiles" }) {
                    string root = Environment.GetEnvironmentVariable(variable);
                    if (!string.IsNullOrWhiteSpace(root)) candidates.Add(Path.Combine(root, "Audiokinetic/Wwise " + WwiseVersion));
                }
            }
            foreach (var candidate in candidates) {
                string path = ValidateAuthoring(candidate, mac);
                if (path != null) return path;
            }
            return "";
        }
        internal static string ValidateAuthoring(string candidate, bool mac) {
            if (string.IsNullOrWhiteSpace(candidate)) return null;
            try {
                string path = Path.GetFullPath(candidate);
                if (mac && !path.EndsWith(".app", StringComparison.OrdinalIgnoreCase)) path = Path.Combine(path, "Wwise.app");
                string console = mac ? Path.Combine(path, "Contents/Tools/WwiseConsole.sh") : Path.Combine(path, "Authoring/x64/Release/bin/WwiseConsole.exe");
                if (!File.Exists(console)) return null;
                string version;
                if (mac) {
                    version = ReadMacBundleVersion(Path.Combine(path, "Contents/Info.plist"));
                } else {
                    var info = System.Diagnostics.FileVersionInfo.GetVersionInfo(console);
                    version = $"{info.FileMajorPart}.{info.FileMinorPart}.{info.FileBuildPart}.{info.FilePrivatePart}";
                }
                return version == WwiseVersion ? path : null;
            } catch (Exception) { return null; }
        }

        static string ReadMacBundleVersion(string path) {
            try {
                var plist = new XmlDocument { XmlResolver = null }; plist.Load(path);
                return plist.SelectSingleNode("/plist/dict/key[text()='CFBundleVersion']/following-sibling::string[1]")?.InnerText;
            } catch (XmlException) {
                if (!IsMac) return null;
                // Current Wwise.app uses a binary plist. Read it without modifying the installation.
                var start = new System.Diagnostics.ProcessStartInfo {
                    FileName = "/usr/bin/plutil", Arguments = "-extract CFBundleVersion raw -o - " + QuoteArgument(path),
                    UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true
                };
                using (var process = System.Diagnostics.Process.Start(start)) {
                    if (process == null) return null;
                    if (!process.WaitForExit(5000)) { process.Kill(); return null; }
                    return process.ExitCode == 0 ? process.StandardOutput.ReadToEnd().Trim() : null;
                }
            }
        }

        public static void SelectAuthoring() {
            string path = EditorUtility.OpenFolderPanel("Wwise " + WwiseVersion + " 설치 폴더 또는 Wwise.app 선택", "", "");
            if (string.IsNullOrEmpty(path)) return;
            string validated = ValidateAuthoring(path, IsMac);
            if (validated == null) { EditorUtility.DisplayDialog("Wwise 경로", "Wwise " + WwiseVersion + " 설치와 실행 파일을 확인해주세요.", "확인"); return; }
            EditorPrefs.SetString(LocalPathKey, validated); Apply();
        }

        public static void OpenScene(bool askToSave = true) {
            if (askToSave && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(WeatherW11Setup.ScenePath); WeatherW11Setup.ValidateScene();
        }

        public static void OpenAuthoring() {
            var report = Apply();
            if (string.IsNullOrEmpty(report.authoringPath)) {
                SelectAuthoring(); report = LastReport;
                if (report == null || string.IsNullOrEmpty(report.authoringPath)) return;
            }
            var start = new System.Diagnostics.ProcessStartInfo { UseShellExecute = false };
            if (IsMac) { start.FileName = "/usr/bin/open"; start.Arguments = "-a " + QuoteArgument(report.authoringPath) + " " + QuoteArgument(WwiseProjectPath); }
            else { start.FileName = Path.Combine(report.authoringPath, "Authoring/x64/Release/bin/Wwise.exe"); start.Arguments = QuoteArgument(WwiseProjectPath); }
            System.Diagnostics.Process.Start(start)?.Dispose();
        }
        internal static string QuoteArgument(string argument) {
            // ProcessStartInfo.Arguments uses backslash/quote escaping; no shell is involved.
            var result = new System.Text.StringBuilder("\""); int slashes = 0;
            foreach (char c in argument) {
                if (c == '\\') { slashes++; continue; }
                result.Append('\\', c == '"' ? slashes * 2 + 1 : slashes); result.Append(c); slashes = 0;
            }
            return result.Append('\\', slashes * 2).Append('"').ToString();
        }
    }

    public sealed class VesperSetupWindow : EditorWindow {
        [MenuItem("Vesper/W11 Audio/Setup Status", priority = 0)]
        public static void ShowWindow() {
            var window = GetWindow<VesperSetupWindow>("Vesper 실행 준비"); window.minSize = new Vector2(460, 300);
        }
        void OnInspectorUpdate() { Repaint(); }
        void OnGUI() {
            GUILayout.Label("Vesper W11", EditorStyles.boldLabel);
            var report = VesperProjectBootstrap.LastReport;
            EditorGUILayout.HelpBox(report == null ? "프로젝트 가져오기가 끝나면 자동으로 설정합니다." :
                report.ready ? "실행 준비 완료. W11 장면에서 Play를 누르세요." :
                report.awaitingCompilation ? "Wwise 활성화 후 컴파일 중입니다." : "아래 항목을 확인해주세요.",
                report != null && report.ready ? MessageType.Info : MessageType.Warning);
            if (report != null) {
                foreach (string error in report.errors) EditorGUILayout.HelpBox(error, MessageType.Error);
                foreach (string note in report.notes) EditorGUILayout.HelpBox(note, MessageType.Info);
            }
            using (new EditorGUI.DisabledScope(EditorApplication.isCompiling || EditorApplication.isPlayingOrWillChangePlaymode)) {
                if (GUILayout.Button("설정 다시 확인")) VesperProjectBootstrap.Schedule();
                using (new EditorGUI.DisabledScope(report == null || !report.ready))
                    if (GUILayout.Button("W11 장면 열기")) VesperProjectBootstrap.OpenScene();
                GUILayout.Space(12);
                GUILayout.Label("음향 편집 시에만 필요", EditorStyles.boldLabel);
                if (GUILayout.Button("Wwise 프로젝트 열기")) VesperProjectBootstrap.OpenAuthoring();
                if (GUILayout.Button("Wwise 설치 경로 선택")) VesperProjectBootstrap.SelectAuthoring();
            }
        }
    }
}
