using System;
using System.Collections.Generic;
using System.Linq;

namespace Vesper.SoundDirector.Editor {
    public static class DirectorExamples {
        // Explicitly authored rehearsal fixtures. These never masquerade as live AI inference.
        public static PlannerResult Create(DirectorSnapshot snapshot, bool dramatic) {
            var layers = new List<DirectionLayer>();
            foreach (var target in snapshot.targets) {
                string hint = (target.name + " " + target.description).ToLowerInvariant();
                bool water = new[] { "river", "pond", "국소 수원", "호수" }.Any(hint.Contains);
                bool ruin = new[] { "abbey", "ruin", "폐허", "어두운" }.Any(hint.Contains);
                bool snow = new[] { "snow", "midnight", "눈 덮인", "설산" }.Any(hint.Contains);
                bool rain = new[] { "rain", "비가", "비 오는" }.Any(hint.Contains);
                Add(target, water ? "river" : snow ? "snow_bed" : dramatic && ruin ? "night_bed" : rain ? "rain_bed" : "day_wind",
                    water ? -12 : -17, water ? Math.Min(22, target.suggestedRadius) : target.suggestedRadius, 30,
                    water ? "수원 가까이에서만 물소리가 들리는 예제" : "장소별 환경음을 배치한 수동 작성 예제");
                if (!water && !rain && !snow) Add(target, dramatic && ruin ? "wolves" : "birds", dramatic && ruin ? -19 : -20,
                    target.suggestedRadius, dramatic && ruin ? 24 : 12, "분위기 차이를 확인하는 간헐적 자연음 예제");
            }
            return new PlannerResult { source = "Example · AI 아님", model = "authored-fixture", prompt = "수동 작성된 " + (dramatic ? "긴장감" : "편안한") + " 시연 예제",
                plan = new DirectionPlan { sceneRevision = snapshot.revision, summary = dramatic ? "숲에서 폐허로 갈수록 어두워지는 연출 · 수동 예제" : "편안한 자연음과 가까운 물소리 · 수동 예제",
                    layers = layers.Take(DirectorRules.MaxLayers).ToArray(), warnings = new[] { "이 계획은 AI가 생성하지 않은 기능 확인용 예제입니다." } } };
            void Add(DirectorTarget target, string sound, float gain, float radius, float interval, string reason) {
                layers.Add(new DirectionLayer { targetId = target.id, soundId = sound, gainDb = gain, radius = radius,
                    fadeSeconds = 2, intervalSeconds = interval, reason = reason });
            }
        }
    }
}
