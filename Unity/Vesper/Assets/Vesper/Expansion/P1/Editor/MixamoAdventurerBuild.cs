using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Vesper.Expansion.Editor {
    // Additive P1 motion revision. Never rewrites the delivered P1/candidate58 scene.
    public static class MixamoAdventurerBuild {
        public const string Scene = "Assets/Vesper/Scenes/Expansion/VesperAdventurerMixamo.unity";
        const string Art = "Assets/Vesper/Expansion/P1Mixamo/Art/Adventurer.fbx";
        [Serializable] class Calibration { public float walkSpeed; }
        [Serializable] class ImportReport {
            public string scene, model, walk; public int skins, bones, triangles, missingScripts;
            public float authoredSpeed; public string[] clips;
        }
        public static void Prepare() {
            try {
                AssetDatabase.Refresh();
                var importer = (ModelImporter)AssetImporter.GetAtPath(Art);
                if (!importer) throw new Exception("Prepared Mixamo derivative is missing");
                importer.animationType = ModelImporterAnimationType.Generic;
                importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
                importer.materialImportMode = ModelImporterMaterialImportMode.None;
                importer.animationCompression = ModelImporterAnimationCompression.Off;
                importer.importCameras = false; importer.importLights = false;
                importer.importAnimation = true; importer.preserveHierarchy = true;
                importer.SaveAndReimport();
                var specs = importer.defaultClipAnimations;
                foreach (var clip in specs) {
                    string take = clip.takeName;
                    clip.name = take.Contains("WalkAlternative") ? "WalkAlternative" : take.Contains("Idle") ? "Idle" : take.Contains("Stop") ? "Stop" : "Walk";
                    clip.loopTime = clip.name != "Stop"; clip.loopPose = false;
                    clip.lockRootRotation = clip.lockRootHeightY = clip.lockRootPositionXZ = true;
                }
                importer.clipAnimations = specs; importer.SaveAndReimport();
                var scene = EditorSceneManager.OpenScene(AdventurerBuild.Scene);
                EditorSceneManager.SaveScene(scene, Scene, false);
                var motor = UnityEngine.Object.FindAnyObjectByType<AdventurerMotor>();
                var previous = motor.GetComponentInChildren<AdventurerAnimation>();
                var material = previous.GetComponentInChildren<SkinnedMeshRenderer>().sharedMaterial;
                var scale = previous.transform.localScale;
                UnityEngine.Object.DestroyImmediate(previous.gameObject);
                var visual = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Art));
                visual.name = "Mixamo traveler visual"; visual.transform.SetParent(motor.transform, false); visual.transform.localScale = scale;
                var skins = visual.GetComponentsInChildren<SkinnedMeshRenderer>();
                foreach (var skin in skins) {
                    skin.sharedMaterials = Enumerable.Repeat(material, skin.sharedMesh.subMeshCount).ToArray();
                    skin.updateWhenOffscreen = true;
                }
                var animator = visual.GetComponent<Animator>(); if (!animator) animator = visual.AddComponent<Animator>();
                animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                var clips = AssetDatabase.LoadAllAssetsAtPath(Art).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__")).ToArray();
                var motion = visual.AddComponent<AdventurerAnimation>(); motion.motor = motor; motion.animator = animator;
                string selected = AdventurerBuild.Arg("-mixamoWalk", "Walk");
                motion.idleClip = clips.First(c => c.name == "Idle"); motion.walkClip = clips.First(c => c.name == selected);
                var calibration = JsonUtility.FromJson<Calibration>(File.ReadAllText("../../Migration/Source/Expansion/P1-Mixamo/prepared-01/calibration.json"));
                if (calibration.walkSpeed < .1f) throw new Exception("Invalid Mixamo stride calibration");
                motion.authoredWalkSpeed = calibration.walkSpeed * scale.x;
                visual.AddComponent<AdventurerAmbient>();
                motion.idleClip.SampleAnimation(visual, 0);
                AssetDatabase.SaveAssets(); EditorSceneManager.SaveScene(scene);
                string output = Path.GetFullPath(AdventurerBuild.Arg("-p1Output", "../../Migration/Evidence/Expansion/P1-Mixamo/candidate-01"));
                Directory.CreateDirectory(output);
                File.WriteAllText(Path.Combine(output, "character-import.json"), JsonUtility.ToJson(new ImportReport {
                    scene = Scene, model = Art, walk = selected, skins = skins.Length, bones = skins.Sum(s => s.bones.Length),
                    triangles = skins.Sum(s => s.sharedMesh.triangles.Length / 3), authoredSpeed = motion.authoredWalkSpeed,
                    clips = clips.Select(c => c.name + " " + c.length.ToString("F3") + "s").ToArray(),
                    missingScripts = UnityEngine.Object.FindObjectsByType<Transform>().Sum(t => GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject))
                }, true));
                Debug.Log("MIXAMO_PREPARE_PASS"); EditorApplication.Exit(0);
            } catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
        }
        [Serializable] class BuildData { public string result; public int errors, warnings; public double seconds; public string[] messages; }
        public static void Build() {
            string output = Path.GetFullPath("Builds/VesperMixamo/VesperMixamo.exe"); Directory.CreateDirectory(Path.GetDirectoryName(output));
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { Scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.StrictMode });
            File.WriteAllText(Path.Combine(Path.GetDirectoryName(output), "build-report.json"), JsonUtility.ToJson(new BuildData {
                result = report.summary.result.ToString(), errors = report.summary.totalErrors, warnings = report.summary.totalWarnings,
                seconds = report.summary.totalTime.TotalSeconds,
                messages = report.steps.SelectMany(s => s.messages).Where(m => m.type == LogType.Error || m.type == LogType.Warning).Select(m => m.content).Distinct().ToArray()
            }, true));
            Debug.Log("MIXAMO_BUILD_" + report.summary.result); EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
        }
    }
}
