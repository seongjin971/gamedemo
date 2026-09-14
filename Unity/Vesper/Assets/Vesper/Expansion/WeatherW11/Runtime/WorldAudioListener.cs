using UnityEngine;

namespace Vesper.Expansion.WeatherW11 {
    [DefaultExecutionOrder(60)]
    public sealed class WorldAudioListener : MonoBehaviour {
        public Transform player;
        public Camera view;
        void LateUpdate() {
            if (player) transform.position = player.position + Vector3.up;
            if (view) transform.rotation = view.transform.rotation;
        }
    }
}
