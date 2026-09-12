using System;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace Vesper.Expansion.Editor {
    public static class AdventurerPortrait {
        static Camera camera; static RenderTexture target; static string output; static int frame, index;
        static AdventurerMotor actor;
        static Material original, unlit; static int cleanupFrames;
        public static void Run() {
            output = Path.GetFullPath(AdventurerBuild.Arg("-p1Output", "../../Migration/Evidence/Expansion/P1/portrait-01")); Directory.CreateDirectory(output);
            EditorSceneManager.OpenScene(AdventurerBuild.Scene);
            actor = UnityEngine.Object.FindAnyObjectByType<AdventurerMotor>();
            camera = Camera.main;
            target = new RenderTexture(1536, 1024, 24); target.Create(); camera.targetTexture = target; camera.aspect = 1.5f;
            original = actor.GetComponentInChildren<SkinnedMeshRenderer>().sharedMaterial;
            unlit = new Material(Shader.Find("Universal Render Pipeline/Unlit")); unlit.SetTexture("_BaseMap", original.GetTexture("_BaseMap"));
            index = 0; Setup(); EditorApplication.update += Tick;
        }
        static void Setup() {
            frame = 0;
            var focus = actor.transform.position + Vector3.up * 1.6f;
            camera.orthographicSize = 2.2f;
            camera.transform.position = focus + new Vector3(index == 1 ? -2.4f : 2.4f, 1.3f, index == 1 ? -4 : 4);
            camera.transform.LookAt(focus);
            foreach (var r in actor.GetComponentsInChildren<SkinnedMeshRenderer>()) r.sharedMaterial = index == 2 ? unlit : original;
            foreach (var billboard in UnityEngine.Object.FindObjectsByType<VesperBillboard>()) billboard.transform.rotation = camera.transform.rotation;
        }
        static void Tick() {
            try {
                EditorApplication.QueuePlayerLoopUpdate(); if (++frame < 20) return;
                RenderPipeline.SubmitRenderRequest(camera, new UniversalRenderPipeline.SingleCameraRequest { destination = target });
                if (frame < 25) return;
                RenderTexture.active = target; var tex = new Texture2D(1536, 1024, TextureFormat.RGB24, false);
                tex.ReadPixels(new Rect(0, 0, 1536, 1024), 0, 0); tex.Apply();
                File.WriteAllBytes(output + "/" + new[] { "back-lit", "front-lit", "back-albedo" }[index] + ".png", tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex); RenderTexture.active = null;
                if (++index < 3) { Setup(); return; }
                EditorApplication.update -= Tick;
                foreach (var r in actor.GetComponentsInChildren<SkinnedMeshRenderer>()) r.sharedMaterial = original;
                camera.targetTexture = null; RenderTexture.active = null;
                var reflection = UnityEngine.Object.FindAnyObjectByType<VesperPlanarReflection>();
                if (reflection) reflection.enabled = false;
                target.Release(); UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(unlit);
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                cleanupFrames = 0; EditorApplication.update += Finish;
            } catch (Exception e) { Debug.LogException(e); EditorApplication.update -= Tick; EditorApplication.Exit(1); }
        }
        static void Finish() {
            EditorApplication.QueuePlayerLoopUpdate();
            if (++cleanupFrames < 30) return;
            EditorApplication.update -= Finish;
            File.WriteAllText(output + "/portrait-complete.json", "{\"views\":3,\"sceneSaved\":false,\"resourcesReleased\":true}");
            Debug.Log("P1_PORTRAIT_PASS"); EditorApplication.Exit(0);
        }
    }
}
