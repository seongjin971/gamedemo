using UnityEngine;

namespace Vesper.SoundDirector {
    public sealed class DirectorOverlay : MonoBehaviour {
        SoundDirectorPlayer player;
        void Awake() { player = GetComponent<SoundDirectorPlayer>(); }
        void Update() { if (player && Input.GetKeyDown(KeyCode.Tab)) player.useDirection = !player.useDirection; }
        void OnGUI() {
            if (!player || !player.profile || player.profile.plan.layers.Length == 0) return;
            GUILayout.BeginArea(new Rect(18, Screen.height - 112, 540, 94), GUI.skin.box);
            GUILayout.Label("VESPER  /  SOUND DIRECTOR");
            GUILayout.Label(player.Status + "  ·  TAB: A/B");
            GUILayout.Label(player.profile.plan.summary, new GUIStyle(GUI.skin.label) { wordWrap = true });
            GUILayout.EndArea();
        }
    }
}
