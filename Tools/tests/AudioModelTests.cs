using System;
using Vesper.Expansion.WeatherW11;

public static class AudioModelTests {
    static int assertions;
    static void Check(bool result, string name) {
        assertions++;
        if (!result) throw new Exception(name);
    }
    static void Near(float actual, float expected, string name) { Check(Math.Abs(actual - expected) < .001f, name); }

    public static int Main() {
        try {
            var keys = new[] { new TimeKey(0, 8), new TimeKey(100, 20), new TimeKey(200, 25) };
            Near(AudioModel.TimeAt(-10, keys), 8, "before first key");
            Near(AudioModel.TimeAt(50, keys), 14, "smooth midpoint");
            Near(AudioModel.TimeAt(100, keys), 20, "exact time key");
            Near(AudioModel.TimeAt(250, keys), 1, "after final key and midnight wrap");
            Near(AudioModel.TimeAt(150, keys), 22.5f, "midnight interpolation follows authored direction");
            Near(AudioModel.TimeAt(0, null), 12, "missing timeline fallback");
            Near(AudioModel.Clamp(float.NaN, 0, 1), 0, "NaN excluded from RTPC");
            Near(AudioModel.Clamp(4, 0, 1), 1, "upper RTPC clamp");

            var area = AudioModel.AreaAt(269, AudioArea.Forest, true, 270.5f, 2);
            foreach (float p in new[] { 270f, 271f, 269.8f, 272f }) {
                area = AudioModel.AreaAt(p, area, false, 270.5f, 2);
                Check(area == AudioArea.Forest, "no border chatter entering snow");
            }
            area = AudioModel.AreaAt(273, area, false, 270.5f, 2);
            Check(area == AudioArea.SnowMountain, "enter snow beyond margin");
            area = AudioModel.AreaAt(269, area, false, 270.5f, 2);
            Check(area == AudioArea.SnowMountain, "no border chatter returning");
            area = AudioModel.AreaAt(268, area, false, 270.5f, 2);
            Check(area == AudioArea.Forest, "return to forest");
            Check(AudioModel.AreaAt(0, AudioArea.SnowMountain, true, 270.5f, 2) == AudioArea.Forest, "R reset restores area immediately");

            foreach (int fps in new[] { 15, 30, 60, 144 }) {
                var clock = new FootstepClock(); int contacts = 0;
                clock.Advance(0, true, true, 0, .1f, .6f);
                for (int i = 1; i <= fps * 5; i++) {
                    float phase = (i / (float)fps) % 1;
                    int mask = clock.Advance(phase, true, true, 0, .1f, .6f);
                    contacts += ((mask & 1) != 0 ? 1 : 0) + ((mask & 2) != 0 ? 1 : 0);
                }
                Check(contacts == 10, "two steps per cycle at " + fps + " FPS");
                Check(clock.Advance(.6f, false, true, 0, .1f, .6f) == 0, "idle is silent");
                Check(clock.Advance(.9f, true, false, 0, .1f, .6f) == 0, "unsupported player is silent");
                Check(clock.Advance(0, true, true, 1, .1f, .6f) == 0, "teleport creates no synthetic step");
                Check(clock.Advance(.1f, true, true, 1, .1f, .6f) == 1, "contact resumes after reset");
                Check(clock.Advance(.1f, true, true, 1, .1f, .6f) == 0, "same contact cannot replay");
            }
            Console.WriteLine("PASS: " + assertions + " audio model assertions"); return 0;
        } catch (Exception e) { Console.Error.WriteLine("FAIL: " + e.Message); return 1; }
    }
}
