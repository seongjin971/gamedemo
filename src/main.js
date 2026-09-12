import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';

import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { createWorld } from './world.js';
import { setupTemporalAO } from './temporal-ao.js';
import { createNavigation } from './navigation.js';
import './style.css';

const canvas=document.querySelector('#scene');
const errors=[];window.addEventListener('error',e=>errors.push(e.message));window.addEventListener('unhandledrejection',e=>errors.push(String(e.reason)));
const renderer=new THREE.WebGLRenderer({canvas,antialias:false,powerPreference:'high-performance',preserveDrawingBuffer:false});
renderer.setPixelRatio(1);renderer.setSize(innerWidth,innerHeight);renderer.info.autoReset=false;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;renderer.shadowMap.autoUpdate=false;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.06;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x17323e);scene.fog=new THREE.FogExp2(0x203644,.008);
let backdrop,backdropTexture;const backdropDirection=new THREE.Vector3();
new THREE.TextureLoader().load('/textures/ruins-panorama.png',texture=>{texture.colorSpace=THREE.SRGBColorSpace;texture.wrapS=THREE.RepeatWrapping;texture.anisotropy=4;backdropTexture=texture;backdrop=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,color:0x9aa6b4,fog:false,depthWrite:false,transparent:false}));backdrop.material.onBeforeCompile=s=>{s.fragmentShader=s.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\nfloat cityLuma=dot(diffuseColor.rgb,vec3(.2126,.7152,.0722));diffuseColor.rgb=mix(diffuseColor.rgb,vec3(cityLuma),.20);diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.022,.038,.057),.20);');};backdrop.name='Generated distant city panorama';backdrop.renderOrder=-100;scene.add(backdrop);});
// A cloudy night sky provides broad outdoor reflections. Studio light cards
// produced pale isolated spots on wet slabs, so they are not part of this scene.
const pmrem=new THREE.PMREMGenerator(renderer),envScene=new THREE.Scene();
const skyMaterial=new THREE.ShaderMaterial({side:THREE.BackSide,toneMapped:false,
  vertexShader:`varying vec3 vDirection;void main(){vDirection=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`varying vec3 vDirection;void main(){vec3 d=normalize(vDirection);float h=smoothstep(-.25,.8,d.y);vec3 c=mix(vec3(.11,.17,.23),vec3(.035,.055,.09),h);float moon=pow(max(0.,dot(d,normalize(vec3(-.5,.75,-.4)))),14.);c+=vec3(.25,.34,.43)*moon;gl_FragColor=vec4(c,1.);}`});
const skySphere=new THREE.Mesh(new THREE.SphereGeometry(20,32,16),skyMaterial);envScene.add(skySphere);
const env=pmrem.fromScene(envScene,.035);scene.environment=env.texture;scene.environmentIntensity=.85;skySphere.geometry.dispose();skyMaterial.dispose();pmrem.dispose();

scene.add(new THREE.HemisphereLight(0x91aec8,0x171a21,.80));
const moon=new THREE.DirectionalLight(0xbcd5e0,2.1);moon.position.set(-20,28,-18);moon.castShadow=true;moon.shadow.mapSize.set(2048,2048);moon.shadow.camera.left=-24;moon.shadow.camera.right=24;moon.shadow.camera.top=24;moon.shadow.camera.bottom=-24;moon.shadow.camera.near=1;moon.shadow.camera.far=80;moon.shadow.bias=-.0003;moon.shadow.normalBias=.035;moon.shadow.radius=2;scene.add(moon);scene.add(moon.target);
const fill=new THREE.DirectionalLight(0x9bb2ce,.24);fill.position.set(-12,18,20);scene.add(fill);
const skyGlint=new THREE.DirectionalLight(0xb5d8eb,.12);skyGlint.position.set(-14,28,-25);scene.add(skyGlint);
const treeKey=new THREE.SpotLight(0xbac4ce,179,19,.55,.8,2);treeKey.position.set(-11,11,8);treeKey.target.position.set(-7.2,4,3.7);scene.add(treeKey,treeKey.target);
const rim=new THREE.DirectionalLight(0x76aabd,.75);rim.position.set(5,12,-20);scene.add(rim);
const camera=new THREE.OrthographicCamera(-18,18,12,-12,.1,180);
const home={angle:.46,elevation:.72,zoom:1.27,target:new THREE.Vector3(0,2.9,.7)};
let azimuth=home.angle,desiredAzimuth=azimuth,elevation=home.elevation,desiredElevation=elevation,zoom=home.zoom,desiredZoom=home.zoom;
const focus=home.target.clone(),desiredFocus=home.target.clone();
const world=createWorld(scene,renderer);const nav=createNavigation(world.blockers);
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
const ao=new GTAOPass(scene,camera,innerWidth/2,innerHeight/2,undefined,{radius:.8,distanceExponent:1.2,thickness:.7,samples:8},{radius:4,samples:8});ao.blendIntensity=.85;
ao.setSize=(w,h)=>GTAOPass.prototype.setSize.call(ao,Math.round(w*.5),Math.round(h*.5));
composer.addPass(ao);
const bloom=new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.20,.52,1.5);composer.addPass(bloom);composer.addPass(new SMAAPass());composer.addPass(new OutputPass());
function resize(){const w=innerWidth,h=innerHeight,half=14.1;camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();renderer.setSize(w,h);composer.setSize(w,h);}
addEventListener('resize',resize);resize();
const player=new THREE.Group();player.name='Player';player.position.set(2.25,0,7.5);player.rotation.y=Math.PI;scene.add(player);
const temporalAO=setupTemporalAO({ao,composer,camera,renderer,scene,world,getPlayer:()=>player});
let knight,tree,limbs={},cape,head;
const playerGlow=new THREE.PointLight(0xa8c5da,.35,4,2);playerGlow.position.set(0,1.5,0);player.add(playerGlow);
const contact=new THREE.Mesh(new THREE.CircleGeometry(.38,32),new THREE.MeshBasicMaterial({color:0x05090b,transparent:true,opacity:.27,depthWrite:false}));contact.rotation.x=-Math.PI/2;contact.position.y=.018;player.add(contact);
const loader=new GLTFLoader();
function consolidateRigidParts(root){
  const parents=[];root.traverse(o=>{if(o.children.length)parents.push(o);});
  for(const parent of parents){const groups=new Map();for(const child of [...parent.children]){
    if(!child.isMesh||['Cape','Head','Sword'].includes(child.name))continue;
    if(!groups.has(child.material))groups.set(child.material,[]);groups.get(child.material).push(child);
  }for(const [material,children]of groups){if(children.length<2)continue;const geometries=children.map(child=>{child.updateMatrix();return child.geometry.clone().applyMatrix4(child.matrix);});
    const compatible=geometries.every(g=>Object.keys(g.attributes).join()===Object.keys(geometries[0].attributes).join());
    if(compatible){const geometry=mergeGeometries(geometries);if(geometry){const merged=new THREE.Mesh(geometry,material);merged.name=parent.name+'_'+material.name;parent.add(merged);children.forEach(child=>parent.remove(child));}}
    geometries.forEach(g=>g.dispose());
  }}
}
const load=async()=>{
  const [k,t]=await Promise.all([loader.loadAsync('/models/knight-v2.glb'),loader.loadAsync('/models/tree-v6.glb')]);
  consolidateRigidParts(k.scene);
  knight=k.scene;knight.scale.setScalar(2.05);player.add(knight);const treated=new Set();knight.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;if(!treated.has(o.material)){treated.add(o.material);if(o.material.metalness>.3)o.material.color.multiplyScalar(.48);if(/crimson|cape|cloth/i.test(o.material.name))o.material.color.multiplyScalar(.58);}}});
  for(const n of ['LeftLeg','RightLeg','LeftArm','RightArm']){const obj=knight.getObjectByName(n);if(obj)limbs[n]={obj,rest:obj.rotation.x};}
  cape=knight.getObjectByName('Cape');head=knight.getObjectByName('Head');
  const barkMap=new THREE.TextureLoader().load('/textures/bark-plates-v2.png'),barkNormal=new THREE.TextureLoader().load('/textures/bark-plates-normal-v2.png');barkMap.colorSpace=THREE.SRGBColorSpace;for(const map of [barkMap,barkNormal]){map.flipY=false;map.wrapS=map.wrapT=THREE.RepeatWrapping;map.anisotropy=8;}
  tree=t.scene;tree.position.set(-7.2,0,3.7);tree.scale.setScalar(1.73);tree.rotation.y=.1;tree.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.material.map=barkMap;o.material.normalMap=barkNormal;o.material.normalScale.setScalar(.6);o.material.roughness=.91;}});scene.add(tree);
  await world.loadStone();
  renderer.shadowMap.needsUpdate=true;document.querySelector('#loading').classList.add('loaded');document.querySelector('#loading').setAttribute('aria-hidden','true');
};
load().catch(e=>{errors.push(String(e));document.querySelector('#loading p').textContent='The sanctuary could not load.';document.querySelector('#loading span').textContent='Please refresh. '+e.message;});
let route=[],distanceWalked=0,moving=0,walkPhase=0,clickCount=0,dragCount=0,zoomCount=0,blockedCount=0;
let lastTarget=null,markerLife=0;
const marker=new THREE.Group();const markerMat=new THREE.MeshBasicMaterial({color:0xd8bc7c,transparent:true,opacity:0,depthWrite:false});
const markerRing=new THREE.Mesh(new THREE.RingGeometry(.27,.293,48),markerMat);markerRing.rotation.x=-Math.PI/2;marker.add(markerRing);
for(let i=0;i<4;i++){const tick=new THREE.Mesh(new THREE.PlaneGeometry(.015,.1),markerMat);tick.rotation.x=-Math.PI/2;tick.rotation.z=i*Math.PI/2;tick.position.set(Math.sin(i*Math.PI/2)*.37,0,Math.cos(i*Math.PI/2)*.37);marker.add(tick);}marker.position.y=.03;scene.add(marker);
const raycaster=new THREE.Raycaster(),groundPlane=new THREE.Plane(new THREE.Vector3(0,1,0),0),hit=new THREE.Vector3();
function walkAt(clientX,clientY){
  const rect=canvas.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((clientX-rect.left)/rect.width*2-1,-(clientY-rect.top)/rect.height*2+1),camera);
  if(!raycaster.ray.intersectPlane(groundPlane,hit))return;
  if(!nav.valid(hit.x,hit.z)){blockedCount++;showToast('The old walls mark the edge of your path.');return;}
  route=nav.path(player.position,hit);const destination=route.at(-1);if(!destination)return;
  lastTarget={...destination};marker.position.set(destination.x,.032,destination.z);markerLife=1;clickCount++;
}
let pointer=null,dragged=false;
canvas.addEventListener('pointerdown',e=>{if(e.button!==0&&e.button!==2)return;pointer={id:e.pointerId,x:e.clientX,y:e.clientY,lastX:e.clientX,lastY:e.clientY};dragged=false;canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointermove',e=>{if(!pointer||pointer.id!==e.pointerId)return;const dx=e.clientX-pointer.lastX,dy=e.clientY-pointer.lastY;if(Math.hypot(e.clientX-pointer.x,e.clientY-pointer.y)>5)dragged=true;if(dragged){desiredAzimuth-=dx*.006;desiredElevation=THREE.MathUtils.clamp(desiredElevation+dy*.003,.48,1.14);canvas.classList.add('dragging');}pointer.lastX=e.clientX;pointer.lastY=e.clientY;});
canvas.addEventListener('pointerup',e=>{if(!pointer)return;if(!dragged&&e.button===0)walkAt(e.clientX,e.clientY);else if(dragged)dragCount++;pointer=null;canvas.classList.remove('dragging');});
canvas.addEventListener('pointercancel',()=>{pointer=null;canvas.classList.remove('dragging');});
canvas.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('wheel',e=>{e.preventDefault();desiredZoom=THREE.MathUtils.clamp(desiredZoom*Math.exp(-e.deltaY*.00085),.66,1.85);zoomCount++;},{passive:false});
let toastTimer;function showToast(text){const el=document.querySelector('#toast');el.textContent=text;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),2600);}
function reset(){desiredAzimuth=home.angle;desiredElevation=home.elevation;desiredZoom=home.zoom;player.position.set(2.25,0,7.5);player.rotation.y=Math.PI;route=[];markerLife=0;desiredFocus.copy(home.target);focus.copy(home.target);renderer.shadowMap.needsUpdate=true;showToast('Returned to the sanctuary');}
document.querySelector('#reset').addEventListener('click',reset);
const toggleUI=()=>document.body.classList.toggle('clean');document.querySelector('#hide').addEventListener('click',toggleUI);
let qaVisible=false;addEventListener('keydown',e=>{if(e.key.toLowerCase()==='r')reset();if(e.key.toLowerCase()==='h')toggleUI();if(e.key.toLowerCase()==='d'){qaVisible=!qaVisible;document.querySelector('#qa').hidden=!qaVisible;}if(e.key.toLowerCase()==='p')capture();if(e.key.toLowerCase()==='b')benchmark();if(e.key.toLowerCase()==='n')benchmark('orbit');if(import.meta.env.DEV&&e.key.toLowerCase()==='x')captureReflection();});
const frameTimes=[],renderTimes=[],gpuTimes=[];let previous=performance.now(),lastFps=previous,time=0,frame=0,currentFps=0;
const gl=renderer.getContext(),timer=gl.getExtension('EXT_disjoint_timer_query_webgl2');let pendingQueries=[];
let benchmarking=false,benchmarkResult=null;
async function benchmark(mode='static'){
  if(benchmarking||!knight)return;benchmarking=true;showToast('Measuring '+mode+' render throughput?');
  const savedPosition=camera.position.clone(),savedQuaternion=camera.quaternion.clone();
  let elapsed=0,count=0;
  try{
    await new Promise(resolve=>setTimeout(resolve,30));gl.finish();
    for(let batch=0;batch<18;batch++){
      const start=performance.now();
      for(let i=0;i<10;i++){
        if(mode==='orbit'){camera.position.copy(savedPosition).sub(focus).applyAxisAngle(new THREE.Vector3(0,1,0),Math.sin((count+i)*.025)*.15).add(focus);camera.lookAt(focus);camera.updateMatrixWorld();}
        world.update(time+(count+i)/60);renderer.info.reset();composer.render();
      }
      gl.finish();elapsed+=performance.now()-start;count+=10;
      await new Promise(resolve=>setTimeout(resolve,0));
    }
    benchmarkResult={timestamp:new Date().toISOString(),mode,frames:count,cpuAndGpuCompletedMs:elapsed,renderThroughputFps:count*1000/elapsed,method:'180 rendered frames in 10-frame batches, GPU completion via gl.finish; excludes yield time; not display FPS',viewport:{width:innerWidth,height:innerHeight,pixelRatio:renderer.getPixelRatio()}};
    await fetch('/__qa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label:'render-benchmark-'+mode,metrics:benchmarkResult})});showToast(`${mode} render throughput ? ${benchmarkResult.renderThroughputFps.toFixed(1)} frames/s`);
  }catch(error){errors.push('Benchmark: '+error.message);showToast('Benchmark could not complete.');}
  finally{camera.position.copy(savedPosition);camera.quaternion.copy(savedQuaternion);camera.updateMatrixWorld();benchmarking=false;previous=performance.now();}
}

async function captureReflection(){
  composer.render();const debugScene=new THREE.Scene(),debugCamera=new THREE.Camera();
  const material=new THREE.MeshBasicMaterial({map:world.water.getRenderTarget().texture,depthTest:false,depthWrite:false});
  const geometry=new THREE.PlaneGeometry(2,2),quad=new THREE.Mesh(geometry,material);debugScene.add(quad);
  renderer.setRenderTarget(null);renderer.render(debugScene,debugCamera);const image=canvas.toDataURL('image/png');composer.render();material.dispose();geometry.dispose();
  await fetch('/__qa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label:'reflection-debug',image,metrics:{note:'Actual planar reflection render target, expanded to viewport for diagnosis'}})});
}
function stats(values){const a=[...values].sort((a,b)=>a-b);return a.length?{samples:a.length,mean:a.reduce((a,b)=>a+b,0)/a.length,p50:a[Math.floor(a.length*.5)],p95:a[Math.floor(a.length*.95)]}:null;}
function metrics(){return {timestamp:new Date().toISOString(),visibility:document.visibilityState,focused:document.hasFocus(),activeFrames:frame,wetMaskProbe:world.wetMaskProbe,temporalAO:temporalAO.stats,farGeometry:world.farObjects.filter(o=>o.isInstancedMesh).map(o=>({visible:o.visible,count:o.count})),viewport:{width:innerWidth,height:innerHeight,pixelRatio:renderer.getPixelRatio()},fps:currentFps,frameMs:stats(frameTimes),renderCpuMs:stats(renderTimes),gpuMs:stats(gpuTimes),renderer:gl.getParameter(gl.RENDERER),drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,player:{x:player.position.x,y:player.position.y,z:player.position.z},camera:{azimuth,elevation,zoom,focus:focus.toArray()},navigation:{bounds:nav.bounds,valid:nav.valid(player.position.x,player.position.z),remainingWaypoints:route.length,lastTarget,distanceWalked,clickCount,dragCount,zoomCount,blockedCount},assets:{knight:!!knight,tree:!!tree},time,errors};}
// Visibility is included in captures so background-tab throttling cannot be
// confused with a rendering limit. Long active frames still count as jank.
document.addEventListener('visibilitychange',()=>{previous=performance.now();});
let captureIndex=0;
async function capture(label){label=typeof label==='string'?label:`capture-${Date.now()}`;renderer.info.reset();composer.render();const image=canvas.toDataURL('image/png');const result=await fetch('/__qa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label,image,metrics:metrics()})});if(result.ok)showToast('Screenshot saved · '+label);else{const a=document.createElement('a');a.href=image;a.download='vesper.png';a.click();showToast('Screenshot downloaded');}}
document.querySelector('#capture').addEventListener('click',()=>capture());
// Observable diagnostics are also available in the visible D overlay and captures.
window.vesper={metrics,capture,reset};
if(import.meta.env.DEV)addEventListener('keydown',async e=>{if(e.key.toLowerCase()!=='u'||!knight)return;try{const {exportUnity}=await import('./export-unity.js');const result=await exportUnity(scene,camera,world,player,composer,canvas);showToast('Unity scene exported · '+result.geometryCount+' geometries');}catch(error){errors.push('Unity export: '+error.message);showToast('Unity export failed');}});
// Development proof: compare cached AO with a fresh render at identical poses.
// This tests disocclusion independently of an occluded Chrome window's cadence.
async function motionProof(){
  if(!import.meta.env.DEV||benchmarking||!knight)return;
  benchmarking=true;
  const position=camera.position.clone(),quaternion=camera.quaternion.clone(),savedZoom=camera.zoom;
  const playerPosition=player.position.clone(),pending=[];
  const label='motion-proof-'+Date.now();
  try{
    for(const [i,mode] of ['orbit','zoom','walk'].entries()){
      camera.position.copy(position);camera.quaternion.copy(quaternion);camera.zoom=savedZoom;camera.updateProjectionMatrix();player.position.copy(playerPosition);
      temporalAO.invalidate();composer.render();
      const before={...temporalAO.stats};
      if(mode==='orbit'){camera.position.sub(focus).applyAxisAngle(new THREE.Vector3(0,1,0),.018).add(focus);camera.lookAt(focus);}
      if(mode==='zoom'){camera.zoom*=1.018;camera.updateProjectionMatrix();}
      if(mode==='walk')player.position.x+=.075;
      camera.updateMatrixWorld();player.updateMatrixWorld();
      composer.render();
      const after={...temporalAO.stats},cached=canvas.toDataURL('image/png');
      temporalAO.invalidate();composer.render();const fresh=canvas.toDataURL('image/png');
      pending.push({label:label+'-'+mode+'-cached',image:cached,metrics:{mode,before,after,reprojected:after.reprojectedFrames>before.reprojectedFrames,viewport:{width:innerWidth,height:innerHeight}}},{label:label+'-'+mode+'-fresh',image:fresh,metrics:{mode,reference:'Fresh GTAO at identical pose/time'}});
    }
    for(const proof of pending)await fetch('/__qa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(proof)});
    showToast('AO comparison saved · '+label);
  }catch(error){errors.push('Motion proof: '+error.message);}
  finally{camera.position.copy(position);camera.quaternion.copy(quaternion);camera.zoom=savedZoom;camera.updateProjectionMatrix();player.position.copy(playerPosition);temporalAO.invalidate();benchmarking=false;previous=performance.now();}
}
addEventListener('keydown',e=>{if(e.key.toLowerCase()==='v')motionProof();});
function updatePlayer(dt){
  const isMoving=route.length>0;moving=THREE.MathUtils.damp(moving,isMoving?1:0,10,dt);
  let remaining=dt*2.25;
  while(route.length&&remaining>0){const p=route[0],dx=p.x-player.position.x,dz=p.z-player.position.z,d=Math.hypot(dx,dz),step=Math.min(d,remaining);if(d>.001){player.position.x+=dx/d*step;player.position.z+=dz/d*step;const angle=Math.atan2(dx,dz);const delta=THREE.MathUtils.euclideanModulo(angle-player.rotation.y+Math.PI,Math.PI*2)-Math.PI;player.rotation.y+=delta*(1-Math.exp(-dt*14));distanceWalked+=step;}remaining-=step;if(d<.03||step===d)route.shift();else break;}
  walkPhase+=dt*(isMoving?8:1.5);for(const [name,{obj,rest}] of Object.entries(limbs)){const sign=name.startsWith('Left')?1:-1;obj.rotation.x=rest+Math.sin(walkPhase)*moving*.46*sign*(name.endsWith('Arm')?-.5:1);}
  if(knight)knight.position.y=Math.abs(Math.sin(walkPhase))*moving*.025+Math.sin(time*1.4)*.003;
  if(cape){cape.rotation.z=Math.sin(time*2.4)*.035+Math.sin(walkPhase)*moving*.045;cape.rotation.x=Math.sin(time*1.9)*.035-moving*.1;}
  if(head)head.rotation.y=Math.sin(time*.6)*.055*(1-moving);
  if(isMoving&&frame%4===0)renderer.shadowMap.needsUpdate=true;
}
function animate(now){
  requestAnimationFrame(animate);const raw=now-previous;previous=now;const dt=Math.min(raw/1000,.045);if(document.hidden||benchmarking)return;time+=dt;frame++;
  if(frame>5&&raw>0){frameTimes.push(raw);if(frameTimes.length>600)frameTimes.shift();}
  world.update(time);updatePlayer(dt);
  desiredFocus.set((player.position.x-2.25)*.24,home.target.y,home.target.z+(player.position.z-7.5)*.24);
  focus.lerp(desiredFocus,1-Math.exp(-dt*1.3));azimuth=THREE.MathUtils.damp(azimuth,desiredAzimuth,9,dt);elevation=THREE.MathUtils.damp(elevation,desiredElevation,9,dt);zoom=THREE.MathUtils.damp(zoom,desiredZoom,9,dt);
  const r=42;camera.position.set(focus.x+Math.sin(azimuth)*Math.cos(elevation)*r,focus.y+Math.sin(elevation)*r,focus.z+Math.cos(azimuth)*Math.cos(elevation)*r);camera.lookAt(focus);camera.zoom=zoom;camera.updateProjectionMatrix();
  if(backdrop){camera.getWorldDirection(backdropDirection);backdrop.position.copy(camera.position).addScaledVector(backdropDirection,100);const h=(camera.top-camera.bottom)/zoom*1.05;backdrop.scale.set(h*2,h,1);backdropTexture.offset.x=-azimuth/(Math.PI*2);}
  markerLife=Math.max(0,markerLife-dt*.25);markerMat.opacity=markerLife*.75;marker.scale.setScalar(1+Math.sin(time*3)*.055);
  let q;if(timer&&frame%20===0&&pendingQueries.length<5){q=gl.createQuery();gl.beginQuery(timer.TIME_ELAPSED_EXT,q);}
  const start=performance.now();renderer.info.reset();composer.render();const cpu=performance.now()-start;if(frame>90){renderTimes.push(cpu);if(renderTimes.length>600)renderTimes.shift();}
  if(q){gl.endQuery(timer.TIME_ELAPSED_EXT);pendingQueries.push(q);}
  pendingQueries=pendingQueries.filter(query=>{if(gl.getQueryParameter(query,gl.QUERY_RESULT_AVAILABLE)){if(!gl.getParameter(timer.GPU_DISJOINT_EXT)){gpuTimes.push(gl.getQueryParameter(query,gl.QUERY_RESULT)/1e6);if(gpuTimes.length>120)gpuTimes.shift();}gl.deleteQuery(query);return false;}return true;});
  if(now-lastFps>1000){lastFps=now;const recent=frameTimes.slice(-120);currentFps=recent.length?1000/(recent.reduce((a,b)=>a+b,0)/recent.length):0;document.querySelector('#fps').textContent=`${Math.round(currentFps)} FPS`;if(qaVisible)document.querySelector('#qa').textContent=JSON.stringify(metrics(),null,2);}
}
requestAnimationFrame(animate);






