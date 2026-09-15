using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Vesper.Expansion.WeatherW11.Editor;

namespace Vesper.SoundDirector.Editor {
    public static class DirectorReview {
        [Serializable] public sealed class ValidationReport {
            public string scope = "Static scene, catalog and bank checks. Playback and listening are separate checks.";
            public string scene, source, checkedUtc;
            public int layers;
            public string[] errors;
            public bool passed;
        }
        public static string[] Preflight(DirectorSnapshot snapshot, DirectionPlan plan, bool checkRevision) {
            var errors = DirectorRules.Validate(plan, snapshot, SoundCatalog.Load(), checkRevision).ToList();
            foreach (string platform in new[] { "Mac", "Windows" }) {
                string dir = "Assets/StreamingAssets/Audio/GeneratedSoundBanks/" + platform;
                try {
                    WeatherW11Setup.ValidateBankFile(dir + "/Init.bnk");
                    WeatherW11Setup.ValidateBankFile(dir + "/Vesper_W11.bnk");
                    WeatherW11Setup.ValidateBankFile(dir + "/Vesper_Director.bnk");
                    string metadata = File.ReadAllText(dir + "/Vesper_Director.json");
                    foreach (var sound in (plan?.layers ?? Array.Empty<DirectionLayer>()).Where(l => l != null).Select(l => SoundCatalog.Load().Find(l.soundId)).Where(s => s != null).Distinct())
                        if (!metadata.Contains("\"" + sound.eventName + "\"")) errors.Add(platform + " SoundBank에 이벤트가 없습니다: " + sound.id);
                } catch (Exception e) { errors.Add(platform + " SoundBank: " + e.Message); }
            }
#if !VESPER_WWISE
            errors.Add("Wwise SDK가 활성화되어 있지 않습니다.");
#endif
            var player = DirectorScene.Player();
            if (!player || !player.profile) errors.Add("현재 장면을 먼저 준비해 주세요.");
            if (player && !player.listener) errors.Add("청취자가 연결되지 않았습니다.");
            return errors.Distinct().ToArray();
        }
        public static void Apply(PlannerResult result) {
            if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Play를 멈춘 뒤 적용해 주세요.");
            var snapshot = DirectorScene.Capture();
            var errors = Preflight(snapshot, result.plan, true);
            if (errors.Length > 0) throw new InvalidOperationException(string.Join("\n", errors));
            var player = DirectorScene.Player(); var profile = player.profile;
            // Keep the entire previous state (including provenance) across editor restarts.
            var copy = UnityEngine.Object.Instantiate(profile);
            copy.previousState = "";
            string previous = JsonUtility.ToJson(copy);
            UnityEngine.Object.DestroyImmediate(copy);
            Undo.RecordObject(profile, "Apply sound direction");
            profile.previousState = previous;
            profile.plan = JsonUtility.FromJson<DirectionPlan>(JsonUtility.ToJson(result.plan));
            profile.source = result.source; profile.model = result.model; profile.prompt = result.prompt;
            profile.createdUtc = DateTime.UtcNow.ToString("o"); profile.requestMilliseconds = result.milliseconds;
            EditorUtility.SetDirty(profile); AssetDatabase.SaveAssetIfDirty(profile);
            Undo.RecordObject(player, "Enable sound direction"); player.useDirection = true;
            EditorSceneManager.MarkSceneDirty(player.gameObject.scene);
            WriteReport();
        }
        public static void Restore() {
            if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Play를 멈춘 뒤 복원해 주세요.");
            var player = DirectorScene.Player(); var profile = player ? player.profile : null;
            if (!profile || string.IsNullOrEmpty(profile.previousState)) throw new InvalidOperationException("복원할 이전 연출이 없습니다.");
            string previous = profile.previousState;
            Undo.RecordObject(profile, "Restore previous direction");
            JsonUtility.FromJsonOverwrite(previous, profile);
            EditorUtility.SetDirty(profile); AssetDatabase.SaveAssetIfDirty(profile);
        }
        public static ValidationReport WriteReport() {
            var snapshot = DirectorScene.Capture(); var player = DirectorScene.Player();
            var errors = Preflight(snapshot, player.profile.plan, false);
            var report = new ValidationReport { scene = SceneManager.GetActiveScene().path, source = player.profile.source,
                checkedUtc = DateTime.UtcNow.ToString("o"), layers = player.profile.plan.layers.Length, errors = errors, passed = errors.Length == 0 };
            Directory.CreateDirectory("UserSettings/SoundDirector");
            File.WriteAllText("UserSettings/SoundDirector/validation.json", JsonUtility.ToJson(report, true));
            return report;
        }
    }
}
