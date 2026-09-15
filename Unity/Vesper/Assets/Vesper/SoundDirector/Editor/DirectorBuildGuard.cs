using System;
using System.IO;
using System.Linq;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.SceneManagement;
using Vesper.Expansion.WeatherW11.Editor;

namespace Vesper.SoundDirector.Editor {
    public sealed class DirectorBuildGuard : IProcessSceneWithReport {
        public int callbackOrder => 20;
        public void OnProcessScene(Scene scene, BuildReport report) {
            if (report == null) return;
            foreach (var player in scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<SoundDirectorPlayer>(false))) {
                if (!player.enabled || !player.profile || player.profile.plan.layers.Length == 0) continue;
#if !VESPER_WWISE
                throw new BuildFailedException("Sound Director requires VESPER_WWISE and the native Wwise Integration.");
#else
                string platform = WeatherW11Setup.BankPlatform(report.summary.platform);
                var targets = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<SoundTarget>(false)).Where(t => t.enabled)
                    .Select(t => new DirectorTarget { id = t.id }).ToArray();
                var errors = DirectorRules.Validate(player.profile.plan, new DirectorSnapshot { targets = targets }, SoundCatalog.Load(), false);
                if (errors.Length > 0) throw new BuildFailedException(string.Join("\n", errors));
                if (!player.listener) throw new BuildFailedException("Director listener is missing in " + scene.name);
                string folder = "Assets/StreamingAssets/Audio/GeneratedSoundBanks/" + platform;
                foreach (var bank in new[] { "Init", "Vesper_W11", "Vesper_Director" }) WeatherW11Setup.ValidateBankFile(folder + "/" + bank + ".bnk");
                string metadata = File.ReadAllText(folder + "/Vesper_Director.json");
                foreach (var layer in player.profile.plan.layers) {
                    string name = SoundCatalog.Load().Find(layer.soundId).eventName;
                    if (!metadata.Contains("\"" + name + "\"")) throw new BuildFailedException("Director bank event is missing: " + name);
                }
#endif
            }
        }
    }
}
