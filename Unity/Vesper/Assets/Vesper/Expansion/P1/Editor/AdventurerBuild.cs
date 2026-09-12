using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine.Rendering;

namespace Vesper.Expansion.Editor {
    public static class AdventurerBuild {
        public const string Root = "Assets/Vesper/Expansion/P1";
        public const string Scene = "Assets/Vesper/Scenes/Expansion/VesperAdventurerP1.unity";
        public static string Arg(string key, string fallback) {
            var args = Environment.GetCommandLineArgs(); int i = Array.IndexOf(args, key);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : fallback;
        }
        [Serializable] class CharacterReport {
            public string scene,model; public int skins,bones,triangles,missingScripts;
            public Vector3 baselinePosition,baselineSize,newSize; public string[] clips;
        }
        [Serializable] class BuildReportData {
            public string result; public int errors,warnings; public double seconds; public string[] messages;
        }
        public static void Prepare() {
            try {
                Directory.CreateDirectory(Root + "/Materials");
                Directory.CreateDirectory("Assets/Vesper/Scenes/Expansion");
                AssetDatabase.Refresh();
                string modelPath = Root + "/Art/Adventurer.fbx";
                var importer = (ModelImporter)AssetImporter.GetAtPath(modelPath);
                if (importer == null) throw new Exception("Prepared adventurer FBX is missing");
                importer.animationType = ModelImporterAnimationType.Generic;
                importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                importer.materialImportMode = ModelImporterMaterialImportMode.None;
                importer.animationCompression = ModelImporterAnimationCompression.Off;
                importer.importCameras = false; importer.importLights = false;
                importer.importAnimation = true; importer.preserveHierarchy = true;
                importer.SaveAndReimport();
                var clips = importer.defaultClipAnimations;
                foreach (var clip in clips) {
                    clip.name = clip.takeName.Contains("Idle") ? "Idle" : "Walk";
                    clip.loopTime = true; clip.loopPose = false;
                    clip.lockRootRotation = true; clip.lockRootHeightY = true; clip.lockRootPositionXZ = true;
                }
                importer.clipAnimations = clips; importer.SaveAndReimport();
                Texture2D Texture(string filename, bool normal = false, bool linear = false) {
                    string path = Root + "/Art/" + filename;
                    var imp = (TextureImporter)AssetImporter.GetAtPath(path);
                    if (imp == null) throw new Exception("Missing texture " + path);
                    imp.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                    imp.sRGBTexture = !normal && !linear; imp.maxTextureSize = 2048;
                    imp.mipmapEnabled = true; imp.SaveAndReimport();
                    return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                }
                string materialPath = Root + "/Materials/Traveler.mat";
                var mat = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
                if (!mat) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, materialPath); }
                mat.SetTexture("_BaseMap", Texture("Albedo.png")); mat.SetColor("_BaseColor", Color.white);
                mat.SetTexture("_BumpMap", Texture("Normal.png", true)); mat.SetFloat("_BumpScale", .40f); mat.EnableKeyword("_NORMALMAP");
                mat.SetTexture("_MetallicGlossMap", Texture("MetallicSmoothness.png", false, true));
                mat.SetFloat("_Metallic", 0); mat.SetFloat("_Smoothness", .45f); mat.EnableKeyword("_METALLICSPECGLOSSMAP");
                EditorUtility.SetDirty(mat);

