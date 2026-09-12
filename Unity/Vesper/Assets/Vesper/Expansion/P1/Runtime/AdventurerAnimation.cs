using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace Vesper.Expansion {
    // Generic skeleton, in-place clips, distance-driven walk phase; no root motion.
    [DefaultExecutionOrder(20)]
    public sealed class AdventurerAnimation : MonoBehaviour {
        public AdventurerMotor motor;
        public Animator animator;
        public AnimationClip idleClip, walkClip;
        public float authoredWalkSpeed = 1.55f;
        public float Blend { get; private set; }
        public float Phase { get; private set; }
        PlayableGraph graph;
        AnimationMixerPlayable mixer;
        AnimationClipPlayable idle, walk;
        double walkTime;
        int resetSerial;

        void OnEnable() {
            if (!animator || !idleClip || !walkClip) return;
            animator.applyRootMotion = false;
            graph = PlayableGraph.Create("P1 adventurer locomotion");
            graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
            mixer = AnimationMixerPlayable.Create(graph, 2);
            idle = AnimationClipPlayable.Create(graph, idleClip);
            walk = AnimationClipPlayable.Create(graph, walkClip);
            idle.SetApplyFootIK(false); walk.SetApplyFootIK(false);
            graph.Connect(idle, 0, mixer, 0); graph.Connect(walk, 0, mixer, 1);
            var output = AnimationPlayableOutput.Create(graph, "Generic skin", animator);
            output.SetSourcePlayable(mixer); graph.Play();
            resetSerial = motor.ResetSerial;
            Evaluate(0);
        }

        void Update() { Evaluate(Time.deltaTime); }
        void Evaluate(float dt) {
            if (!graph.IsValid()) return;
            if (resetSerial != motor.ResetSerial) {
                resetSerial = motor.ResetSerial; walkTime = 0; Blend = 0; idle.SetTime(0);
            }
            // The walk clock advances by real distance, including acceleration/braking.
            walkTime += motor.Distance / Mathf.Max(.1f, authoredWalkSpeed);
            walk.SetTime(walkTime % walkClip.length);
            idle.SetTime((idle.GetTime() + dt) % idleClip.length);
            float wanted = Mathf.Clamp01(motor.Speed / .42f);
            Blend = Mathf.MoveTowards(Blend, wanted, dt / (wanted > Blend ? .14f : .20f));
            mixer.SetInputWeight(0, 1 - Blend); mixer.SetInputWeight(1, Blend);
            Phase = (float)(walkTime % walkClip.length) / walkClip.length;
            graph.Evaluate(0);
        }
        void OnDisable() { if (graph.IsValid()) graph.Destroy(); }
    }
}
