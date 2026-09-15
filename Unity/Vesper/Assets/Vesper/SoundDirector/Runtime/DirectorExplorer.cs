using UnityEngine;

namespace Vesper.SoundDirector {
    public sealed class DirectorExplorer : MonoBehaviour {
        void Update() {
            float x = (Input.GetKey(KeyCode.D) ? 1 : 0) - (Input.GetKey(KeyCode.A) ? 1 : 0);
            float z = (Input.GetKey(KeyCode.W) ? 1 : 0) - (Input.GetKey(KeyCode.S) ? 1 : 0);
            var forward = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
            transform.position += (forward * z + transform.right * x) * (Time.deltaTime * 8);
            float yaw = (Input.GetKey(KeyCode.E) ? 1 : 0) - (Input.GetKey(KeyCode.Q) ? 1 : 0);
            transform.Rotate(Vector3.up, yaw * Time.deltaTime * 70, Space.World);
        }
    }
}
