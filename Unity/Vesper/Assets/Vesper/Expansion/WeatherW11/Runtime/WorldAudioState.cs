using UnityEngine;
using W10 = Vesper.Expansion.WeatherW10;

namespace Vesper.Expansion.WeatherW11 {
    [DefaultExecutionOrder(40)]
    public sealed class WorldAudioState : MonoBehaviour {
        public W10.WorldMotor motor;
        public W10.WorldEnvironment environment;
        public WorldAudioProfile profile;
        public AudioState Current { get; private set; }
        public bool Valid { get; private set; }
        public int Revision { get; private set; }
        int serial = -1;

        void OnEnable() { serial = -1; Valid = false; }
        void Update() { Refresh(); }

        public void Refresh() {
            if (!motor || !environment || !profile) { Valid = false; return; }
            var p = motor.transform.position;
            bool reset = serial != motor.ResetSerial;
            if (reset) { serial = motor.ResetSerial; Revision++; }
            bool grounded = motor.Ground(p, out var hit);
            float progress = -p.z;
            // Weather intensity stays global outdoors/under roofs. Shelter filtering is a separate concern.
            float rain = W10.WorldLayout.Weights(progress).y;
            Current = new AudioState {
                grounded = grounded,
                surface = grounded ? SurfaceAt(hit) : Current.surface,
                rainIntensity = Mathf.Clamp01(rain),
                timeOfDay = AudioModel.TimeAt(progress, profile.timeKeys),
                area = AudioModel.AreaAt(progress, Current.area, reset || !Valid,
                    profile.snowMountainBoundary, profile.areaHysteresis)
            };
            Valid = true;
        }

        public SurfaceType SurfaceAt(RaycastHit hit) {
            var tag = hit.collider.GetComponentInParent<SurfaceAudioTag>();
            if (tag) return tag.surface;
            var p = hit.point; float d = -p.z;
            if (W10.WorldLayout.SnowCover(p.x, d) >= profile.snowSurfaceThreshold) return SurfaceType.Snow;
            if (profile.regions != null) foreach (var region in profile.regions)
                if (d >= region.start && d < region.end && Mathf.Abs(p.x) <= region.halfWidth) return region.surface;
            return W10.WorldLayout.Weights(d).y >= profile.mudRainThreshold ? SurfaceType.Mud : SurfaceType.Gravel;
        }
    }
}
