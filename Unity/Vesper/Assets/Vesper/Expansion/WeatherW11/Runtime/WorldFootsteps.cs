using System;
using UnityEngine;
using W10 = Vesper.Expansion.WeatherW10;

namespace Vesper.Expansion.WeatherW11 {
    [DefaultExecutionOrder(50)]
    public sealed class WorldFootsteps : MonoBehaviour {
        public WorldAudioState state;
        public W10.WorldAnimation animationSource;
        public Transform leftFoot, rightFoot;
        public int ContactCount { get; private set; }
        public event Action<SurfaceType> Contact;
        readonly FootstepClock walkClock = new FootstepClock(), runClock = new FootstepClock();
        float lastLeft = -1, lastRight = -1;
        int serial = -1;

        void OnEnable() { walkClock.Reset(); runClock.Reset(); lastLeft = lastRight = -1; serial = -1; }
        void Update() {
            if (!state || !state.Valid || !animationSource) return;
            var motor = state.motor; var profile = state.profile;
            if (serial != motor.ResetSerial) { serial = motor.ResetSerial; lastLeft = lastRight = -1; }
            bool moving = motor.Distance > .0001f && motor.Speed > .05f && animationSource.Blend > .1f;
            int walk = walkClock.Advance(animationSource.Phase, moving, state.Current.grounded, motor.ResetSerial,
                profile.leftWalkContact, profile.rightWalkContact);
            int run = runClock.Advance(Mathf.Repeat(animationSource.Phase + animationSource.runPhaseOffset, 1),
                moving, state.Current.grounded, motor.ResetSerial, profile.leftRunContact, profile.rightRunContact);
            int contacts = animationSource.RunBlend >= .5f ? run : walk;
            // Avoid a duplicate contact when the walk/run blend crosses its midpoint.
            if ((contacts & 1) != 0 && Time.time - lastLeft > .08f) { Emit(leftFoot); lastLeft = Time.time; }
            if ((contacts & 2) != 0 && Time.time - lastRight > .08f) { Emit(rightFoot); lastRight = Time.time; }
        }

        void Emit(Transform foot) {
            var surface = state.Current.surface;
            if (foot && Physics.Raycast(foot.position + Vector3.up * .5f, Vector3.down, out var hit,
                    1.5f, W10.WorldMotor.SurfaceMask, QueryTriggerInteraction.Ignore)) surface = state.SurfaceAt(hit);
            ContactCount++;
            Contact?.Invoke(surface);
        }
    }
}
