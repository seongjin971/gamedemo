using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace Vesper.Expansion.ContinuousWorld {
    [DefaultExecutionOrder(20)]
    public sealed class WorldAnimation : MonoBehaviour {
        public WorldMotor motor;
        public WorldRunInput input;
        public Animator animator;
        public AnimationClip idleClip, walkClip, runClip;
        public float authoredWalkSpeed = 2.668814f, authoredRunSpeed = 5.4f, runPhaseOffset;
        public float Blend { get; private set; }
        public float RunBlend { get; private set; }
        public float Phase { get; private set; }
        PlayableGraph graph;
        AnimationMixerPlayable mixer;
        AnimationClipPlayable idle, walk, run;
        double cycles, idleTime;
        int resetSerial;
        void OnEnable() {
            if (!animator || !idleClip || !walkClip || !runClip || !motor || !input) return;
            animator.applyRootMotion = false;
            graph = PlayableGraph.Create("Continuous world walk and run"); graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
            mixer = AnimationMixerPlayable.Create(graph, 3);
            idle = AnimationClipPlayable.Create(graph, idleClip);
            walk = AnimationClipPlayable.Create(graph, walkClip);
            run = AnimationClipPlayable.Create(graph, runClip);
            idle.SetApplyFootIK(false); walk.SetApplyFootIK(false); run.SetApplyFootIK(false);
            graph.Connect(idle, 0, mixer, 0); graph.Connect(walk, 0, mixer, 1); graph.Connect(run, 0, mixer, 2);
            var output = AnimationPlayableOutput.Create(graph, "Running Generic skin", animator);
            output.SetSourcePlayable(mixer); graph.Play(); resetSerial = motor.ResetSerial; Evaluate(0);
        }
        void Update() { Evaluate(Time.deltaTime); }
        void Evaluate(float dt) {
            if (!graph.IsValid()) return;
            if (resetSerial != motor.ResetSerial) {
                resetSerial = motor.ResetSerial; cycles = idleTime = 0; Blend = RunBlend = 0;
            }
            // Actual speed controls the gait, so braking and sharp turns return to a walk.
            float wantedRun = Mathf.SmoothStep(0, 1, Mathf.InverseLerp(input.walkingSpeed * 1.05f, input.runningSpeed * .94f, motor.Speed));
            RunBlend = Mathf.MoveTowards(RunBlend, wantedRun, dt / .18f);
            float stride = Mathf.Lerp(authoredWalkSpeed * walkClip.length, authoredRunSpeed * runClip.length, RunBlend);
            cycles += motor.Distance / Mathf.Max(.1f, stride);
            Phase = (float)(cycles % 1);
            walk.SetTime(Phase * walkClip.length);
            run.SetTime(Mathf.Repeat(Phase + runPhaseOffset, 1) * runClip.length);
            idleTime += dt; idle.SetTime(idleTime % idleClip.length);
            float wantedMove = Mathf.Clamp01(motor.Speed / .42f);
            Blend = Mathf.MoveTowards(Blend, wantedMove, dt / (wantedMove > Blend ? .14f : .20f));
            mixer.SetInputWeight(0, 1 - Blend);
            mixer.SetInputWeight(1, Blend * (1 - RunBlend));
            mixer.SetInputWeight(2, Blend * RunBlend);
            graph.Evaluate(0);
        }
        void OnDisable() { if (graph.IsValid()) graph.Destroy(); }
    }
}
