using UnityEngine;

namespace Vesper.SoundDirector {
    [CreateAssetMenu(menuName = "Vesper/Sound Direction Profile")]
    public sealed class SoundDirectionProfile : ScriptableObject {
        public DirectionPlan plan = new DirectionPlan();
        public string source = "None", model, createdUtc, prompt;
        public int requestMilliseconds;
        [HideInInspector] public string previousState;
    }
}
