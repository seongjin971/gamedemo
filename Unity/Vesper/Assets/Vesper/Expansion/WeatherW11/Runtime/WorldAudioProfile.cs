using System;
using UnityEngine;

namespace Vesper.Expansion.WeatherW11 {
    [Serializable]
    public struct SurfaceRegion {
        public string description;
        public float start, end, halfWidth;
        public SurfaceType surface;
    }

    [CreateAssetMenu(menuName = "Vesper/W11 Audio Profile")]
    public sealed class WorldAudioProfile : ScriptableObject {
        [Tooltip("Spatially authored audio time, not an elapsed game clock. Hours can exceed 24 across midnight.")]
        public TimeKey[] timeKeys = {
            new TimeKey(0, 8), new TimeKey(55, 17), new TimeKey(112, 20),
            new TimeKey(168, 21), new TimeKey(238, 22), new TimeKey(303, 23)
        };
        public float snowMountainBoundary = 270.5f;
        [Min(0)] public float areaHysteresis = 2;
        [Range(0, 1)] public float snowSurfaceThreshold = .55f;
        [Range(0, 1)] public float mudRainThreshold = .35f;
        [Tooltip("First matching region wins, after explicit collider tags and snow cover. Editable audio approximation of mixed terrain.")]
        public SurfaceRegion[] regions = {
            new SurfaceRegion { description = "Abbey stone trail", start = 168, end = 224, halfWidth = 2.3f, surface = SurfaceType.Rock }
        };
        [Range(0, 1)] public float leftWalkContact = .1f, rightWalkContact = .6f;
        [Range(0, 1)] public float leftRunContact = .1f, rightRunContact = .6f;
        public bool contactsCalibrated;
        [Min(.02f)] public float syncInterval = .05f;
        public string bankName = "Vesper_W11";
        public string footstepEvent = "Play_Footstep";
        public string ambienceEvent = "Play_World_Ambience";
        public string lakeEvent = "Play_Lake_Ambience";

        public bool Validate(out string error) {
            if (timeKeys == null || timeKeys.Length < 2) { error = "At least two time keys are required."; return false; }
            for (int i = 0; i < timeKeys.Length; i++) {
                if (!Finite(timeKeys[i].progress) || !Finite(timeKeys[i].hour) ||
                    (i > 0 && timeKeys[i].progress <= timeKeys[i - 1].progress)) {
                    error = "Time keys must be finite and strictly ordered by progress."; return false;
                }
            }
            if (string.IsNullOrWhiteSpace(bankName) || string.IsNullOrWhiteSpace(footstepEvent) ||
                string.IsNullOrWhiteSpace(ambienceEvent) || string.IsNullOrWhiteSpace(lakeEvent)) {
                error = "Bank and event names are required."; return false;
            }
            if (!Finite(snowMountainBoundary) || !Finite(areaHysteresis) || areaHysteresis < 0 ||
                !Finite(syncInterval) || syncInterval < .02f) { error = "Invalid area or sync settings."; return false; }
            foreach (var value in new[] { snowSurfaceThreshold, mudRainThreshold, leftWalkContact,
                rightWalkContact, leftRunContact, rightRunContact }) {
                if (!Finite(value) || value < 0 || value > 1) { error = "Surface thresholds and foot contacts must be in 0..1."; return false; }
            }
            if (regions != null) foreach (var r in regions) {
                if (!Finite(r.start) || !Finite(r.end) || !Finite(r.halfWidth) || r.end <= r.start || r.halfWidth <= 0) {
                    error = "Surface regions need a positive width and ordered finite bounds."; return false;
                }
            }
            error = null; return true;
        }
        static bool Finite(float v) { return !float.IsNaN(v) && !float.IsInfinity(v); }
    }
}
