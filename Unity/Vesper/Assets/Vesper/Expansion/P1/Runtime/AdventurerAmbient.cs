using UnityEngine;
using UnityEngine.Rendering;

namespace Vesper.Expansion {
    // A modest character-only ambient probe supplement keeps cloth/hair readable
    // in the tree shadow. It neither changes courtyard lights nor emits bloom.
    [ExecuteAlways]
    public sealed class AdventurerAmbient : MonoBehaviour {
        void OnEnable() { Apply(); }
        public void Apply() {
            var probe = RenderSettings.ambientProbe;
            probe.AddAmbientLight(new Color(.14f, .16f, .18f));
            var block = new MaterialPropertyBlock();
            block.CopySHCoefficientArraysFrom(new[] { probe });
            foreach (var skin in GetComponentsInChildren<SkinnedMeshRenderer>()) {
                skin.lightProbeUsage = LightProbeUsage.CustomProvided;
                skin.SetPropertyBlock(block);
            }
        }
    }
}
