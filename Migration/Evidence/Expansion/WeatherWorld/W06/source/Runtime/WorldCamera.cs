using UnityEngine;

namespace Vesper.Expansion.WeatherWorld {
    [RequireComponent(typeof(Camera))]
    public sealed class WorldCamera : MonoBehaviour {
        public WorldMotor player;
        public Vector3 homeTarget = new Vector3(0, 2.9f, .7f);
        public float homeSize = 8.8f;
        public float Angle { get; private set; } = .59f;
        public float Elevation { get; private set; } = .88f;
        public float Zoom { get; private set; } = 8.8f;
        public bool BaselineFraming { get; set; }
        public bool MatchP1Framing { get; set; }
        public int clicks, drags, zooms, resets, blocked;
        public bool nativeInput = true;
        Camera cam;
        Vector3 target, initialPlayer, press, lastMouse;
        bool dragging;
        bool pointerHeld;
        float feedbackUntil;
        Vector3 feedbackPoint;
        bool feedbackAccepted;
        bool traceInput;
        float desiredAngle = .59f, desiredElevation = .88f;
        void Awake() {
            traceInput = System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "-linearInputTrace") >= 0;
            cam = GetComponent<Camera>(); target = player ? player.transform.position + Vector3.up * 1.2f : homeTarget; Zoom = homeSize;
            if (player) initialPlayer = player.transform.position;
            Application.targetFrameRate = 120; QualitySettings.vSyncCount = 0;
        }
        void Update() {
            if (!nativeInput) return;
            if (traceInput && (Input.GetMouseButtonDown(0) || Input.GetMouseButtonUp(0)))
                Debug.Log($"WORLD INPUT raw down={Input.GetMouseButtonDown(0)} up={Input.GetMouseButtonUp(0)} pos={Input.mousePosition} screen={Screen.width}x{Screen.height} focused={Application.isFocused}");
            if (Mathf.Abs(Input.mouseScrollDelta.y) > .001f) { zooms++; SetZoom(Zoom - Input.mouseScrollDelta.y * .55f); }
            if (Input.GetKeyDown(KeyCode.R)) { resets++; ResetView(); }
        }
        void OnGUI() {
            if (!nativeInput) return;
            DrawClickFeedback();
            var e = Event.current;
            if (traceInput && (e.type == EventType.MouseDown || e.type == EventType.MouseUp))
                Debug.Log($"WORLD INPUT gui type={e.type} button={e.button} pos={e.mousePosition} dpi={Screen.dpi} busy={false} cam={!!cam} player={!!player}");
            var pos = new Vector3(e.mousePosition.x, Screen.height - e.mousePosition.y, 0);
            if (HandlePointer(e.type, e.button, pos)) e.Use();
        }
        // Both IMGUI and the opt-in regression probe exercise this full input path.
        public bool HandlePointer(EventType type, int button, Vector3 pos) {
            if (!cam || button != 0) return false;
            
            if (type == EventType.MouseDown) { pointerHeld = true; press = lastMouse = pos; dragging = false; }
            else if (type == EventType.MouseDrag && pointerHeld) {
                if (Vector3.Distance(press, pos) > 5) { if (!dragging) drags++; dragging = true; }
                if (dragging) { var delta = pos - lastMouse; Orbit(-delta.x * .004f, -delta.y * .003f); }
                lastMouse = pos;
            } else if (type == EventType.MouseUp && pointerHeld) {
                pointerHeld = false;
                if (!dragging && Vector3.Distance(press, pos) > 5) {
                    dragging = true; drags++; var delta = pos - press; Orbit(-delta.x * .004f, -delta.y * .003f);
                }
                if (!dragging && player) {
                    clicks++;
                    var ray = cam.ScreenPointToRay(pos);
                    bool accepted = player.Click(ray);
                    if (!accepted) blocked++;
                    feedbackAccepted = accepted; feedbackUntil = Time.unscaledTime + .9f;
                    feedbackPoint = accepted ? cam.WorldToScreenPoint(player.ClickDestination) : pos;
                    if (traceInput) {
                        Physics.Raycast(ray, out var hit, 150, WorldMotor.SurfaceMask | WorldMotor.BlockMask, QueryTriggerInteraction.Ignore);
                        Debug.Log($"WORLD INPUT click accepted={accepted} screen={pos} collider={(hit.collider ? hit.collider.name : "NONE")} hit={hit.point} normal={hit.normal} player={player.transform.position}");
                    }
                }
            } else return false;
            return true;
        }
        void OnApplicationFocus(bool focused) { if (!focused) pointerHeld = false; }
        void OnDisable() { pointerHeld = false; }
        void DrawClickFeedback() {
            if (Time.unscaledTime >= feedbackUntil || false) return;
            var p = feedbackAccepted ? cam.WorldToScreenPoint(player.ClickDestination) : feedbackPoint;
            float x=p.x, y=Screen.height-p.y;
            var old=GUI.color;
            GUI.color=feedbackAccepted ? new Color(.7f,.95f,.7f,Mathf.Min(1,(feedbackUntil-Time.unscaledTime)*3)) : new Color(1,.55f,.4f,Mathf.Min(1,(feedbackUntil-Time.unscaledTime)*3));
            GUI.DrawTexture(new Rect(x-8,y-8,16,2),Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(x-8,y+6,16,2),Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(x-8,y-6,2,12),Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(x+6,y-6,2,12),Texture2D.whiteTexture);
            if(!feedbackAccepted)GUI.Label(new Rect(x+12,y-12,100,24),"Blocked");
            GUI.color=old;
        }
        void LateUpdate() {
            float dt = Time.unscaledDeltaTime;
            Angle = Mathf.Lerp(Angle, desiredAngle, 1 - Mathf.Exp(-12 * dt));
            Elevation = Mathf.Lerp(Elevation, desiredElevation, 1 - Mathf.Exp(-12 * dt));
            cam.orthographicSize = Mathf.Lerp(cam.orthographicSize, Zoom, 1 - Mathf.Exp(-9 * dt));
            var follow = player ? player.transform.position + Vector3.up * 1.2f : homeTarget;
            // Close views frame the traveler rather than cropping legs at the window edge.
            float close = BaselineFraming ? 0 : Mathf.SmoothStep(0, 1, Mathf.InverseLerp(homeSize, 6.5f, cam.orthographicSize));
            if (player) follow = Vector3.Lerp(follow, player.transform.position + Vector3.up * 1.0f, close * .82f);
            target = Vector3.Lerp(target, follow, 1 - Mathf.Exp(-(1.3f + close * 3) * dt));
            transform.position = target + new Vector3(-Mathf.Sin(Angle) * Mathf.Cos(Elevation), Mathf.Sin(Elevation), Mathf.Cos(Angle) * Mathf.Cos(Elevation)) * 42;
            transform.LookAt(target);
        }
        public void Orbit(float angleDelta, float elevationDelta) {
            desiredAngle = Mathf.Clamp(desiredAngle + angleDelta, -.05f, 1.10f);
            desiredElevation = Mathf.Clamp(desiredElevation + elevationDelta, .48f, 1.14f);
        }
        public void SetZoom(float value) { Zoom = Mathf.Clamp(value, 6.5f, 18); }
        // Used only by opt-in screenshot fixtures after teleporting, never during normal travel.
        public void SnapToPlayer() { if (player) target = player.transform.position + Vector3.up * 1.2f; }
        public void Enter(Vector3 spawn, bool connection) {
            initialPlayer = spawn; homeTarget = connection ? spawn + new Vector3(0, 1.2f, -1) : new Vector3(0, 2.9f, .7f);
            homeSize = connection ? 8.8f : 8.8f;
            ResetView(); Angle = desiredAngle; Elevation = desiredElevation; cam.orthographicSize = Zoom;
        }
        public void ResetView() {
            
            desiredAngle = .59f; desiredElevation = .88f; Zoom = homeSize; target = homeTarget;
            if (player) player.ResetPosition();
        }
    }
}
