using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Vesper.Expansion.WeatherW11;
using W10 = Vesper.Expansion.WeatherW10;

namespace Vesper.SoundDirector.Editor {
    public static class DirectorScene {
        public const string Root = "Assets/Vesper/SoundDirector";
        public const string W11 = "Assets/Vesper/Scenes/Expansion/VesperWeatherWorld_W11.unity";
        public const string Lab = "Assets/Vesper/Scenes/Expansion/VesperSoundDirector_Lab.unity";
        public static SoundDirectorPlayer Player() => UnityEngine.Object.FindObjectsByType<SoundDirectorPlayer>(FindObjectsInactive.Exclude)
            .FirstOrDefault(p => p.gameObject.scene == SceneManager.GetActiveScene());
        public static DirectorSnapshot Capture() {
            var scene = SceneManager.GetActiveScene();
            if (!scene.IsValid() || string.IsNullOrEmpty(scene.path)) throw new InvalidOperationException("장면을 먼저 저장해 주세요.");
            var transforms = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(false)).ToArray();
            var targets = transforms.Select(t => t.GetComponent<SoundTarget>()).Where(t => t && t.enabled)
                .OrderBy(t => t.id, StringComparer.Ordinal).Select(t => new DirectorTarget {
                    id = t.id, name = t.name, description = t.description, position = t.transform.position,
                    suggestedRadius = t.suggestedRadius,
                    materials = t.GetComponentsInChildren<Renderer>(false).Take(16).SelectMany(r => r.sharedMaterials)
                        .Where(m => m).Select(m => m.name).Distinct().Take(8).ToArray()
                }).ToArray();
            if (targets.Length == 0) throw new InvalidOperationException("사운드 대상이 없습니다. '현재 장면 준비' 또는 '선택 오브젝트를 대상으로 추가'를 눌러 주세요.");
            if (targets.Length > 24) throw new InvalidOperationException("첫 버전은 장면당 최대 24개 대상을 지원합니다.");
            if (targets.Any(t => string.IsNullOrWhiteSpace(t.id)) || targets.Select(t => t.id).Distinct().Count() != targets.Length)
                throw new InvalidOperationException("대상 ID가 없거나 중복됐습니다. '대상 ID 정리'를 눌러 주세요.");
            if (targets.Any(t => !DirectorRules.Range(t.suggestedRadius, 2, 150) || string.IsNullOrWhiteSpace(t.description)))
                throw new InvalidOperationException("각 대상에 설명과 2~150m 반경을 지정해 주세요.");
            var player = Player();
            var snapshot = new DirectorSnapshot { scenePath = scene.path, catalogRevision = SoundCatalog.Load().revision,
                objectCount = transforms.Length, targets = targets,
                sceneObjects = transforms.Select(t => t.name).Distinct().OrderBy(n => n, StringComparer.Ordinal).Take(160).ToArray(),
                currentPlan = player && player.profile ? player.profile.plan : new DirectionPlan() };
            using (var sha = SHA256.Create()) snapshot.revision = BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(JsonUtility.ToJson(snapshot))))
                .Replace("-", "").ToLowerInvariant();
            return snapshot;
        }
        public static void PrepareCurrent() {
            if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("장면 준비는 Play를 멈춘 뒤 실행해 주세요.");
            var scene = SceneManager.GetActiveScene();
            if (string.IsNullOrEmpty(scene.path)) throw new InvalidOperationException("장면을 먼저 저장해 주세요.");
            var player = Player();
            if (!player) {
                var root = new GameObject("Vesper Sound Director"); Undo.RegisterCreatedObjectUndo(root, "Add Sound Director");
                player = Undo.AddComponent<SoundDirectorPlayer>(root);
                Undo.AddComponent<DirectorOverlay>(root);
            }
            Undo.RecordObject(player, "Prepare Sound Director");
            player.existingAudio = UnityEngine.Object.FindObjectsByType<WwiseAudioBridge>().FirstOrDefault(b => b.gameObject.scene == scene);
            player.listener = player.existingAudio ? player.existingAudio.listener.transform : Camera.main ? Camera.main.transform : null;
#if VESPER_WWISE
            // AkInitializer makes its entire GameObject persistent. Keep the scene-scoped
            // director on a different root so its targets stay in the same scene.
            var attached = player.GetComponent<AkInitializer>();
            if (attached || !UnityEngine.Object.FindAnyObjectByType<AkInitializer>()) {
                var initRoot = new GameObject("Wwise Initializer"); Undo.RegisterCreatedObjectUndo(initRoot, "Add Wwise initializer");
                var initializer = Undo.AddComponent<AkInitializer>(initRoot);
                if (attached) { EditorUtility.CopySerialized(attached, initializer); Undo.DestroyObjectImmediate(attached); }
            }
#endif
            if (!player.profile) {
                Directory.CreateDirectory(Root + "/Profiles"); AssetDatabase.Refresh();
                string path = Root + "/Profiles/" + scene.name + "_Direction.asset";
                player.profile = AssetDatabase.LoadAssetAtPath<SoundDirectionProfile>(path);
                if (!player.profile) { player.profile = ScriptableObject.CreateInstance<SoundDirectionProfile>(); AssetDatabase.CreateAsset(player.profile, path); }
            }
            if (player.SceneTargets().Length == 0) {
                if (scene.path == W11) {
                    var starts = new[] { 0f, 55, 112, 168, 238, 303 };
                    var ends = new[] { 55f, 112, 168, 238, 303, 360 };
                    var descriptions = new[] {
                        "숲 초입과 강가. 아침의 편안한 산책, 나뭇잎과 새소리.",
                        "비가 시작되는 숲. 바람과 젖은 나무, 저녁으로 변하는 구간.",
                        "어두운 비 오는 숲. 폐허로 접근하는 길.",
                        "수도원 폐허와 돌길. 밤, 고립감, 불안한 정적과 바람.",
                        "설산으로 오르는 길. 밤, 차가운 바람, 눈이 시작됨.",
                        "눈 덮인 산길. 한밤중, 강한 추위와 먼 야생동물 소리."
                    };
                    for (int i = 0; i < starts.Length; i++) {
                        float middle = (starts[i] + ends[i]) / 2;
                        AddTarget(player.transform, W10.WorldLayout.Region(middle), W10.WorldLayout.Point(middle), descriptions[i], (ends[i] - starts[i]) * .85f);
                    }
                    AddTarget(player.transform, "River at Willowbank", player.existingAudio.lakeEmitter.transform.position,
                        "강과 호수의 물소리. 이 위치에 가까울 때만 들려야 하는 국소 수원.", 35);
                } else {
                    // Names are discovery hints, never treated as model instructions. Authors can edit every target.
                    var objects = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(false))
                        .Where(t => t.GetComponent<Renderer>() && Relevant(t.name)).Take(12).ToArray();
                    foreach (var obj in objects) AddToObject(obj.gameObject);
                    if (objects.Length == 0) AddTarget(player.transform, "Scene ambience", Vector3.zero,
                        "이 장면의 기본 환경음. 장면의 장소와 연출 의도를 설명해 주세요.", 40);
                }
            }
            EditorUtility.SetDirty(player); EditorSceneManager.MarkSceneDirty(scene); AssetDatabase.SaveAssets();
        }
        static bool Relevant(string name) {
            string lower = name.ToLowerInvariant();
            return new[] { "river", "lake", "pond", "forest", "grove", "ruin", "abbey", "snow", "water" }.Any(lower.Contains);
        }
        static SoundTarget AddTarget(Transform parent, string name, Vector3 point, string description, float radius) {
            var go = new GameObject(name); Undo.RegisterCreatedObjectUndo(go, "Add sound target");
            go.transform.SetParent(parent, false); go.transform.position = point;
            var target = go.AddComponent<SoundTarget>(); target.id = Guid.NewGuid().ToString("N");
            target.description = description; target.suggestedRadius = Mathf.Clamp(radius, 2, 150); return target;
        }
        public static void AddToObject(GameObject go) {
            if (!go || go.GetComponent<SoundTarget>()) return;
            var target = Undo.AddComponent<SoundTarget>(go); target.id = Guid.NewGuid().ToString("N"); target.description = go.name;
            EditorUtility.SetDirty(target); EditorSceneManager.MarkSceneDirty(go.scene);
        }
        public static void RepairIds() {
            var seen = new System.Collections.Generic.HashSet<string>();
            foreach (var target in UnityEngine.Object.FindObjectsByType<SoundTarget>().Where(t => t.gameObject.scene == SceneManager.GetActiveScene())) {
                if (!string.IsNullOrEmpty(target.id) && seen.Add(target.id)) continue;
                Undo.RecordObject(target, "Repair sound target ID"); target.id = Guid.NewGuid().ToString("N"); seen.Add(target.id); EditorUtility.SetDirty(target);
            }
            EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
        }
        public static void OpenLab() {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            if (File.Exists(Lab)) { EditorSceneManager.OpenScene(Lab); return; }
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var camera = new GameObject("Explorer", typeof(Camera), typeof(AudioListener), typeof(DirectorExplorer));
            camera.tag = "MainCamera"; camera.transform.position = new Vector3(0, 2, 12);
            camera.transform.rotation = Quaternion.Euler(12, 180, 0);
            camera.GetComponent<Camera>().backgroundColor = new Color(.09f, .14f, .19f);
            camera.GetComponent<Camera>().clearFlags = CameraClearFlags.SolidColor;
            var light = new GameObject("Sun", typeof(Light)); light.GetComponent<Light>().type = LightType.Directional;
            light.transform.rotation = Quaternion.Euler(50, -25, 0);
            CreatePrimitive("Ground", PrimitiveType.Cube, new Vector3(0, -.5f, -10), new Vector3(55, 1, 65), new Color(.17f, .23f, .2f));
            CreatePrimitive("Pond water", PrimitiveType.Cylinder, new Vector3(11, .05f, -6), new Vector3(11, .08f, 9), new Color(.15f, .48f, .56f));
            CreatePrimitive("Forest grove", PrimitiveType.Cylinder, new Vector3(-11, 3, -8), new Vector3(4, 3, 4), new Color(.1f, .3f, .2f));
            CreatePrimitive("Abbey ruins", PrimitiveType.Cube, new Vector3(0, 3, -30), new Vector3(10, 6, 2), new Color(.39f, .4f, .43f));
            for (int i = 0; i < 7; i++) CreatePrimitive("Tree " + i, PrimitiveType.Cylinder, new Vector3(-16 + (i % 3) * 5, 2, -12 - (i / 3) * 6), new Vector3(2, 2, 2), new Color(.12f, .27f, .17f));
            EditorSceneManager.SaveScene(scene, Lab); PrepareCurrent();
            foreach (var target in Player().SceneTargets()) {
                target.suggestedRadius = 22;
                target.description = target.name.Contains("Pond") ? "작은 연못과 흐르는 물. 가까이에서 들리는 국소 수원." :
                    target.name.Contains("Forest") ? "낮의 작은 숲. 편안한 새소리와 바람." : "숲 너머의 버려진 수도원. 고요하고 불안한 폐허.";
            }
            EditorSceneManager.SaveScene(scene); AssetDatabase.SaveAssets();
        }
        static void CreatePrimitive(string name, PrimitiveType type, Vector3 point, Vector3 scale, Color color) {
            var go = GameObject.CreatePrimitive(type); go.name = name; go.transform.position = point; go.transform.localScale = scale;
            Directory.CreateDirectory(Root + "/DemoMaterials"); AssetDatabase.Refresh();
            string path = Root + "/DemoMaterials/" + name.Replace(" ", "_") + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!material) { material = new Material(Shader.Find("Universal Render Pipeline/Lit")); material.color = color; AssetDatabase.CreateAsset(material, path); }
            go.GetComponent<Renderer>().sharedMaterial = material;
        }
    }
}
