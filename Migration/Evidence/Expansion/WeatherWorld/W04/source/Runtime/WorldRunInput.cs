using UnityEngine;

namespace Vesper.Expansion.WeatherWorld {
    // Opt-in only on the separate running scene; the preserved motor is unchanged.
    [DefaultExecutionOrder(-60)]
    public sealed class WorldRunInput : MonoBehaviour {
        public WorldMotor motor;
        public float walkingSpeed = 2.25f, runningSpeed = 5.4f;
        public bool keyboardEnabled = true;
        public bool Requested { get; private set; }
        public int shiftChanges { get; private set; }
        float originalSpeed, originalAcceleration;
        void OnEnable() { if (motor) { originalSpeed = motor.walkSpeed; originalAcceleration = motor.acceleration; } }
        void Update() {
            if (keyboardEnabled) {
                bool held = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
                if (held != Requested) shiftChanges++;
                SetRunning(held);
            }
        }
        public void SetRunning(bool value) {
            Requested = value;
            if (!motor) return;
            motor.walkSpeed = value ? runningSpeed : walkingSpeed;
            motor.acceleration = value ? 7.5f : 5.5f;
        }
        void OnDisable() { if (motor) { motor.walkSpeed = originalSpeed; motor.acceleration = originalAcceleration; } }
    }
}
