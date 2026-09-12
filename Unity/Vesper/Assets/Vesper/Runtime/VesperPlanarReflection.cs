using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Vesper
{
    /// <summary>
    /// One horizontal courtyard reflection, generated before its source camera.
    /// Layer 31 is always omitted; put any separate water/overlay geometry there.
    /// WetStone itself is opaque and disables reflection sampling for this pass.
    /// This is deliberately one plane, not a reflection for elevated stair treads.
    /// </summary>
    [ExecuteAlways, DisallowMultipleComponent]
    public sealed class VesperPlanarReflection : MonoBehaviour
    {
        public Camera sourceCamera;
        [Tooltip("Horizontal floor plane in Unity world coordinates.")]
        public float planeHeight = -0.005f;
        [Range(256, 2048)] public int textureSize = 1024;
        [Range(0.001f, 0.15f)] public float clipOffset = 0.025f;
        public LayerMask reflectionMask = ~0;
        [Min(0)] public int rendererIndex;
        public bool renderShadows = true;
        public bool renderSky;
        public Material reflectedSkybox;
        public bool includeSceneView;

        static readonly int TextureId = Shader.PropertyToID("_VesperPlanarReflection");
        static readonly int MatrixId = Shader.PropertyToID("_VesperReflectionVP");
        static readonly int PlaneId = Shader.PropertyToID("_VesperReflectionPlane");
        static readonly int TexelId = Shader.PropertyToID("_VesperReflectionTexelSize");
        static readonly int AvailableId = Shader.PropertyToID("_VesperReflectionAvailable");

        static bool renderingReflection;
        Camera reflectionCamera;
        RenderTexture reflectionTexture;
        int lastFrame = -1;
        Camera lastSourceCamera;

        public RenderTexture ReflectionTexture => reflectionTexture;
        public int RenderedFrameCount { get; private set; }

        void OnEnable()
        {
            RenderPipelineManager.beginCameraRendering += BeginCameraRendering;
            Shader.SetGlobalFloat(AvailableId, 0);
        }

        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering -= BeginCameraRendering;
            Shader.SetGlobalFloat(AvailableId, 0);
            Shader.SetGlobalTexture(TextureId, Texture2D.blackTexture);
            ReleaseTexture();
            if (reflectionCamera != null)
                DestroyOwned(reflectionCamera.gameObject);
            reflectionCamera = null;
            lastFrame = -1;
        }

        void OnValidate()
        {
            textureSize = Mathf.Clamp(textureSize, 256, 2048);
            clipOffset = Mathf.Clamp(clipOffset, 0.001f, 0.15f);
            rendererIndex = Mathf.Max(0, rendererIndex);
            lastFrame = -1;
        }

        void BeginCameraRendering(ScriptableRenderContext context, Camera camera)
        {
            if (!isActiveAndEnabled || renderingReflection || camera == null || camera == reflectionCamera)
                return;
            if (!(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset))
                return;
            if (camera.cameraType == CameraType.Reflection || camera.cameraType == CameraType.Preview)
                return;
            bool sceneView = camera.cameraType == CameraType.SceneView;
            if (sceneView && !includeSceneView)
                return;
            Camera selected = sourceCamera != null ? sourceCamera : Camera.main;
            if (!sceneView && camera != selected)
                return;
            if (camera.transform.position.y < planeHeight + 0.01f)
            {
                Shader.SetGlobalFloat(AvailableId, 0);
                return;
            }

            // Editor repaints can reuse Time.frameCount, so cache only during Play.
            if (Application.isPlaying && lastFrame == Time.frameCount && lastSourceCamera == camera)
                return;

            EnsureResources(camera);
            ConfigureCamera(camera);
            bool previousInvertCulling = GL.invertCulling;
            bool succeeded = false;
            renderingReflection = true;
            Shader.SetGlobalFloat(AvailableId, 0);
            try
            {
                GL.invertCulling = !previousInvertCulling;
                // Verified in installed URP 17.5.0: this public method still exists
                // and renders within the supplied context without camera callbacks.
                // It avoids re-entering a second pipeline render-request context.
#pragma warning disable CS0618
                UniversalRenderPipeline.RenderSingleCamera(context, reflectionCamera);
#pragma warning restore CS0618
                succeeded = true;
            }
            finally
            {
                GL.invertCulling = previousInvertCulling;
                renderingReflection = false;
                // Restore globals used by the camera whose callback we interrupted.
                context.SetupCameraProperties(camera);
                if (succeeded)
                {
                    Shader.SetGlobalTexture(TextureId, reflectionTexture);
                    Shader.SetGlobalMatrix(MatrixId,
                        GL.GetGPUProjectionMatrix(reflectionCamera.projectionMatrix, true) * reflectionCamera.worldToCameraMatrix);
                    Shader.SetGlobalVector(PlaneId, new Vector4(0, 1, 0, -planeHeight));
                    Shader.SetGlobalVector(TexelId, new Vector4(1f / reflectionTexture.width,
                        1f / reflectionTexture.height, reflectionTexture.width, reflectionTexture.height));
                    Shader.SetGlobalFloat(AvailableId, 1);
                    lastFrame = Time.frameCount;
                    lastSourceCamera = camera;
                    RenderedFrameCount++;
                }
            }
        }

        void EnsureResources(Camera source)
        {
            if (reflectionCamera == null)
            {
                var go = new GameObject("VESPER planar reflection camera")
                {
                    hideFlags = HideFlags.HideAndDontSave
                };
                reflectionCamera = go.AddComponent<Camera>();
                reflectionCamera.enabled = false;
                var data = go.AddComponent<UniversalAdditionalCameraData>();
                data.renderType = CameraRenderType.Base;
                data.renderPostProcessing = false;
                data.requiresColorOption = CameraOverrideOption.Off;
                data.requiresDepthOption = CameraOverrideOption.Off;
                data.antialiasing = AntialiasingMode.None;
                data.volumeLayerMask = 0;
            }

            int width = Mathf.Clamp(textureSize, 256, 2048);
            int height = Mathf.Max(128, Mathf.RoundToInt(width / Mathf.Max(0.1f, source.aspect)));
            if (reflectionTexture != null && reflectionTexture.width == width && reflectionTexture.height == height)
                return;
            ReleaseTexture();
            var format = SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBHalf)
                ? RenderTextureFormat.ARGBHalf : RenderTextureFormat.ARGB32;
            reflectionTexture = new RenderTexture(width, height, 24, format, RenderTextureReadWrite.Linear)
            {
                name = "VESPER courtyard planar reflection",
                hideFlags = HideFlags.HideAndDontSave,
                filterMode = FilterMode.Bilinear,
                wrapMode = TextureWrapMode.Clamp,
                antiAliasing = 1,
                useMipMap = false,
                autoGenerateMips = false
            };
            reflectionTexture.Create();
        }

        void ConfigureCamera(Camera source)
        {
            reflectionCamera.CopyFrom(source);
            if(renderSky) reflectionCamera.clearFlags=CameraClearFlags.Skybox;
            var skybox=reflectionCamera.GetComponent<Skybox>();
            if(!skybox)skybox=reflectionCamera.gameObject.AddComponent<Skybox>();
            skybox.enabled=renderSky&&reflectedSkybox;skybox.material=reflectedSkybox;
            reflectionCamera.enabled = false;
            reflectionCamera.cameraType = CameraType.Game;
            reflectionCamera.targetTexture = reflectionTexture;
            reflectionCamera.allowMSAA = false;
            reflectionCamera.allowHDR = true;
            reflectionCamera.useOcclusionCulling = false;
            reflectionCamera.cullingMask = reflectionMask.value & source.cullingMask & ~(1 << 31);
            reflectionCamera.depthTextureMode = DepthTextureMode.None;
            reflectionCamera.rect = new Rect(0, 0, 1, 1);
            var data = reflectionCamera.GetUniversalAdditionalCameraData();
            data.SetRenderer(rendererIndex);
            data.renderShadows = renderShadows;
            data.renderPostProcessing = false;
            data.volumeLayerMask = 0;
            data.requiresColorOption = CameraOverrideOption.Off;
            data.requiresDepthOption = CameraOverrideOption.Off;

            var reflection = Matrix4x4.identity;
            reflection.m11 = -1;
            reflection.m13 = 2 * planeHeight;
            reflectionCamera.transform.SetPositionAndRotation(
                reflection.MultiplyPoint(source.transform.position),
                Quaternion.LookRotation(reflection.MultiplyVector(source.transform.forward),
                    reflection.MultiplyVector(source.transform.up)));
            reflectionCamera.worldToCameraMatrix = source.worldToCameraMatrix * reflection;
            reflectionCamera.projectionMatrix = source.projectionMatrix;

            Vector3 clipPoint = new Vector3(0, planeHeight + clipOffset, 0);
            Vector3 cameraPoint = reflectionCamera.worldToCameraMatrix.MultiplyPoint(clipPoint);
            Vector3 cameraNormal = reflectionCamera.worldToCameraMatrix.MultiplyVector(Vector3.up).normalized;
            Vector4 clipPlane = new Vector4(cameraNormal.x, cameraNormal.y, cameraNormal.z,
                -Vector3.Dot(cameraPoint, cameraNormal));
            reflectionCamera.projectionMatrix = source.CalculateObliqueMatrix(clipPlane);
            reflectionCamera.cullingMatrix = reflectionCamera.projectionMatrix * reflectionCamera.worldToCameraMatrix;
        }

        void ReleaseTexture()
        {
            if (reflectionTexture == null)
                return;
            if (reflectionCamera != null)
                reflectionCamera.targetTexture = null;
            reflectionTexture.Release();
            DestroyOwned(reflectionTexture);
            reflectionTexture = null;
        }

        static void DestroyOwned(Object item)
        {
            if (Application.isPlaying) Destroy(item);
            else DestroyImmediate(item);
        }
    }
}
