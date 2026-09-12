using System.Collections.Generic;
using UnityEngine;

namespace Vesper.Expansion {
    // P1 keeps the accepted courtyard navigator. Only this root owns translation.
    [DefaultExecutionOrder(-40)]
    public sealed class AdventurerMotor : MonoBehaviour {
        public Vector3 home;
        public float walkSpeed = 1.55f;
        public float acceleration = 5.5f;
        public float turnSpeed = 420f;
        public float Speed { get; private set; }
        public float Distance { get; private set; }
        public float TurnRate { get; private set; }
        public bool IsWalking => route.Count > 0 || Speed > .02f;
        public int Arrivals { get; private set; }
        public int Rejected { get; private set; }
        public int ResetSerial { get; private set; }
        VesperNavigation navigation;
        List<Vector3> route = new List<Vector3>();

        public bool Walk(Vector3 destination) {
            if (navigation == null) navigation = new VesperNavigation();
            if (!navigation.Valid(destination)) { Rejected++; return false; }
            var candidate = navigation.Path(transform.position, destination);
            if (candidate.Count == 0) { Rejected++; return false; }
            // Remove grid zigzags only where the existing clearance test permits
            // the entire straight segment. This is still the P1 courtyard path.
            var simplified = new List<Vector3>();
            Vector3 origin = transform.position;
            for (int at = 0; at < candidate.Count;) {
                int next = at;
                for (int look = candidate.Count - 1; look > at; look--) {
                    if (ClearSegment(origin, candidate[look])) { next = look; break; }
                }
                simplified.Add(candidate[next]); origin = candidate[next]; at = next + 1;
            }
            route = simplified;
            return true;
        }

        bool ClearSegment(Vector3 a, Vector3 b) {
            int samples = Mathf.CeilToInt(Vector3.Distance(a, b) / .07f);
            for (int i = 1; i <= samples; i++) if (!navigation.Valid(Vector3.Lerp(a, b, (float)i / samples))) return false;
            return true;
        }

        void Update() {
            float dt = Mathf.Min(Time.deltaTime, .05f);
            if (dt <= 0) return;
            Vector3 before = transform.position;
            float yaw = transform.eulerAngles.y;
            float remainingDistance = 0;
            Vector3 previous = before;
            foreach (var point in route) { remainingDistance += Vector3.Distance(previous, point); previous = point; }
            float desiredSpeed = Mathf.Min(walkSpeed, Mathf.Sqrt(2 * acceleration * remainingDistance));
            if (route.Count > 0) {
                Vector3 direction = route[0] - transform.position;
                if (direction.sqrMagnitude > .000001f) {
                    var desired = Quaternion.LookRotation(direction);
                    float angle = Quaternion.Angle(transform.rotation, desired);
                    transform.rotation = Quaternion.RotateTowards(transform.rotation, desired, turnSpeed * dt);
                    // Slow before a reversal, so legs do not walk sideways through a turn.
                    desiredSpeed *= Mathf.Lerp(.12f, 1, Mathf.Clamp01(1 - angle / 100));
                }
            }
            Speed = Mathf.MoveTowards(Speed, desiredSpeed, acceleration * dt);
            float budget = Speed * dt;
            while (route.Count > 0 && budget > 0) {
                Vector3 delta = route[0] - transform.position;
                float length = delta.magnitude;
                float step = Mathf.Min(length, budget);
                if (length > .000001f) transform.position += delta / length * step;
                budget -= step;
                if (step >= length) {
                    route.RemoveAt(0);
                    if (route.Count == 0) { Arrivals++; Speed = 0; }
                } else break;
            }
            Distance = Vector3.Distance(before, transform.position);
            Speed = Distance / dt;
            TurnRate = Mathf.DeltaAngle(yaw, transform.eulerAngles.y) / dt;
        }

        public void ResetPosition() {
            route.Clear(); Speed = Distance = TurnRate = 0;
            transform.position = home;
            transform.rotation = Quaternion.Euler(0, 180, 0);
            ResetSerial++;
        }
    }
}
