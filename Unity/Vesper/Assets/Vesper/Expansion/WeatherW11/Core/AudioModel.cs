using System;

namespace Vesper.Expansion.WeatherW11 {
    public enum SurfaceType { Mud, Gravel, Snow, Rock }
    public enum AudioArea { Forest, SnowMountain }

    [Serializable]
    public struct TimeKey {
        public float progress, hour;
        public TimeKey(float progress, float hour) { this.progress = progress; this.hour = hour; }
    }

    public struct AudioState {
        public SurfaceType surface;
        public AudioArea area;
        public float timeOfDay, rainIntensity;
        public bool grounded;
    }

    public static class AudioModel {
        public static float Clamp(float value, float min, float max) {
            if (float.IsNaN(value) || float.IsInfinity(value)) return min;
            return Math.Max(min, Math.Min(max, value));
        }

        // Authors may use 25 for 01:00 after midnight. Interpolate before wrapping.
        public static float TimeAt(float progress, TimeKey[] keys) {
            if (keys == null || keys.Length == 0) return 12;
            float hour = keys[0].hour;
            for (int i = 1; i < keys.Length && progress > keys[i - 1].progress; i++) {
                float span = keys[i].progress - keys[i - 1].progress;
                float t = span > 0 ? Clamp((progress - keys[i - 1].progress) / span, 0, 1) : 1;
                t = t * t * (3 - 2 * t);
                hour = keys[i - 1].hour + (keys[i].hour - keys[i - 1].hour) * t;
            }
            if (float.IsNaN(hour) || float.IsInfinity(hour)) return 12;
            return (hour % 24 + 24) % 24;
        }

        public static AudioArea AreaAt(float progress, AudioArea previous, bool initialize,
            float boundary, float hysteresis) {
            if (initialize) return progress >= boundary ? AudioArea.SnowMountain : AudioArea.Forest;
            float margin = Math.Max(0, hysteresis);
            if (previous == AudioArea.Forest && progress >= boundary + margin) return AudioArea.SnowMountain;
            if (previous == AudioArea.SnowMountain && progress < boundary - margin) return AudioArea.Forest;
            return previous;
        }
    }

    // Tracks crossings, rather than playing repeatedly while a foot is near a contact phase.
    public sealed class FootstepClock {
        float previous;
        int resetSerial;
        bool primed;
        public void Reset() { primed = false; }

        public int Advance(float phase, bool moving, bool grounded, int serial,
            float leftContact, float rightContact) {
            phase = AudioModel.Clamp(phase, 0, 1);
            if (!primed || serial != resetSerial || !moving || !grounded) {
                previous = phase; resetSerial = serial; primed = true; return 0;
            }
            float end = phase < previous ? phase + 1 : phase;
            int mask = Crossed(previous, end, leftContact) ? 1 : 0;
            if (Crossed(previous, end, rightContact)) mask |= 2;
            previous = phase;
            return mask;
        }

        static bool Crossed(float start, float end, float contact) {
            contact = AudioModel.Clamp(contact, 0, .999999f);
            return (contact > start && contact <= end) || (contact + 1 > start && contact + 1 <= end);
        }
    }
}
