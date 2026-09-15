using System;
using System.IO;
using System.Linq;
using System.Threading;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Vesper.SoundDirector.Editor {
    public sealed class SoundDirectorWindow : EditorWindow {
        [SerializeField] string prompt = "숲 초입은 편안하게, 폐허에 가까워질수록 불안하게 만들어줘. 물소리는 가까이에서만 들리게 하고, 발소리는 유지해줘.";
        [SerializeField] string model = DirectorPlanner.DefaultModel;
        [SerializeField] bool connectionOpen;
        // Native Editor SessionState survives Play Mode/domain reload and clears on Unity exit.
        // The key never enters window serialization, assets, EditorPrefs, or the player build.
        static string KeySlot => "Vesper.SoundDirector.ApiKey." + Application.dataPath;
        static string sessionKey { get => SessionState.GetString(KeySlot, ""); set => SessionState.SetString(KeySlot, value); }
        DirectorSnapshot snapshot;
        PlannerResult review;
        CancellationTokenSource cancellation;
        bool busy;
        string message;
        MessageType messageType;
        Vector2 scroll, targetScroll;
        bool showCatalog;
        double started;
        GUIStyle titleStyle, subtitle, wrap, cardTitle;
        [MenuItem("Vesper/Sound Director/Open %#d")]
        public static void Open() { var window = GetWindow<SoundDirectorWindow>("Sound Director"); window.minSize = new Vector2(760, 610); window.Show(); }
        void OnEnable() { EditorApplication.playModeStateChanged += OnPlayMode; }
        void OnDisable() { cancellation?.Cancel(); EditorApplication.playModeStateChanged -= OnPlayMode; }
        void OnPlayMode(PlayModeStateChange state) { cancellation?.Cancel(); snapshot = null; review = null; Repaint(); }
        void OnInspectorUpdate() { Repaint(); }
        void Styles() {
            if (titleStyle != null) return;
            titleStyle = new GUIStyle(EditorStyles.boldLabel) { fontSize = 25, normal = { textColor = new Color(.42f, .87f, .77f) } };
            subtitle = new GUIStyle(EditorStyles.label) { fontSize = 12, wordWrap = true };
            wrap = new GUIStyle(EditorStyles.label) { wordWrap = true };
            cardTitle = new GUIStyle(EditorStyles.boldLabel) { fontSize = 13, wordWrap = true };
        }
        void OnGUI() {
            Styles();
            GUILayout.Space(16);
            using (new EditorGUILayout.HorizontalScope()) {
                GUILayout.Space(18);
                using (new EditorGUILayout.VerticalScope()) {
                    GUILayout.Label("VESPER / SOUND DIRECTOR", titleStyle);
                    GUILayout.Label("장면의 의도를, 실제로 들리는 사운드로.", subtitle);
                }
                GUILayout.FlexibleSpace();
                if (GUILayout.Button("사용 안내", GUILayout.Width(90), GUILayout.Height(30)))
                    Application.OpenURL("https://github.com/seongjin971/gamedemo/blob/feat/wwise-w11/Audio/SOUND_DIRECTOR.md");
                GUILayout.Space(18);
            }
            GUILayout.Space(14);
            using (new EditorGUILayout.HorizontalScope(EditorStyles.toolbar)) {
                GUILayout.Label("01 장면 읽기     →     02 연출 설계     →     03 적용·비교     →     04 검증");
                GUILayout.FlexibleSpace(); GUILayout.Label(busy ? "AI 설계 중…" : "Unity + Wwise");
            }
            using (new EditorGUILayout.HorizontalScope()) {
                using (new EditorGUILayout.VerticalScope(GUILayout.Width(245))) { DrawScene(); }
                scroll = EditorGUILayout.BeginScrollView(scroll);
                DrawWorkspace();
                EditorGUILayout.EndScrollView();
            }
        }
        void DrawScene() {
            GUILayout.Space(10);
            GUILayout.Label("현재 장면", cardTitle);
            GUILayout.Label(UnityEngine.SceneManagement.SceneManager.GetActiveScene().name, wrap);
            using (new EditorGUI.DisabledScope(busy || EditorApplication.isPlayingOrWillChangePlaymode)) {
                if (GUILayout.Button("현재 장면 준비")) Run(() => { DirectorScene.PrepareCurrent(); Analyze(); });
                if (GUILayout.Button("장면 다시 읽기")) Run(Analyze);
                if (GUILayout.Button("선택 오브젝트를 대상으로 추가")) Run(() => {
                    foreach (var go in Selection.gameObjects) DirectorScene.AddToObject(go); Analyze();
                });
                if (GUILayout.Button("대상 ID 정리")) Run(() => { DirectorScene.RepairIds(); Analyze(); });
            }
            GUILayout.Space(8);
            if (snapshot != null) {
                GUILayout.Label(snapshot.targets.Length + "개 대상 · " + snapshot.objectCount + "개 오브젝트", EditorStyles.miniLabel);
                targetScroll = EditorGUILayout.BeginScrollView(targetScroll, GUILayout.MinHeight(180));
                foreach (var target in snapshot.targets) using (new EditorGUILayout.VerticalScope(EditorStyles.helpBox)) {
                    GUILayout.Label(target.name, EditorStyles.boldLabel); GUILayout.Label(target.description, wrap);
                    GUILayout.Label(target.suggestedRadius.ToString("0") + " m · " + target.position.ToString("F0"), EditorStyles.miniLabel);
                    if (GUILayout.Button("장면에서 보기", EditorStyles.miniButton)) {
                        var found = UnityEngine.Object.FindObjectsByType<SoundTarget>().FirstOrDefault(t => t.id == target.id);
                        if (found) { Selection.activeGameObject = found.gameObject; SceneView.lastActiveSceneView?.FrameSelected(); }
                    }
                }
                EditorGUILayout.EndScrollView();
            } else EditorGUILayout.HelpBox("장면을 읽으면 사운드 대상과 설명이 여기에 표시됩니다.", MessageType.None);
            GUILayout.FlexibleSpace();
            using (new EditorGUI.DisabledScope(busy || EditorApplication.isPlayingOrWillChangePlaymode)) {
                if (GUILayout.Button("W11 탐험 장면 열기")) Run(() => {
                    if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) { EditorSceneManager.OpenScene(DirectorScene.W11); Analyze(); }
                });
                if (GUILayout.Button("두 번째 장면 · Sound Lab")) Run(() => { DirectorScene.OpenLab(); Analyze(); });
            }
            GUILayout.Space(8);
        }
        void DrawWorkspace() {
            GUILayout.Space(10);
            connectionOpen = EditorGUILayout.Foldout(connectionOpen, "연결 설정 · " + (HasKey ? "키 입력됨 (호출 전)" : "API 키 필요"), true);
            if (connectionOpen) using (new EditorGUILayout.VerticalScope(EditorStyles.helpBox)) {
                sessionKey = EditorGUILayout.PasswordField("OpenAI API 키", sessionKey);
                model = EditorGUILayout.TextField("모델", model);
                GUILayout.Label("키는 현재 Unity 세션에만 보관되며 종료 시 지워집니다. Play/정지 후에도 유지됩니다. OPENAI_API_KEY 환경변수도 사용할 수 있습니다.", wrap);
                GUILayout.Label("AI 설계 시 요청문, 장면 대상·이름·재질, 사운드 목록, 현재 계획이 OpenAI로 전송됩니다. WAV 파일은 전송하지 않습니다.", wrap);
                if (GUILayout.Button("API 키 관리 페이지 열기")) Application.OpenURL("https://platform.openai.com/api-keys");
                if (!string.IsNullOrEmpty(sessionKey) && GUILayout.Button("입력한 키 지우기")) SessionState.EraseString(KeySlot);
            }
            GUILayout.Space(10);
            GUILayout.Label("어떤 분위기로 연출할까요?", cardTitle);
            using (new EditorGUI.DisabledScope(busy || EditorApplication.isPlayingOrWillChangePlaymode))
                prompt = EditorGUILayout.TextArea(prompt, new GUIStyle(EditorStyles.textArea) { wordWrap = true }, GUILayout.MinHeight(78));
            using (new EditorGUILayout.HorizontalScope()) {
                using (new EditorGUI.DisabledScope(busy || EditorApplication.isPlayingOrWillChangePlaymode)) {
                    if (GUILayout.Button("AI 연출 설계", GUILayout.Height(34))) Generate();
                    if (GUILayout.Button("예제 불러오기 · AI 아님", GUILayout.Height(34))) Run(() => {
                        Analyze(); review = DirectorExamples.Create(snapshot, true); message = "수동 작성된 기능 확인용 예제입니다. 실제 AI 응답이 아닙니다."; messageType = MessageType.Warning;
                    });
                }
                if (busy && GUILayout.Button("취소", GUILayout.Width(60), GUILayout.Height(34))) cancellation?.Cancel();
            }
            if (busy) GUILayout.Label("장면과 사운드 목록으로 계획을 작성하고 검사합니다. " + (EditorApplication.timeSinceStartup - started).ToString("0") + "초", wrap);
            if (!string.IsNullOrEmpty(message)) EditorGUILayout.HelpBox(message, messageType);
            if (EditorApplication.isPlayingOrWillChangePlaymode) EditorGUILayout.HelpBox("Play 중에는 A/B를 들어볼 수 있습니다. 새 연출의 설계·적용은 Play를 멈춘 뒤 실행해 주세요.", MessageType.Info);
            if (review != null) DrawReview();
            GUILayout.Space(12); DrawApplied();
            GUILayout.Space(12);
            showCatalog = EditorGUILayout.Foldout(showCatalog, "보유 사운드 · 76개 파일 / 17개 사용 가능 환경음 풀", true);
            if (showCatalog) foreach (var sound in SoundCatalog.Load().sounds) {
                GUILayout.Label((sound.available ? "● " : "○ ") + sound.id + " · " + sound.files.Length + " files" + (sound.loop ? " · loop" : " · one-shot"), EditorStyles.boldLabel);
                GUILayout.Label(sound.description, wrap);
            }
        }
        void DrawReview() {
            GUILayout.Space(12);
            using (new EditorGUILayout.VerticalScope(EditorStyles.helpBox)) {
                GUILayout.Label("변경안 · " + review.source, cardTitle);
                GUILayout.Label(review.plan.summary, wrap);
                GUILayout.Label(review.model + (review.milliseconds > 0 ? " · " + (review.milliseconds / 1000f).ToString("F1") + "초 · " + review.attempts + "회 호출" : ""), EditorStyles.miniLabel);
                foreach (var warning in review.plan.warnings ?? Array.Empty<string>()) EditorGUILayout.HelpBox(warning, MessageType.Warning);
                foreach (var layer in review.plan.layers) {
                    var target = snapshot.targets.FirstOrDefault(t => t.id == layer.targetId);
                    var old = snapshot.currentPlan?.layers?.FirstOrDefault(l => l.targetId == layer.targetId && l.soundId == layer.soundId);
                    GUILayout.Space(6); GUILayout.Label((target?.name ?? layer.targetId) + " → " + layer.soundId, EditorStyles.boldLabel);
                    string values = layer.gainDb + " dB / " + layer.radius + " m / fade " + layer.fadeSeconds + " s";
                    if (!SoundCatalog.Load().Find(layer.soundId).loop) values += " / 간격 " + layer.intervalSeconds + " s";
                    GUILayout.Label(old == null ? "추가 · " + values : "기존 " + old.gainDb + " dB / " + old.radius + " m → " + values, wrap);
                    GUILayout.Label(layer.reason, wrap);
                }
                foreach (var old in snapshot.currentPlan?.layers ?? Array.Empty<DirectionLayer>())
                    if (!review.plan.layers.Any(l => l.targetId == old.targetId && l.soundId == old.soundId)) GUILayout.Label("제거 · " + old.soundId + " / " + snapshot.targets.FirstOrDefault(t => t.id == old.targetId)?.name, wrap);
                GUILayout.Space(10);
                using (new EditorGUI.DisabledScope(busy || EditorApplication.isPlayingOrWillChangePlaymode))
                    if (GUILayout.Button("이 연출 적용", GUILayout.Height(34))) Run(() => {
                        DirectorReview.Apply(review); review = null; Analyze();
                        message = "적용과 정적 검사 완료. Play를 눌러 A/B를 비교해 주세요. 실제 재생 검증은 다음 단계입니다."; messageType = MessageType.Info;
                    });
                if (GUILayout.Button("변경안 닫기")) review = null;
            }
        }
        void DrawApplied() {
            var player = DirectorScene.Player();
            if (!player || !player.profile || player.profile.plan.layers.Length == 0) return;
            GUILayout.Label("적용된 연출", cardTitle);
            GUILayout.Label(player.profile.plan.summary, wrap);
            GUILayout.Label(player.profile.source + " · " + player.profile.plan.layers.Length + " layers", EditorStyles.miniLabel);
            using (new EditorGUILayout.HorizontalScope()) {
                using (new EditorGUI.DisabledScope(!EditorApplication.isPlaying || !player.Ready)) {
                    GUI.backgroundColor = !player.useDirection ? new Color(.4f, .85f, .75f) : Color.white;
                    if (GUILayout.Button("A · 원본", GUILayout.Height(32))) player.useDirection = false;
                    GUI.backgroundColor = player.useDirection ? new Color(.4f, .85f, .75f) : Color.white;
                    if (GUILayout.Button("B · 연출", GUILayout.Height(32))) player.useDirection = true;
                    GUI.backgroundColor = Color.white;
                }
                if (!EditorApplication.isPlaying && GUILayout.Button("Play · 들어보기", GUILayout.Height(32))) EditorApplication.EnterPlaymode();
                if (EditorApplication.isPlaying && GUILayout.Button("정지", GUILayout.Height(32))) EditorApplication.ExitPlaymode();
            }
            if (EditorApplication.isPlaying) GUILayout.Label(player.Status + " · posted " + player.PostedEvents + " · errors " + player.ErrorCount, wrap);
            using (new EditorGUI.DisabledScope(busy || EditorApplication.isPlayingOrWillChangePlaymode)) using (new EditorGUILayout.HorizontalScope()) {
                if (GUILayout.Button("적용 결과 검사")) Run(() => { var report = DirectorReview.WriteReport(); message = report.passed ? "장면·이벤트·Mac/Windows Bank 검사 통과. 음향 품질은 A/B 청취로 확인해 주세요." : string.Join("\n", report.errors); messageType = report.passed ? MessageType.Info : MessageType.Error; });
                using (new EditorGUI.DisabledScope(string.IsNullOrEmpty(player.profile.previousState)))
                    if (GUILayout.Button("이전 연출 복원")) Run(() => { DirectorReview.Restore(); Analyze(); message = "이전 연출을 복원했습니다."; messageType = MessageType.Info; });
                if (GUILayout.Button("계획 JSON 내보내기")) Run(() => {
                    string path = EditorUtility.SaveFilePanel("연출 계획 내보내기", "", "sound-direction.json", "json");
                    if (!string.IsNullOrEmpty(path)) File.WriteAllText(path, JsonUtility.ToJson(player.profile, true));
                });
            }
        }
        bool HasKey => !string.IsNullOrWhiteSpace(sessionKey) || !string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("OPENAI_API_KEY"));
        void Analyze() { snapshot = DirectorScene.Capture(); review = null; }
        void Run(Action action) { try { action(); } catch (Exception e) { message = e.Message; messageType = MessageType.Error; } Repaint(); }
        async void Generate() {
            if (!HasKey) { connectionOpen = true; message = "실제 AI 설계에는 OpenAI API 키가 필요합니다. 키를 입력하거나 명시된 예제로 먼저 기능을 확인할 수 있습니다."; messageType = MessageType.Warning; return; }
            try {
                Analyze(); busy = true; review = null; message = null; started = EditorApplication.timeSinceStartup;
                cancellation = new CancellationTokenSource();
                var result = await DirectorPlanner.Generate(prompt, snapshot, SoundCatalog.Load(), model,
                    string.IsNullOrWhiteSpace(sessionKey) ? Environment.GetEnvironmentVariable("OPENAI_API_KEY") : sessionKey, cancellation.Token);
                if (!this || cancellation.IsCancellationRequested) return;
                if (snapshot.revision != DirectorScene.Capture().revision) throw new InvalidOperationException("AI 설계 중 장면이 바뀌었습니다. 장면을 다시 읽고 설계해 주세요.");
                review = result; message = "AI 계획 검사 통과. 변경 내용을 확인하고 적용해 주세요."; messageType = MessageType.Info;
            } catch (OperationCanceledException) { message = "설계를 취소했습니다. 현재 연출은 유지됩니다."; messageType = MessageType.Info; }
            catch (Exception e) { message = e.Message; messageType = MessageType.Error; }
            finally { busy = false; cancellation?.Dispose(); cancellation = null; if (this) Repaint(); }
        }
    }
}
