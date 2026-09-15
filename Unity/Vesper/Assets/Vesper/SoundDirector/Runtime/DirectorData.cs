using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Vesper.SoundDirector {
    [Serializable] public sealed class SoundFile { public string path, sha256; public float seconds; }
    [Serializable] public sealed class CatalogSound {
        public string id, description, eventName;
        public bool loop, available;
        public SoundFile[] files;
    }
    [Serializable] public sealed class SoundCatalog {
        public int version;
        public string revision, bankName, mediaBankName;
        public CatalogSound[] sounds;
        public CatalogSound Find(string id) => sounds?.FirstOrDefault(s => s.id == id);
        public static SoundCatalog Load() {
            var asset = Resources.Load<TextAsset>("VesperSoundCatalog");
            if (!asset) throw new InvalidOperationException("Vesper sound catalog is missing.");
            return JsonUtility.FromJson<SoundCatalog>(asset.text);
        }
    }
    [Serializable] public sealed class DirectorTarget {
        public string id, name, description;
        public Vector3 position;
        public float suggestedRadius;
        public string[] materials;
    }
    [Serializable] public sealed class DirectorSnapshot {
        public string scenePath, revision, catalogRevision;
        public int objectCount;
        public string[] sceneObjects;
        public DirectorTarget[] targets;
        public DirectionPlan currentPlan;
    }
    [Serializable] public sealed class DirectionLayer {
        public string targetId, soundId, reason;
        public float gainDb, radius, fadeSeconds, intervalSeconds;
    }
    [Serializable] public sealed class DirectionPlan {
        public int version = 1;
        public string sceneRevision, summary;
        public DirectionLayer[] layers = Array.Empty<DirectionLayer>();
        public string[] warnings = Array.Empty<string>();
    }
    public static class DirectorRules {
        public const int MaxLayers = 24;
        public static string[] Validate(DirectionPlan plan, DirectorSnapshot scene, SoundCatalog catalog, bool checkRevision = true) {
            var errors = new List<string>();
            if (plan == null || scene?.targets == null || catalog?.sounds == null) return new[] { "계획 또는 장면/사운드 목록이 없습니다." };
            if (plan.version != 1) errors.Add("지원하지 않는 계획 버전입니다.");
            if (checkRevision && plan.sceneRevision != scene.revision) errors.Add("장면이나 적용된 계획이 바뀌었습니다. 다시 분석해 주세요.");
            if (string.IsNullOrWhiteSpace(plan.summary) || plan.summary.Length > 2000) errors.Add("연출 설명이 비어 있거나 너무 깁니다.");
            if (scene.targets.Any(t => string.IsNullOrEmpty(t.id)) || scene.targets.Select(t => t.id).Distinct().Count() != scene.targets.Length)
                errors.Add("장면 대상 ID가 없거나 중복됩니다. 대상 설정을 확인해 주세요.");
            if (plan.layers == null || plan.layers.Length == 0 || plan.layers.Length > MaxLayers) {
                errors.Add("사운드 레이어는 1~24개여야 합니다."); return errors.ToArray();
            }
            var pairs = new HashSet<string>();
            var counts = new Dictionary<string, int>();
            foreach (var layer in plan.layers) {
                if (layer == null) { errors.Add("빈 레이어가 있습니다."); continue; }
                var target = scene.targets.FirstOrDefault(t => t.id == layer.targetId);
                if (target == null) errors.Add("장면에 없는 대상: " + layer.targetId);
                var sound = catalog.Find(layer.soundId);
                if (sound == null || !sound.available || string.IsNullOrEmpty(sound.eventName)) errors.Add("사용할 수 없는 사운드: " + layer.soundId);
                if (!Range(layer.gainDb, -48, -3)) errors.Add("볼륨은 -48~-3 dB 범위여야 합니다.");
                if (!Range(layer.radius, 2, 150)) errors.Add("청취 반경은 2~150 m 범위여야 합니다.");
                if (!Range(layer.fadeSeconds, .25f, 10)) errors.Add("전환 시간은 0.25~10초 범위여야 합니다.");
                if (!Range(layer.intervalSeconds, 3, 120)) errors.Add("재생 간격은 3~120초 범위여야 합니다.");
                if (string.IsNullOrWhiteSpace(layer.reason) || layer.reason.Length > 1000) errors.Add("각 선택에는 짧은 이유가 필요합니다.");
                var key = layer.targetId ?? "";
                if (!pairs.Add(key + ":" + layer.soundId)) errors.Add("같은 대상에 같은 사운드가 중복됐습니다.");
                counts[key] = counts.TryGetValue(key, out int count) ? count + 1 : 1;
                if (counts[key] > 3) errors.Add("한 대상에는 최대 3개 레이어를 사용할 수 있습니다.");
            }
            return errors.Distinct().ToArray();
        }
        public static bool Range(float value, float min, float max) => !float.IsNaN(value) && !float.IsInfinity(value) && value >= min && value <= max;
        // Flat center followed by a smooth falloff. A layer reaches silence at its declared radius.
        public static float DistanceGain(float distance, float radius) {
            if (radius <= 0 || distance >= radius) return 0;
            float t = Mathf.Clamp01((distance / radius - .2f) / .8f);
            return 1 - t * t * (3 - 2 * t);
        }
        public static float Db(float amplitude) => amplitude <= .00001585f ? -96 : Mathf.Clamp(20 * Mathf.Log10(amplitude), -96, 0);
    }
}
