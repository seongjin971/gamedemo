import {
  BoxGeometry, DepthFormat, DepthStencilFormat, DepthTexture, Matrix4, NearestFilter,
  NoBlending, ShaderMaterial, UnsignedIntType, UnsignedInt248Type, Vector3,
} from 'three';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';

/**
 * Install after constructing GTAOPass, replacing the caller's render override.
 * The scene RenderPass must directly precede AO: its readBuffer depth is needed.
 * Supports standard WebGL perspective/orthographic depth, not reversed/log depth.
 * Returns { invalidate, dispose, stats }; no per-frame GPU readbacks are used.
 */
export function setupTemporalAO({ ao, composer, camera, renderer, scene, world, getPlayer }) {
  if (!ao?._renderGBuffer || !ao.normalRenderTarget?.depthTexture) {
    throw new Error('Temporal AO requires GTAOPass internal normal/depth buffer.');
  }
  if (renderer.capabilities?.reversedDepthBuffer || renderer.capabilities?.logarithmicDepthBuffer) {
    throw new Error('Temporal AO requires standard WebGL depth.');
  }
  if (typeof getPlayer !== 'function') throw new Error('Temporal AO requires getPlayer().');

  const oldAORender = ao.render, oldComposerRender = composer.render;
  const targetAttachments = new Map();
  const proxy = new BoxGeometry(1, 1, 1);
  const currentPV = new Matrix4(), currentInversePV = new Matrix4();
  const previousPV = new Matrix4(), previousInversePV = new Matrix4();
  const previousPlayer = new Vector3(), currentPlayer = new Vector3();
  let valid = false, disposed = false, lastRefresh = -Infinity;
  let previousWidth = 0, previousHeight = 0, previousNear = 0, previousFar = 0;
  const stats = { refreshes: 0, cachedFrames: 0, reprojectedFrames: 0 };

  const material = new ShaderMaterial({
    name: 'Depth reprojected cached GTAO',
    depthTest: false, depthWrite: false, blending: NoBlending, toneMapped: false,
    uniforms: {
      tScene: { value: null }, tCurrentDepth: { value: null }, tAO: { value: null },
      tPreviousDepth: { value: null }, currentInversePV: { value: currentInversePV },
      previousPV: { value: previousPV }, previousInversePV: { value: previousInversePV },
      intensity: { value: ao.blendIntensity }, reproject: { value: false },
    },
    vertexShader: `varying vec2 vUv;
      void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}`,
    fragmentShader: `
      varying vec2 vUv;
      uniform sampler2D tScene,tCurrentDepth,tAO,tPreviousDepth;
      uniform mat4 currentInversePV,previousPV,previousInversePV;
      uniform float intensity;
      uniform bool reproject;
      void main(){
        vec4 sceneColor=texture2D(tScene,vUv);
        vec4 visibility=vec4(1.);
        if(!reproject){
          visibility=texture2D(tAO,vUv);
        }else{
          float depth=texture2D(tCurrentDepth,vUv).r;
          vec4 worldH=currentInversePV*vec4(vUv*2.-1.,depth*2.-1.,1.);
          vec3 worldPosition=worldH.xyz/worldH.w;
          // Derivatives must be evaluated before any data-dependent branch.
          float footprint=max(length(dFdx(worldPosition)),length(dFdy(worldPosition)));
          float tolerance=.12+min(footprint*2.,.25);
          vec4 oldClip=previousPV*vec4(worldPosition,1.);
          vec3 oldNdc=oldClip.xyz/oldClip.w;
          vec2 oldUv=oldNdc.xy*.5+.5;
          bool inside=all(greaterThanEqual(oldUv,vec2(0.)))&&all(lessThanEqual(oldUv,vec2(1.)));
          if(depth<.999999&&oldClip.w>0.&&abs(oldNdc.z)<=1.&&inside){
            float oldDepth=texture2D(tPreviousDepth,oldUv).r;
            vec4 oldWorldH=previousInversePV*vec4(oldUv*2.-1.,oldDepth*2.-1.,1.);
            vec3 oldWorldPosition=oldWorldH.xyz/oldWorldH.w;
            // Current color depth uses chipped meshes; cached AO uses cube proxies.
            // Small proxy/half-resolution differences are tolerated, newly exposed
            // surfaces or sky retain AO=1 instead of stretching stale dark pixels.
            if(oldDepth<.999999&&distance(oldWorldPosition,worldPosition)<=tolerance){
              visibility=texture2D(tAO,oldUv);
            }
          }
        }
        gl_FragColor=sceneColor*vec4(mix(vec3(1.),visibility.rgb,intensity),visibility.a);
      }`,
  });

  function invalidate() { valid = false; }

  function ensureDepthAttachments() {
    for (const target of [composer.renderTarget1, composer.renderTarget2]) {
      if (!target || targetAttachments.has(target)) continue;
      if (target.depthTexture) continue;
      const depth = new DepthTexture(target.width, target.height, target.stencilBuffer ? UnsignedInt248Type : UnsignedIntType);
      depth.name = 'Temporal AO scene depth'; depth.format = target.stencilBuffer ? DepthStencilFormat : DepthFormat;
      depth.minFilter = depth.magFilter = NearestFilter;
      targetAttachments.set(target, { depth, depthBuffer: target.depthBuffer, stencilBuffer: target.stencilBuffer });
      // Recreate an already allocated framebuffer with the new depth attachment.
      target.dispose(); target.depthTexture = depth; target.depthBuffer = true;
      invalidate();
    }
  }

  function readPlayer() {
    const player = getPlayer();
    if (player?.isObject3D) player.getWorldPosition(currentPlayer);
    else if (player?.position) currentPlayer.copy(player.position);
    else if (player?.isVector3) currentPlayer.copy(player);
    else currentPlayer.set(0, 0, 0);
  }

  function renderFresh(r, write, read, rest) {
    const visibility = [], geometries = [];
    const far = new Set(world.farObjects || []);
    try {
      scene.traverse(object => {
        if (!object.visible || !(object.isMesh || object.isSprite)) return;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        if (object.isSprite || far.has(object) || materials.some(m => m?.transparent)) {
          visibility.push([object, object.visible]); object.visible = false;
        }
      });
      for (const object of world.stoneInstances || []) {
        geometries.push([object, object.geometry]); object.geometry = proxy;
      }
      // Calling the prototype prevents accidental nesting of the old cache wrapper.
      GTAOPass.prototype.render.call(ao, r, write, read, ...rest);
    } finally {
      for (const [object, geometry] of geometries) object.geometry = geometry;
      for (const [object, visible] of visibility) object.visible = visible;
    }
  }

  function temporalRender(r, write, read, ...rest) {
    const aoIndex = composer.passes.indexOf(ao);
    const preceding = composer.passes.slice(0, aoIndex).filter(pass => pass.enabled).at(-1);
    // Reprojection is invalid after an intervening pass that discards scene depth.
    const depthUsable = !!read.depthTexture && preceding?.isRenderPass === true;
    camera.updateWorldMatrix(true, false);
    currentPV.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
    currentInversePV.copy(currentPV).invert(); readPlayer();
    const cameraMoved = valid && currentPV.elements.some((n, i) => Math.abs(n - previousPV.elements[i]) > 1e-6);
    const playerMoved = valid && currentPlayer.distanceToSquared(previousPlayer) > 1e-8;
    const moving = cameraMoved || playerMoved;
    const now = performance.now();
    const dimensionsChanged = previousWidth !== read.width || previousHeight !== read.height;
    const rangeChanged = previousNear !== camera.near || previousFar !== camera.far;
    const refresh = !valid || !depthUsable || dimensionsChanged || rangeChanged ||
      ao.output !== GTAOPass.OUTPUT.Default || now - lastRefresh >= (moving ? 1000 / 30 : 150);
    if (refresh) {
      valid = false;
      renderFresh(r, write, read, rest);
      previousPV.copy(currentPV); previousInversePV.copy(currentInversePV); previousPlayer.copy(currentPlayer);
      previousWidth = read.width; previousHeight = read.height;
      previousNear = camera.near; previousFar = camera.far;
      lastRefresh = performance.now(); valid = true; stats.refreshes++;
      return;
    }
    const uniforms = material.uniforms;
    uniforms.tScene.value = read.texture; uniforms.tCurrentDepth.value = read.depthTexture;
    uniforms.tAO.value = ao.pdRenderTarget.texture;
    uniforms.tPreviousDepth.value = ao.normalRenderTarget.depthTexture;
    uniforms.intensity.value = ao.blendIntensity; uniforms.reproject.value = moving;
    ao._renderPass(r, material, ao.renderToScreen ? null : write);
    stats.cachedFrames++; if (moving) stats.reprojectedFrames++;
  }

  function composerRender(...args) {
    ensureDepthAttachments();
    return oldComposerRender.apply(this, args);
  }
  ensureDepthAttachments(); ao.render = temporalRender; composer.render = composerRender;

  function dispose() {
    if (disposed) return; disposed = true;
    if (ao.render === temporalRender) ao.render = oldAORender;
    if (composer.render === composerRender) composer.render = oldComposerRender;
    for (const [target, attachment] of targetAttachments) {
      if (target.depthTexture === attachment.depth) {
        target.dispose(); target.depthTexture = null;
        target.depthBuffer = attachment.depthBuffer; target.stencilBuffer = attachment.stencilBuffer;
      }
      attachment.depth.dispose();
    }
    targetAttachments.clear(); material.dispose(); proxy.dispose(); invalidate();
  }
  return { invalidate, dispose, stats };
}
