using System.Collections;
using UnityEngine;

namespace Vesper.Expansion.WeatherW11 {
    [DisallowMultipleComponent, DefaultExecutionOrder(70)]
    public sealed class WwiseAudioBridge : MonoBehaviour {
        public WorldAudioState state;
        public WorldFootsteps footsteps;
        public GameObject playerEmitter, ambienceEmitter, lakeEmitter, listener;
        public string Status { get; private set; } = "Waiting for Wwise";
        public int PostedEvents { get; private set; }
        public int ErrorCount { get; private set; }
        public bool Ready { get; private set; }
#if VESPER_WWISE
        AudioState sent;
        float nextSync;
        int revision = -1;
        uint bankId, initBankId;
        bool ownsBank, ownsInitBank;
#endif

        void OnEnable() {
            if (footsteps) footsteps.Contact += OnFootstep;
            StartCoroutine(Initialize());
        }

        IEnumerator Initialize() {
            if (!state || !footsteps || !state.profile || !playerEmitter || !ambienceEmitter || !lakeEmitter || !listener) {
                Fail("W11 audio references are incomplete."); yield break;
            }
            if (!state.profile.Validate(out var error)) { Fail(error); yield break; }
#if VESPER_WWISE
            float deadline = Time.realtimeSinceStartup + 15;
            while (!AkUnitySoundEngine.IsInitialized() && Time.realtimeSinceStartup < deadline) yield return null;
            if (!AkUnitySoundEngine.IsInitialized()) { Fail("Wwise initialization timed out. Check AkInitializer and platform plug-ins."); yield break; }
            // The Integration normally loads Init. Track ownership so we never unload another loader's bank.
            var init = AkUnitySoundEngine.LoadBank("Init", out initBankId);
            ownsInitBank = init == AKRESULT.AK_Success;
            if (!ownsInitBank && init != AKRESULT.AK_BankAlreadyLoaded) { Fail("Init.bnk: " + init); yield break; }
            var result = AkUnitySoundEngine.LoadBank(state.profile.bankName, out bankId);
            ownsBank = result == AKRESULT.AK_Success;
            if (!ownsBank && result != AKRESULT.AK_BankAlreadyLoaded) { Fail(state.profile.bankName + ".bnk: " + result); yield break; }
            foreach (var emitter in new[] { playerEmitter, ambienceEmitter, lakeEmitter, listener })
                if (!emitter.GetComponent<AkGameObj>()) emitter.AddComponent<AkGameObj>();
            if (!listener.GetComponent<AkAudioListener>()) listener.AddComponent<AkAudioListener>();
            yield return null;
            state.Refresh();
            if (!state.Valid || !SendState(true)) { Fail("Cannot send initial game syncs."); yield break; }
            Ready = true;
            if (!Post(state.profile.ambienceEvent, ambienceEmitter) || !Post(state.profile.lakeEvent, lakeEmitter)) {
                Ready = false; StopEmitters(); yield break;
            }
            Status = "Wwise connected";
#else
            Status = "NO AUDIO: Wwise Integration is not enabled";
            Debug.LogWarning("W11 state preview only. Install the Wwise Unity Integration, then use Vesper > W11 Audio > Enable Wwise SDK.", this);
            yield break;
#endif
        }

        void Update() {
#if VESPER_WWISE
            if (!Ready || !state.Valid || Time.unscaledTime < nextSync) return;
            nextSync = Time.unscaledTime + state.profile.syncInterval;
            if (!SendState(revision != state.Revision)) { Ready = false; StopEmitters(); }
#endif
        }

        void OnFootstep(SurfaceType surface) {
#if VESPER_WWISE
            if (!Ready) return;
            // Apply the Switch to the SAME object that posts the one-shot.
            if (!Check(AkUnitySoundEngine.SetSwitch("SurfaceType", surface.ToString(), playerEmitter), "SurfaceType")) return;
            sent.surface = surface;
            if (!Post(state.profile.footstepEvent, playerEmitter)) { Ready = false; StopEmitters(); }
#endif
        }

#if VESPER_WWISE
        bool SendState(bool force) {
            var current = state.Current;
            bool ok = true;
            if (force || sent.area != current.area) ok &= Check(AkUnitySoundEngine.SetState("Area", current.area.ToString()), "Area");
            if (force || sent.surface != current.surface) ok &= Check(AkUnitySoundEngine.SetSwitch("SurfaceType", current.surface.ToString(), playerEmitter), "SurfaceType");
            if (force || Mathf.Abs(sent.rainIntensity - current.rainIntensity) >= .005f)
                ok &= Check(AkUnitySoundEngine.SetRTPCValue("RainIntensity", current.rainIntensity), "RainIntensity");
            if (force || Mathf.Abs(sent.timeOfDay - current.timeOfDay) >= .01f)
                ok &= Check(AkUnitySoundEngine.SetRTPCValue("TimeOfDay", current.timeOfDay), "TimeOfDay");
            // Only advance the sent values after successful calls; keep sub-threshold deltas accumulating.
            if (ok) {
                sent.area = current.area; sent.surface = current.surface;
                if (force || Mathf.Abs(sent.rainIntensity - current.rainIntensity) >= .005f) sent.rainIntensity = current.rainIntensity;
                if (force || Mathf.Abs(sent.timeOfDay - current.timeOfDay) >= .01f) sent.timeOfDay = current.timeOfDay;
                revision = state.Revision;
            }
            return ok;
        }
        bool Post(string eventName, GameObject emitter) {
            if (AkUnitySoundEngine.PostEvent(eventName, emitter) == 0) { Fail("Event failed: " + eventName); return false; }
            PostedEvents++; return true;
        }
        bool Check(AKRESULT result, string operation) {
            if (result == AKRESULT.AK_Success) return true;
            Fail(operation + ": " + result); return false;
        }
        void StopEmitters() {
            if (!AkUnitySoundEngine.IsInitialized()) return;
            foreach (var emitter in new[] { playerEmitter, ambienceEmitter, lakeEmitter })
                if (emitter) AkUnitySoundEngine.StopAll(emitter);
        }
#endif
        void Fail(string message) {
            Status = "AUDIO ERROR: " + message; ErrorCount++;
            Debug.LogError(Status, this);
        }

        void OnDisable() {
            StopAllCoroutines();
            if (footsteps) footsteps.Contact -= OnFootstep;
            Ready = false;
#if VESPER_WWISE
            revision = -1;
            StopEmitters();
            if (AkUnitySoundEngine.IsInitialized()) {
                if (ownsBank) AkUnitySoundEngine.UnloadBank(bankId, System.IntPtr.Zero);
                if (ownsInitBank) AkUnitySoundEngine.UnloadBank(initBankId, System.IntPtr.Zero);
            }
            ownsBank = ownsInitBank = false;
#endif
            Status = "Audio stopped";
        }
    }
}
