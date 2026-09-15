using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Vesper.Expansion.WeatherW11;

namespace Vesper.SoundDirector {
    [DisallowMultipleComponent, DefaultExecutionOrder(90)]
    public sealed class SoundDirectorPlayer : MonoBehaviour {
        public SoundDirectionProfile profile;
        public Transform listener;
        public WwiseAudioBridge existingAudio;
        public bool useDirection = true;
        public bool Ready { get; private set; }
        public string Status { get; private set; } = "계획을 적용하면 재생됩니다.";
        public int PostedEvents { get; private set; }
        public int ErrorCount { get; private set; }
        public float Mix { get; private set; }
        public int LayerCount => voices.Count;
        sealed class Voice {
            public DirectionLayer layer;
            public CatalogSound sound;
            public SoundTarget target;
            public GameObject emitter;
            public float envelope, nextShot;
        }
        readonly List<Voice> voices = new List<Voice>();
        SoundCatalog catalog;
        string loadedPlan;
        bool initializing;
        float nextPlanCheck;
#if VESPER_WWISE
        uint bankId, initId, mediaId;
        bool ownsBank, ownsInit, ownsMedia;
#endif
        void OnEnable() { Reload(); }
        public void Reload() {
            StopAllCoroutines(); initializing = false;
            Release();
            if (!profile || profile.plan?.layers == null || profile.plan.layers.Length == 0) {
                Status = "계획을 적용하면 재생됩니다."; return;
            }
            StartCoroutine(Initialize());
        }
        IEnumerator Initialize() {
            initializing = true;
            catalog = SoundCatalog.Load();
            var targets = SceneTargets();
            var snapshot = new DirectorSnapshot { targets = targets.Select(t => new DirectorTarget { id = t.id }).ToArray() };
            var errors = DirectorRules.Validate(profile.plan, snapshot, catalog, false);
            if (errors.Length > 0) { Fail(string.Join(" / ", errors)); yield break; }
            if (existingAudio && existingAudio.listener) listener = existingAudio.listener.transform;
            if (!listener && Camera.main) listener = Camera.main.transform;
            if (!listener) { Fail("청취자 또는 Main Camera가 없습니다."); yield break; }
#if VESPER_WWISE
            float deadline = Time.realtimeSinceStartup + 15;
            while ((!AkUnitySoundEngine.IsInitialized() || (existingAudio && !existingAudio.Ready)) && Time.realtimeSinceStartup < deadline) yield return null;
            if (!AkUnitySoundEngine.IsInitialized() || (existingAudio && !existingAudio.Ready)) { Fail("Wwise 연결 시간이 초과됐습니다."); yield break; }
            var init = AkUnitySoundEngine.LoadBank("Init", out initId);
            ownsInit = init == AKRESULT.AK_Success;
            if (!ownsInit && init != AKRESULT.AK_BankAlreadyLoaded) { Fail("Init SoundBank: " + init); yield break; }
            var media = AkUnitySoundEngine.LoadBank(catalog.mediaBankName, out mediaId);
            ownsMedia = media == AKRESULT.AK_Success;
            if (!ownsMedia && media != AKRESULT.AK_BankAlreadyLoaded) { Fail("Media SoundBank: " + media); yield break; }
            var result = AkUnitySoundEngine.LoadBank(catalog.bankName, out bankId);
            ownsBank = result == AKRESULT.AK_Success;
            if (!ownsBank && result != AKRESULT.AK_BankAlreadyLoaded) { Fail("Director SoundBank: " + result); yield break; }
            if (!listener.GetComponent<AkGameObj>()) listener.gameObject.AddComponent<AkGameObj>();
            if (!listener.GetComponent<AkAudioListener>()) listener.gameObject.AddComponent<AkAudioListener>();
            foreach (var layer in profile.plan.layers) {
                var target = targets.First(t => t.id == layer.targetId);
                var emitter = new GameObject("Director: " + target.name + " / " + layer.soundId);
                emitter.transform.SetParent(transform, false); emitter.transform.position = target.transform.position;
                emitter.AddComponent<AkGameObj>();
                voices.Add(new Voice { layer = layer, sound = catalog.Find(layer.soundId), target = target,
                    emitter = emitter, nextShot = Time.time + Mathf.Min(2, layer.intervalSeconds / 2) });
            }
            yield return null;
            foreach (var voice in voices) {
                if (!Check(AkUnitySoundEngine.SetRTPCValue("SD_Gain", -96, voice.emitter), "초기 볼륨")) yield break;
                if (voice.sound.loop && !Post(voice)) yield break;
            }
            loadedPlan = JsonUtility.ToJson(profile.plan);
            Ready = true; initializing = false; Status = "Wwise에서 연출 재생 중";
#else
            Fail("Wwise SDK가 활성화되어 있지 않습니다.");
            yield break;
#endif
        }
        public SoundTarget[] SceneTargets() => UnityEngine.Object.FindObjectsByType<SoundTarget>(FindObjectsInactive.Exclude)
            .Where(t => t.gameObject.scene == gameObject.scene).OrderBy(t => t.id, StringComparer.Ordinal).ToArray();
        public float LayerEnvelope(int index) => index >= 0 && index < voices.Count ? voices[index].envelope : 0;
        public GameObject LayerEmitter(int index) => index >= 0 && index < voices.Count ? voices[index].emitter : null;
        void Update() {
            if (!initializing && Ready && Time.unscaledTime >= nextPlanCheck) {
                nextPlanCheck = Time.unscaledTime + .5f;
                if (!profile || loadedPlan != JsonUtility.ToJson(profile.plan)) { Reload(); return; }
            }
#if VESPER_WWISE
            if (!Ready || !listener || !AkUnitySoundEngine.IsInitialized()) return;
            if (voices.Any(v => !v.target || !v.emitter)) { Fail("사운드 대상이 삭제되었습니다. 다시 분석해 주세요."); return; }
            // Pausing freezes one-shot scheduling and envelopes. Wwise handles the audio pause itself.
            if (Time.timeScale <= 0) return;
            Mix = Mathf.MoveTowards(Mix, useDirection ? 1 : 0, Time.deltaTime / .75f);
            if (!SetOriginalGain(1 - Mix)) return;
            float combinedAmplitude = 0;
            foreach (var voice in voices) {
                voice.emitter.transform.position = voice.target.transform.position;
                float distance = Vector3.Distance(listener.position, voice.target.transform.position);
                float desired = DirectorRules.DistanceGain(distance, voice.layer.radius);
                voice.envelope = Mathf.MoveTowards(voice.envelope, desired, Time.deltaTime / voice.layer.fadeSeconds);
                combinedAmplitude += Mathf.Pow(10, voice.layer.gainDb / 20) * voice.envelope;
            }
            // Bound the sum even when authors place all 24 targets at the same position.
            // The authored -6 dB pool headroom is additional to this envelope limit.
            float headroom = combinedAmplitude > .7f ? .7f / combinedAmplitude : 1;
            foreach (var voice in voices) {
                float amplitude = Mathf.Pow(10, voice.layer.gainDb / 20) * voice.envelope * Mix * headroom;
                if (!Check(AkUnitySoundEngine.SetRTPCValue("SD_Gain", DirectorRules.Db(amplitude), voice.emitter), "레이어 볼륨")) return;
                if (!voice.sound.loop && Time.time >= voice.nextShot) {
                    if (amplitude > .001f && !Post(voice)) return;
                    voice.nextShot = Time.time + voice.layer.intervalSeconds * UnityEngine.Random.Range(.8f, 1.2f);
                }
            }
            Status = useDirection ? "연출 B · " + profile.source : "원본 A";
#endif
        }
#if VESPER_WWISE
        bool Post(Voice voice) {
            if (AkUnitySoundEngine.PostEvent(voice.sound.eventName, voice.emitter) == 0) { Fail("재생 실패: " + voice.sound.id); return false; }
            PostedEvents++; return true;
        }
        bool SetOriginalGain(float gain) {
            if (!existingAudio || !existingAudio.Ready) return true;
            foreach (var emitter in new[] { existingAudio.ambienceEmitter, existingAudio.lakeEmitter })
                if (emitter && !Check(AkUnitySoundEngine.SetGameObjectOutputBusVolume(emitter, listener.gameObject, gain), "원본 환경음 전환")) return false;
            // The existing player's footstep emitter is deliberately never touched.
            return true;
        }
        bool Check(AKRESULT result, string action) {
            if (result == AKRESULT.AK_Success) return true;
            Fail(action + ": " + result); return false;
        }
#endif
        void Fail(string message) {
            ErrorCount++; Release(); initializing = false; Status = message;
            Debug.LogError("Sound Director: " + message, this);
        }
        void Release() {
            Ready = false; Mix = 0;
#if VESPER_WWISE
            if (AkUnitySoundEngine.IsInitialized()) {
                if (existingAudio && existingAudio.listener) {
                    foreach (var emitter in new[] { existingAudio.ambienceEmitter, existingAudio.lakeEmitter })
                        if (emitter) AkUnitySoundEngine.SetGameObjectOutputBusVolume(emitter, existingAudio.listener, 1);
                }
                foreach (var voice in voices) if (voice.emitter) AkUnitySoundEngine.StopAll(voice.emitter);
                if (ownsBank) AkUnitySoundEngine.UnloadBank(bankId, IntPtr.Zero);
                if (ownsMedia) AkUnitySoundEngine.UnloadBank(mediaId, IntPtr.Zero);
                if (ownsInit) AkUnitySoundEngine.UnloadBank(initId, IntPtr.Zero);
            }
            ownsBank = ownsInit = ownsMedia = false;
#endif
            foreach (var voice in voices) if (voice.emitter) Destroy(voice.emitter);
            voices.Clear();
        }
        void OnDisable() { StopAllCoroutines(); initializing = false; Release(); }
    }
}