                // Save a new scene before touching any object. Referenced courtyard assets stay read-only.
                var scene = EditorSceneManager.OpenScene("Assets/Vesper/Scenes/VesperAtmosphereV2.unity");
                EditorSceneManager.SaveScene(scene, Scene, false);
                var old = UnityEngine.Object.FindAnyObjectByType<VesperKnight>();
                if (!old) throw new Exception("Accepted scene has no baseline knight");
                var bounds = old.GetComponentsInChildren<Renderer>().First().bounds;
                foreach (var r in old.GetComponentsInChildren<Renderer>()) bounds.Encapsulate(r.bounds);
                var home = old.home; var spawn = old.transform.position;
                UnityEngine.Object.DestroyImmediate(old.gameObject);
                var go = new GameObject("P1 novice adventurer"); go.transform.position = spawn; go.transform.rotation = Quaternion.Euler(0, 180, 0);
                var motor = go.AddComponent<AdventurerMotor>(); motor.home = home;
                var visual = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(modelPath));
                visual.name = "Traveler visual"; visual.transform.SetParent(go.transform, false);
                const float courtyardScale = 1.8f;
                visual.transform.localScale = Vector3.one * courtyardScale;
                var skins = visual.GetComponentsInChildren<SkinnedMeshRenderer>();
                foreach (var skin in skins) {
                    skin.sharedMaterials = Enumerable.Repeat(mat, skin.sharedMesh.subMeshCount).ToArray();
                    skin.shadowCastingMode = ShadowCastingMode.On; skin.receiveShadows = true;
                    skin.updateWhenOffscreen = true;
                }
                var animator = visual.GetComponent<Animator>(); if (!animator) animator = visual.AddComponent<Animator>();
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                var animations = AssetDatabase.LoadAllAssetsAtPath(modelPath).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__")).ToArray();
                var motion = visual.AddComponent<AdventurerAnimation>(); motion.animator = animator; motion.motor = motor;
                motion.idleClip = animations.First(c => c.name == "Idle"); motion.walkClip = animations.First(c => c.name == "Walk");
                string calibration = Path.GetFullPath("../../Migration/Source/Expansion/P1/animation-calibration.json");
                if (File.Exists(calibration)) motion.authoredWalkSpeed = JsonUtility.FromJson<Calibration>(File.ReadAllText(calibration)).walkSpeed;
                motor.walkSpeed = motion.authoredWalkSpeed;
                motion.authoredWalkSpeed *= courtyardScale; motor.walkSpeed = 2.25f;
                visual.AddComponent<AdventurerAmbient>();
                // Store a natural idle pose in the scene for read-only comparison captures.
                motion.idleClip.SampleAnimation(visual, 0);
                var cam = Camera.main; var previous = cam.GetComponent<VesperOrbitCamera>();
                var target = previous.homeTarget; var size = previous.homeSize;
                UnityEngine.Object.DestroyImmediate(previous);
                var control = cam.gameObject.AddComponent<AdventurerCamera>(); control.player = motor; control.homeTarget = target; control.homeSize = size;
                var newBounds = skins[0].bounds; foreach (var skin in skins) newBounds.Encapsulate(skin.bounds);
                var report = new CharacterReport { scene = Scene, model = modelPath, baselinePosition = spawn, baselineSize = bounds.size,
                    newSize = newBounds.size, skins = skins.Length, bones = skins.Sum(s => s.bones.Length), triangles = skins.Sum(s => s.sharedMesh.triangles.Length / 3),
                    clips = animations.Select(c => c.name + " " + c.length.ToString("F3") + "s").ToArray(),
                    missingScripts = UnityEngine.Object.FindObjectsByType<Transform>().Sum(t => GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)) };
                AssetDatabase.SaveAssets(); EditorSceneManager.SaveScene(scene);
                string output = Path.GetFullPath(Arg("-p1Output", "../../Migration/Evidence/Expansion/P1/candidate-01"));
                Directory.CreateDirectory(output); File.WriteAllText(output + "/character-import.json", JsonUtility.ToJson(report, true));
                Debug.Log("P1_PREPARE_PASS " + JsonUtility.ToJson(report)); EditorApplication.Exit(0);
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
        [Serializable] class Calibration { public float walkSpeed = 1.55f; }
        public static void Build() {
            string output = Path.GetFullPath(Arg("-p1Player", "Builds/VesperExpansion/VesperAdventurer.exe"));
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { Scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.StrictMode });
            var data = new BuildReportData { result = report.summary.result.ToString(), errors = report.summary.totalErrors, warnings = report.summary.totalWarnings,
                seconds = report.summary.totalTime.TotalSeconds,
                messages = report.steps.SelectMany(s => s.messages).Where(m => m.type == LogType.Warning || m.type == LogType.Error).Select(m => m.content).Distinct().ToArray() };
            File.WriteAllText(Path.Combine(Path.GetDirectoryName(output), "build-report.json"), JsonUtility.ToJson(data, true));
            Debug.Log("P1_BUILD_" + report.summary.result); EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
        }
    }
}
