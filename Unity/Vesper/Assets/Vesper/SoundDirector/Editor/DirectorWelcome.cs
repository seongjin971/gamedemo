using UnityEditor;
using UnityEngine;

namespace Vesper.SoundDirector.Editor {
    [InitializeOnLoad]
    public static class DirectorWelcome {
        static DirectorWelcome() { if (!Application.isBatchMode && !AssetDatabase.IsAssetImportWorkerProcess()) EditorApplication.update += ShowOnce; }
        static void ShowOnce() {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return;
            EditorApplication.update -= ShowOnce;
            string key = "Vesper.SoundDirector.Welcome.1." + Application.dataPath;
            if (EditorPrefs.GetBool(key, false)) return;
            EditorPrefs.SetBool(key, true); SoundDirectorWindow.Open();
        }
    }
}
