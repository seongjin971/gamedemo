using UnityEngine;

namespace Vesper.Expansion.WeatherW11 {
    public sealed class WorldAudioDebug : MonoBehaviour {
        public WorldAudioState state;
        public WorldFootsteps footsteps;
        public WwiseAudioBridge bridge;
        public bool visible = true;
        void OnGUI() {
#if UNITY_EDITOR || DEVELOPMENT_BUILD
            if (!visible || !state || !state.Valid || !bridge || !footsteps) return;
            var s = state.Current;
            GUI.Box(new Rect(20, 70, 390, 150), "W11 Audio diagnostics");
            GUI.Label(new Rect(32, 98, 365, 110),
                $"{bridge.Status}\nSurface: {s.surface}    Area: {s.area}\n" +
                $"TimeOfDay: {s.timeOfDay:F2} (authored)    Rain: {s.rainIntensity:F2}\n" +
                $"Ground: {s.grounded}    Foot contacts: {footsteps.ContactCount}\n" +
                $"Wwise events: {bridge.PostedEvents}    Errors: {bridge.ErrorCount}");
#endif
        }
    }
}
