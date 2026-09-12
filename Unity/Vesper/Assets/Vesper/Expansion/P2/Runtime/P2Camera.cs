using UnityEngine;

namespace Vesper.Expansion.P2 {
    [RequireComponent(typeof(Camera))]
    public sealed class P2Camera : MonoBehaviour {
        public P2Motor player;
        public Vector3 homeTarget = new Vector3(0, 2.9f, .7f);
        public float homeSize = 14.1f / 1.27f;
        public float Angle { get; private set; } = .46f;
        public float Elevation { get; private set; } = .72f;
        public float Zoom { get; private set; } = 14.1f / 1.27f;
        public bool BaselineFraming { get; set; }
        public bool MatchP1Framing { get; set; }
        public int clicks, drags, zooms, resets, blocked;
        Camera cam;
        Vector3 target, initialPlayer, press, lastMouse;
        bool dragging;
        bool pointerHeld;
        float feedbackUntil;
        Vector3 feedbackPoint;
        bool feedbackAccepted;
        bool traceInput;
        float desiredAngle = .46f, desiredElevation = .72f;
        void Awake() {
            traceInput = System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "-p2InputTrace") >= 0;
            cam = GetComponent<Camera>(); target = homeTarget; Zoom = homeSize;
            if (player) initialPlayer = player.transform.position;
            Application.targetFrameRate = 60; QualitySettings.vSyncCount = 0;
        }
        void Update() {
            if (traceInput && (Input.GetMouseButtonDown(0) || Input.GetMouseButtonUp(0)))
                Debug.Log($"P2 INPUT raw down={Input.GetMouseButtonDown(0)} up={Input.GetMouseButtonUp(0)} pos={Input.mousePosition} screen={Screen.width}x{Screen.height} focused={Application.isFocused}");
            if (Mathf.Abs(Input.mouseScrollDelta.y) > .001f) { zooms++; SetZoom(Zoom - Input.mouseScrollDelta.y * .55f); }
            if (Input.GetKeyDown(KeyCode.R)) { resets++; ResetView(); }
        }
        void OnGUI() {
            DrawClickFeedback();
            var e = Event.current;
            if (traceInput && (e.type == EventType.MouseDown || e.type == EventType.MouseUp))
                Debug.Log($"P2 INPUT gui type={e.type} button={e.button} pos={e.mousePosition} dpi={Screen.dpi} busy={(P2World.Instance && P2World.Instance.Busy)} cam={!!cam} player={!!player}");
            var pos = new Vector3(e.mousePosition.x, Screen.height - e.mousePosition.y, 0);
            if (HandlePointer(e.type, e.button, pos)) e.Use();
        }
        // Both IMGUI and the opt-in regression probe exercise this full input path.
        public bool HandlePointer(EventType type, int button, Vector3 pos) {
            if (!cam || button != 0) return false;
            if (P2World.Instance && P2World.Instance.Busy) { pointerHeld = false; return false; }
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
                        Physics.Raycast(ray, out var hit, 150, P2Motor.SurfaceMask | P2Motor.BlockMask, QueryTriggerInteraction.Ignore);
                        Debug.Log($"P2 INPUT click accepted={accepted} screen={pos} collider={(hit.collider ? hit.collider.name : "NONE")} hit={hit.point} normal={hit.normal} player={player.transform.position}");
                    }
                }
            } else return false;
            return true;
        }
        void OnApplicationFocus(bool focused) { if (!focused) pointerHeld = false; }
        void OnDisable() { pointerHeld = false; }
        void DrawClickFeedback() {
            if (Time.unscaledTime >= feedbackUntil || (P2World.Instance && P2World.Instance.Busy)) return;
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
            var follow = homeTarget + (player ? Vector3.Scale(player.transform.position - initialPlayer, (MatchP1Framing ? Vector3.one * .24f : new Vector3(.75f, 1, .75f))) : Vector3.zero);
            // Close views frame the traveler rather than cropping legs at the window edge.
            float close = BaselineFraming ? 0 : Mathf.SmoothStep(0, 1, Mathf.InverseLerp(homeSize, 7.5f, cam.orthographicSize));
            if (player) follow = Vector3.Lerp(follow, player.transform.position + Vector3.up * 1.0f, close * .82f);
            target = Vector3.Lerp(target, follow, 1 - Mathf.Exp(-(1.3f + close * 3) * dt));
            transform.position = target + new Vector3(-Mathf.Sin(Angle) * Mathf.Cos(Elevation), Mathf.Sin(Elevation), Mathf.Cos(Angle) * Mathf.Cos(Elevation)) * 42;
            transform.LookAt(target);
        }
        public void Orbit(float angleDelta, float elevationDelta) {
            desiredAngle = Mathf.Clamp(desiredAngle + angleDelta, -.05f, 1.10f);
            desiredElevation = Mathf.Clamp(desiredElevation + elevationDelta, .48f, 1.14f);
        }
        public void SetZoom(float value) { Zoom = Mathf.Clamp(value, 7.5f, 14); }
        public void Enter(Vector3 spawn, bool connection) {
            initialPlayer = spawn; homeTarget = connection ? spawn + new Vector3(0, 1.2f, -1) : new Vector3(0, 2.9f, .7f);
            homeSize = connection ? 8.8f : 14.1f / 1.27f;
            ResetView(); Angle = desiredAngle; Elevation = desiredElevation; cam.orthographicSize = Zoom;
        }
        public void ResetView() {
            if (P2World.Instance && P2World.Instance.Busy) return;
            desiredAngle = .46f; desiredElevation = .72f; Zoom = homeSize; target = homeTarget;
            if (player) player.ResetPosition();
        }
    }
}
