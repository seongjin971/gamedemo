using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.SceneManagement;
using UnityEngine;
using System.IO;
using System.Linq;
namespace Vesper.Expansion.P2.Editor {
public static class Setup {
 static UnityEditor.PackageManager.Requests.AddRequest request;
 public static void Install(){request=Client.Add("com.unity.ai.navigation@2.0.14"); EditorApplication.update+=Poll;}
 static void Poll(){if(!request.IsCompleted)return; EditorApplication.update-=Poll; File.WriteAllText("../../Migration/Evidence/Expansion/P2/package-install.txt",request.Status+" "+(request.Result?.packageId ?? request.Error?.message)); EditorApplication.Exit(request.Status==StatusCode.Success?0:1);}
 public static void Inspect(){EditorSceneManager.OpenScene("Assets/Vesper/Scenes/Expansion/VesperAdventurerRun.unity"); File.WriteAllLines("../../Migration/Evidence/Expansion/P2/scene-inventory.txt",Object.FindObjectsByType<Transform>().Select(t=>t.name+" | "+t.position+" | "+string.Join(",",t.GetComponents<Component>().Select(c=>c?c.GetType().Name:"MISSING")))); EditorApplication.Exit(0);}
}}
