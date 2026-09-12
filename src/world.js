import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { TessellateModifier } from 'three/addons/modifiers/TessellateModifier.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

export function createWorld(scene, renderer) {
  let seed = 21417;
  const rand = () => { seed = (Math.imul(seed, 1664525) + 1013904223) | 0; return (seed >>> 0) / 4294967296; };
  const between = (a, b) => a + rand() * (b-a);
  const stoneTex = new THREE.TextureLoader().load('/textures/stone-grain-v2.png');
  stoneTex.wrapS = stoneTex.wrapT = THREE.RepeatWrapping; stoneTex.colorSpace = THREE.SRGBColorSpace;
  stoneTex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  const stoneNormal=new THREE.TextureLoader().load('/textures/stone-grain-normal-v2.png');stoneNormal.wrapS=stoneNormal.wrapT=THREE.RepeatWrapping;stoneNormal.anisotropy=stoneTex.anisotropy;
  const stone = new THREE.MeshStandardMaterial({ color: 0xb8b7ae, roughness: .52, metalness: .03, map: stoneTex, bumpMap: stoneTex, bumpScale: .11 });
  const floorMat = new THREE.MeshPhysicalMaterial({clearcoat:.75,clearcoatRoughness:.18,anisotropy:.25,anisotropyRotation:Math.PI*.5, color: 0x99a9b5, roughness: .62, metalness: .08, map: stoneTex, bumpMap: stoneTex, bumpScale: .07,envMapIntensity:1.15 });
  const trim = new THREE.MeshStandardMaterial({ color: 0xd1c9b7, roughness: .56, metalness: .08, map: stoneTex, bumpMap: stoneTex, bumpScale: .09 });
  for(const mat of [stone,floorMat,trim]){mat.normalMap=stoneNormal;mat.normalScale.setScalar(mat===floorMat?.80:.80);mat.bumpMap=null;}
  floorMat.clearcoatNormalMap=stoneNormal;floorMat.clearcoatNormalScale.setScalar(.65);
  const dark = new THREE.MeshStandardMaterial({ color: 0x292f30, roughness: .88, map: stoneTex });
  const bronze = new THREE.MeshStandardMaterial({ color: 0x544331, roughness: .41, metalness: .8 });
  const coal = new THREE.MeshStandardMaterial({ color: 0x37170c, emissive: 0xc13706, emissiveIntensity: .8, roughness: 1 });
  // Multiscale weathering and wetness vary continuously in world space, so the
  // material does not repeat the same pattern on every instanced stone.
  const surfaceNoise=`float hashStone(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}float stoneNoise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hashStone(i),hashStone(i+vec3(1,0,0)),f.x),mix(hashStone(i+vec3(0,1,0)),hashStone(i+vec3(1,1,0)),f.x),f.y),mix(mix(hashStone(i+vec3(0,0,1)),hashStone(i+vec3(1,0,1)),f.x),mix(hashStone(i+vec3(0,1,1)),hashStone(i+vec3(1,1,1)),f.x),f.y),f.z);}`;
  const waterNoise=`float waterHash(vec2 p){p=fract(p*vec2(.1031,.1030));p+=dot(p,p.yx+33.33);return fract((p.x+p.y)*p.x);}float waterNoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(waterHash(i),waterHash(i+vec2(1,0)),f.x),mix(waterHash(i+vec2(0,1)),waterHash(i+vec2(1,1)),f.x),f.y);}`;
  const puddleField=waterNoise+`float puddleField(vec2 p){
    vec2 q=p+vec2(sin(p.y*.77+p.x*.26),cos(p.x*.71-p.y*.37))*.8;
    float n=waterNoise(q*.72)*.65+waterNoise(q*1.7)*.35;
    vec2 a=(q-vec2(-1.7,3.))/vec2(2.5,5.7),b=(q-vec2(6.5,3.7))/vec2(2.7,5.5),c=(q-vec2(-2.,11.))/vec2(5.5,6.);
    float pools=max(exp(-dot(a,a)),exp(-dot(b,b)));pools=max(pools,exp(-dot(c,c))*.6);
    vec2 d=(q-vec2(3.0,8.5))/vec2(1.6,2.3),e=(q-vec2(-4.0,15.))/vec2(2.0,1.8);pools=max(pools,exp(-dot(d,d)));pools=max(pools,exp(-dot(e,e)));return smoothstep(.30,.70,pools*.66+n*.44);
  }`;
  // Bake the immutable puddle field once, then share the same continuous mask
  // between wet stone and reflection. This removes expensive per-frame noise.
  const wetTarget=new THREE.WebGLRenderTarget(1024,1024,{type:THREE.HalfFloatType,depthBuffer:false});
  const wetScene=new THREE.Scene(),wetCamera=new THREE.Camera();
  const wetMaterial=new THREE.ShaderMaterial({depthTest:false,depthWrite:false,toneMapped:false,
    vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}`,
    fragmentShader:`varying vec2 vUv;${puddleField}void main(){float w=puddleField(vUv*64.-32.);gl_FragColor=vec4(w,w,w,1.);}`});
  const wetQuad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),wetMaterial);wetScene.add(wetQuad);
  const originalTarget=renderer.getRenderTarget();renderer.setRenderTarget(wetTarget);renderer.render(wetScene,wetCamera);renderer.setRenderTarget(originalTarget);wetQuad.geometry.dispose();wetMaterial.dispose();
  const wetProbe=new Uint16Array(4);renderer.readRenderTargetPixels(wetTarget,512,560,1,1,wetProbe);const wetMaskProbe=Array.from(wetProbe,v=>THREE.DataUtils.fromHalfFloat(v));
  const wetLookup=`uniform sampler2D uWetMap;float puddleField(vec2 p){return texture2D(uWetMap,(p+32.)/64.).r;}`;
  for(const mat of [stone,floorMat,trim]) {
    mat.onBeforeCompile=s=>{
      s.vertexShader='varying vec3 vStoneWorld;\n'+s.vertexShader;
      s.vertexShader=s.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvec4 stonePosition=vec4(transformed,1.);\n#ifdef USE_INSTANCING\nstonePosition=instanceMatrix*stonePosition;\n#endif\nvStoneWorld=(modelMatrix*stonePosition).xyz;');
      if(mat!==floorMat)s.vertexShader=s.vertexShader.replace('vStoneWorld=(modelMatrix*stonePosition).xyz;','vStoneWorld=(modelMatrix*stonePosition).xyz;vec3 faceAxis=abs(normal);vec2 masonryUV=faceAxis.y>faceAxis.x&&faceAxis.y>faceAxis.z?vStoneWorld.xz:(faceAxis.x>faceAxis.z?vStoneWorld.zy:vStoneWorld.xy);vMapUv=masonryUV*.18;vNormalMapUv=vMapUv;');
      if(mat===floorMat)s.vertexShader=s.vertexShader.replace('vStoneWorld=(modelMatrix*stonePosition).xyz;','vStoneWorld=(modelMatrix*stonePosition).xyz;float slabSeed=.5;\n#ifdef USE_INSTANCING\nslabSeed=fract(sin(dot(instanceMatrix[3].xz,vec2(17.13,73.71)))*43758.54);\n#endif\nfloat slabAngle=slabSeed*2.4-1.2;mat2 grainRotation=mat2(cos(slabAngle),-sin(slabAngle),sin(slabAngle),cos(slabAngle));vec2 stoneUV=grainRotation*vStoneWorld.xz*mix(.12,.20,slabSeed)+slabSeed*7.;vMapUv=stoneUV;vNormalMapUv=stoneUV;vClearcoatNormalMapUv=stoneUV;');
      s.uniforms.uWetMap={value:wetTarget.texture};s.fragmentShader='varying vec3 vStoneWorld;\n'+surfaceNoise+'\n'+wetLookup+'\n'+s.fragmentShader;
      s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\nfloat patina=stoneNoise(vStoneWorld*1.7)*.5+stoneNoise(vStoneWorld*7.3)*.3+stoneNoise(vStoneWorld*28.)*.2;diffuseColor.rgb*=mix(.48,1.20,patina);');
      if(mat===floorMat){s.fragmentShader=s.fragmentShader.replace('#include <lights_physical_fragment>','#include <lights_physical_fragment>\nfloat wetUp=smoothstep(.86,.98,abs(inverseTransformDirection(normal,viewMatrix).y));material.anisotropy*=wetUp;material.clearcoat*=smoothstep(.28,.82,wet)*wetUp;material.clearcoatRoughness=mix(.42,.26,wet)+geometryRoughness;material.roughness=mix(max(material.roughness,.58),material.roughness,wetUp);material.alphaT=mix(pow2(material.roughness),1.,pow2(material.anisotropy));');s.fragmentShader=s.fragmentShader.replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nfloat wet=puddleField(vStoneWorld.xz);wet*=mix(1.,.78,smoothstep(.12,.4,vStoneWorld.y));float stairWet=smoothstep(.2,.5,vStoneWorld.y)*smoothstep(3.8,5.4,vStoneWorld.x)*(1.-smoothstep(-2.,-.5,vStoneWorld.z));wet=mix(wet,.92,stairWet*.85);float grain=texture2D(normalMap,vNormalMapUv).b;roughnessFactor=mix(.72,.43,wet)+(.95-grain)*.22;diffuseColor.rgb*=mix(1.08,.94,wet);');s.fragmentShader=s.fragmentShader.replace('#include <lights_fragment_end>','#include <lights_fragment_end>\nreflectedLight.directSpecular*=.48;clearcoatSpecularIndirect*=.24;clearcoatSpecularDirect*=mix(.14,.80,stairWet);clearcoatSpecularDirect*=min(1.,mix(.16,.38,stairWet)/max(.001,max3(clearcoatSpecularDirect)));reflectedLight.directSpecular*=min(1.,.18/max(.001,max3(reflectedLight.directSpecular)));');}
    };
    mat.customProgramCacheKey=()=>mat===floorMat?'wet-stone-round3b':'stone-patina-4';
  }
  const runeMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.0, .47, .105), toneMapped: false });
  const batches = new Map();const stoneInstances=[],farObjects=[];
  const distantMaterials = new Map();let distantMode=false;let assemblyOffset=false;
  const box = new RoundedBoxGeometry(1,1,1,1,.04);
  const dummy = new THREE.Object3D();
  const c = new THREE.Color();
  function distantMaterial(mat){
    if(distantMaterials.has(mat))return distantMaterials.get(mat);
    const dm=mat.clone();dm.userData.distant=true;dm.color.set(0x626a74);dm.emissive.set(0x172b3e);dm.emissiveIntensity=.65;dm.normalMap=stoneNormal;dm.normalScale.setScalar(.28);dm.bumpMap=null;dm.roughness=.95;dm.flatShading=true;
    dm.onBeforeCompile=shader=>{
      shader.vertexShader='varying float ruinHeight;varying float ruinBaseFade;\n'+shader.vertexShader;
      shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvec4 ruinP=vec4(transformed,1.);\n#ifdef USE_INSTANCING\nruinP=instanceMatrix*ruinP;\n#endif\nruinHeight=(modelMatrix*ruinP).y;ruinBaseFade=1.;\n#ifdef USE_INSTANCING\nif(length(instanceMatrix[1].xyz)>4.)ruinBaseFade=smoothstep(-.5,-.28,transformed.y);\n#endif');
      shader.fragmentShader='varying float ruinHeight;varying float ruinBaseFade;\n'+shader.fragmentShader;
      shader.fragmentShader=shader.fragmentShader.replace('#include <fog_fragment>','#include <fog_fragment>\nfloat baseHaze=(1.-smoothstep(-21.,1.,ruinHeight))*.83;gl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(.035,.067,.092),baseHaze);gl_FragColor.a*=ruinBaseFade*smoothstep(-18.,-5.,ruinHeight);');
    };
    dm.transparent=true;dm.depthWrite=true;dm.customProgramCacheKey=()=> 'ruin-height-fog-v4';distantMaterials.set(mat,dm);return dm;
  }
  function block(x,y,z,sx,sy,sz,mat=stone,ry=0,variation=.19,tilt=0) {
    if(assemblyOffset){x+=2.8;z+=.5;}
    if(distantMode)mat=distantMaterial(mat);
    if (!batches.has(mat)) batches.set(mat, []);
    if(distantMode){sx*=1.026;sy*=1.042;}
    else if(mat===stone&&sy<.9&&y>1&&sx<1.5&&sz<2.1){
      const wear=rand();if(wear<.065){sx*=between(.66,.86);sz*=between(.72,.9);ry+=between(-.035,.035);}
      y+=between(-.012,.012);ry+=between(-.009,.009);sz+=.035*Math.sin(x*12.73+y*8.41+z*16.1);z+=.018*Math.cos(x*16.3+y*11.3);
    }
    const shade = 1 + between(-variation,variation);
    dummy.position.set(x,y,z); dummy.scale.set(sx,sy,sz); dummy.rotation.set(tilt,ry,tilt*.35);dummy.updateMatrix();
    c.setRGB(shade*(1+between(-.025,.025)),shade,shade*(1+between(-.025,.025)));
    batches.get(mat).push({ matrix: dummy.matrix.clone(), color: c.clone() });
  }
  function mesh(geo, mat, x,y,z) { if(distantMode)mat=distantMaterial(mat);const m=new THREE.Mesh(geo,mat);m.position.set(x+(assemblyOffset?2.8:0),y,z+(assemblyOffset?.5:0));m.castShadow=true;m.receiveShadow=true;scene.add(m);if(distantMode)farObjects.push(m);return m; }
  function pillar(x,z,base=0,height=7,wide=1.3) {
    block(x,base+.15,z,wide+1,.3,wide+1,trim);
    block(x,base+.45,z,wide+.6,.3,wide+.6,stone);
    for(let y=.7;y<height-.4;y+=.68) {
      block(x,base+y+.31,z,wide,.643,wide,stone,0,.16);
      if(y<height-1) for(const side of [-1,1]) {
        block(x+side*wide*.36,base+y+.31,z+wide*.49,.19,.643,.24,trim);
      }
    }
    block(x,base+height-.2,z,wide+.34,.27,wide+.34,trim);
    block(x,base+height+.02,z,wide+.17,.19,wide+.19,stone,between(-.04,.04),.2,.045);
    for(let i=0;i<2;i++) block(x+between(-.35,.35)*wide,base+height+between(.2,.55),z+between(-.3,.3)*wide,between(.36,.65),between(.35,.94),between(.3,.6),stone,between(-.18,.18),.25,between(-.22,.22));
  }
  function wallRun(x,z,length,height,rotation=0,base=0) {
    const count=Math.ceil(length/.8);const bw=length/count;
    for(let row=0;row<height/.43;row++)for(let i=0;i<count;i++) {
      const local=-length/2+(i+.5)*bw+(row%2)*bw*.28;
      const edge=Math.abs(local)/(length/2);
      if(row>height/.43-2 && rand()<.4)continue;
      if(distantMode&&i>1&&i<5&&row>height/.43-4)continue;
      if(row>2 && edge>.85 && rand()<.25)continue;
      block(x+Math.cos(rotation)*local,base+row*.43+.21,z+Math.sin(rotation)*local,bw-.025,.407,.78,stone,-rotation,.23);
    }
    for(let i=0;i<count;i++) if(rand()>.2) {
      const local=-length/2+(i+.5)*bw;
      block(x+Math.cos(rotation)*local,base+height+.12,z+Math.sin(rotation)*local,bw-.015,.21,.91,trim,-rotation);
    }
  }
  // The visible foundation continues far below the player, into fog.
  block(0,-1.15,5,18.7,2.2,32,dark);
  for(let side of [-1,1]) for(let z=-10;z<21;z+=.95) {
    const bottom=between(-14,-5);
    block(side*9.03,(bottom-.15)/2,z,between(.7,1.35),-bottom,between(.72,1.03),stone,between(-.04,.04),.27);
    for(let y=-.5;y>-3.5;y-=.45)block(side*9.47,y,z,.5,.43,.91,stone);
  }
  for(let x=-8.8;x<9;x+=.9) {
    let bottom=between(-14,-5);
    block(x,bottom/2,20.45,.86,-bottom,1.0,stone,0,.25);
    for(let y=-.35;y>-3;y-=.45)block(x,y,20.8,.87,.41,.4,stone);
  }
  // Individually beveled, staggered flagstones: real gaps and irregular elevations.
  const tileD=.94;
  for(let row=0;row<31;row++){
    const z=-7.65+row*tileD;let left=-9.0;
    while(left<8.85){
      const width=Math.min(between(1.13,1.75)*(left===-9.0&&row%3===1?.73:1.),8.9-left);if(width<.18)break;
      const x=left+width/2;left+=width;
      if(z<-1.6&&Math.abs(x-2.8)<4.)continue;
      const y=-.105+between(-.026,.021),rotation=between(-.022,.022);
      if(rand()<.14){for(const side of [-1,1])block(x+side*width*.25,y,z,width*.5-.025,.16,tileD-.034,floorMat,rotation,.20);}
      else block(x,y,z,width-.038,.16,tileD-.033,floorMat,rotation,.20);
    }
  }
  // Exposed rear foundation is capped in the same aged flagstone as the court.
  // A broken lip ends the terrace; no bare black foundation top is left visible.
  for(let row=0;row<3;row++)for(let col=0;col<6;col++){
    const x=-8.3+col*1.24,z=-10.6+row*.98;
    if(row===0&&(col===1||col===4))continue;
    block(x,-.10,z,1.20,.17,.94,floorMat,.018*Math.sin(col*4+row),.18);
  }
  // Long narrow inlay bands anchor the composition without covering the wet stone.
  for(const x of [-6.25,6.25])for(let z=-1.6;z<20;z+=.84)block(x,-.012,z,.09,.045,.78,trim,0,.1);
  // Stair flight and elevated sanctuary landing.
  assemblyOffset=true;
  const stairCount=10,stepDepth=.49,rise=.29;
  for(let i=0;i<stairCount;i++) {
    const z=-2.25-i*stepDepth,y=(i+1)*rise;
    block(0,y/2-.015,z,7.8,y,stepDepth+.01,dark);
    for(let j=0;j<9;j++)block(-3.53+j*.885,y-rise*.51,z+.19,.863,rise*.96,.17,stone,0,.16);
    for(let j=0;j<9;j++)block(-3.53+j*.885,y+.007,z+.04,.863,.07,.49,floorMat,0,.14);
    for(let j=0;j<10;j++){if((i===3&&j===2)||(i===7&&j===6))continue;block(-3.51+j*.78,y+.02+between(-.005,.005),z+.254,.753,.049,between(.04,.073),floorMat,0,.11);}
  }
  const platformY=stairCount*rise;
  block(0,platformY/2,-8.2,9,platformY,3.8,dark);
  for(let row=0;row<5;row++)for(let col=0;col<10;col++)block(-4.02+col*.895,platformY-.07,-6.7-row*.82,.869,.16,.8,floorMat,0,.19);
  // Monumental masonry: cut stones around an actual pointed opening.
  function arch(x,z,base=0,scale=1,detailed=true) {
    const half=2.0,spring=4.6,peak=spring+Math.sqrt(3)*half;
    const put=(px,py,pz,sx,sy,sz,mat=stone,ry=0)=>block(x+px*scale,base+py*scale,z+pz*scale,sx*scale,sy*scale,sz*scale,mat,ry,.2);
    const segments=[];
    for(const side of [-1,1]) {
      for(let row=0;row<8;row++) {
        put(side*(half+.47),row*.575+.28,0,.87,.55,1.4);
        if(detailed) {
          put(side*(half+.09),row*.575+.28,.81,.18,.55,.23,trim);
          put(side*(half+.48),row*.575+.28,.77,.13,.55,.26,trim);
          put(side*(half+.84),row*.575+.28,.74,.18,.55,.3,trim);
        }
      }
      for(let ring=0;ring<(detailed?3:1);ring++)for(let n=0;n<13;n++) {
        if(!detailed&&n>=8&&n<=11&&side===-1)continue;
        const start=Math.PI-(Math.PI/3)*n/13-.006,end=Math.PI-(Math.PI/3)*(n+1)/13+.006;
        const ri=half*2+ring*.255,ro=ri+.235;
        const pts=[new THREE.Vector2(half+Math.cos(start)*ri,spring+Math.sin(start)*ri),new THREE.Vector2(half+Math.cos(end)*ri,spring+Math.sin(end)*ri),new THREE.Vector2(half+Math.cos(end)*ro,spring+Math.sin(end)*ro),new THREE.Vector2(half+Math.cos(start)*ro,spring+Math.sin(start)*ro)];
        if(side===1)pts.forEach(p=>p.x=-p.x);
        const shape=new THREE.Shape(pts);
        const geo=new THREE.ExtrudeGeometry(shape,{depth:1.4+ring*.08,bevelEnabled:true,bevelSegments:1,steps:1,bevelSize:.022,bevelThickness:.025,curveSegments:1});
        geo.translate(0,0,-.7);geo.scale(scale,scale,scale);geo.translate(x,base,z);segments.push(geo);
      }
      // Broken vertical masses and buttresses.
      for(let col=0;col<4;col++) {
        const px=side*(3.19+col*.72),h=(10-col*1.35)+between(-.3,.9);
        for(let y=.30;y<h;y+=.59) {
          if(y>h-.9 && rand()<.25)continue;
          put(px,y,0,.69,.562,1.3);
        }
      }
      if(detailed) {
        for(let y=.32;y<10.2;y+=.64)put(side*3.7,y,.83,.72,.609,1.65);
        for(let y of [.25,1.0,3.0,5.7,8.0])put(side*3.7,y,1.0,.95,.21,1.93,trim);
        put(side*3.7,10.3,.83,.79,.31,1.69,trim);
        // Tiny angled crown atop the outer pilaster.
        const g=new THREE.ConeGeometry(.54,1.24,4);g.rotateY(Math.PI/4);const m=mesh(g,stone,x+side*3.7*scale,base+11*scale,z+.83*scale);m.scale.setScalar(scale);
      }
    }
    // Spandrel courses follow the curved aperture instead of filling it.
    for(let row=0;row<10;row++) {
      const py=spring+.23+row*.46;
      for(let col=0;col<8;col++) {
        const px=-2.56+col*.73;
        const boundary=py<peak?Math.abs(half-Math.sqrt(Math.max(0,4*half*half-(py-spring)**2))):0;
        if(Math.abs(px)-.38>boundary+.6 || py>peak+.67)put(px,py,-.23,.703,.438,1.04);
      }
    }
    let joined=mergeGeometries(segments);if(detailed){const dense=new TessellateModifier(.25,4).modify(joined);joined.dispose();joined=dense;const pos=joined.attributes.position;for(let v=0;v<pos.count;v++){const x=pos.getX(v),y=pos.getY(v),z=pos.getZ(v);const relief=.007*Math.sin(x*29.+y*17.)+.006*Math.cos(y*37.+x*11.)+.009*Math.sin(x*8.+y*13.);pos.setZ(v,z+relief);}joined.computeVertexNormals();}const a=mesh(joined,trim,0,0,0);if(distantMode)a.castShadow=false;
    segments.forEach(g=>g.dispose());
    return a;
  }
  arch(0,-8.4,platformY,1,true);
  pillar(-4.95,-2.8,0,6.8,1.15);pillar(4.95,-2.8,0,6.15,1.15);
  for(const side of [-1,1])for(let i=0;i<7;i++) {
    const z=-7.35+i*.75,h=7.7-i*.51+between(-.45,.7);
    for(let row=0;row<h/.43;row++) {
      if(row>h/.43-2&&rand()<.4)continue;
      if((i===2||i===5)&&row>h/.43-5)continue;
      block(side*5.9,row*.43+.21,z,.87,.405,.72,stone,between(-.006,.006),.3);
      if(i%3===0)block(side*6.48,row*.43+.21,z,.31,.405,.77,stone,0,.2);
    }
  }
  for(const side of [-1,1]) {
    // stepped cheek walls along the stair.
    for(let i=0;i<10;i++) {
      const y=(i+1)*rise;
      for(let row=.21;row<y+1;row+=.43)block(side*4.2,row,-2.25-i*.49,.69,.407,.47,stone);
      block(side*4.2,y+1.05,-2.25-i*.49,.86,.18,.49,trim);
    }
  }
  assemblyOffset=false;
  for(const side of [-1,1]){
    wallRun(side*8.9,8.1,25.7,1.13,Math.PI/2);
    for(const z of [-3.4,4.6,11.4,18.4])pillar(side*8.9,z,0,between(2.0,3.15),.87);
  }
  wallRun(-6.7,20.4,4.1,1.3);wallRun(6.7,20.4,4.1,1.3);
  wallRun(-8.85,.2,3.7,2.15,Math.PI/2);
  // Pedestal and hovering sacred instrument.
  assemblyOffset=true;
  block(0,platformY+.18,-8.6,1.7,.35,1.5,stone,0,.08);
  block(0,platformY+.62,-8.6,1.04,.56,.96,stone,0,.06);
  block(0,platformY+.94,-8.6,1.55,.18,1.37,trim,0,.07);
  const halo=new THREE.Group();halo.position.set(2.8,platformY+2.72,-8.1);scene.add(halo);
  const runeLineMat=new THREE.LineBasicMaterial({color:runeMat.color,toneMapped:false});
  function ring(radius,tube=.013) {const points=Array.from({length:192},(_,i)=>new THREE.Vector3(Math.cos(i*Math.PI*2/192)*radius,Math.sin(i*Math.PI*2/192)*radius,0));return new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),runeLineMat);}
  halo.add(ring(.94),ring(.69,.009));
  const orbit1=ring(.88,.009);orbit1.rotation.y=1.1;halo.add(orbit1);
  const orbit2=ring(.88,.009);orbit2.rotation.x=.92;halo.add(orbit2);
  const center=new THREE.Mesh(new THREE.OctahedronGeometry(.14),runeMat);halo.add(center);
  for(let i=0;i<12;i++) {
    const a=i*Math.PI/6;const tick=new THREE.Mesh(new THREE.BoxGeometry(.018,i%3===0?.27:.09,.018),runeMat);
    tick.position.set(Math.sin(a)*1.04,Math.cos(a)*1.04,0);tick.rotation.z=-a;halo.add(tick);
  }
  const axis=new THREE.Mesh(new THREE.BoxGeometry(.014,2.95,.014),runeMat);halo.add(axis);
  const baseRune=ring(.56,.013);baseRune.rotation.x=-Math.PI/2;baseRune.position.set(2.8,platformY+1.043,-8.1);scene.add(baseRune);
  const runeLight=new THREE.PointLight(0xffaa42,25,13,2);runeLight.position.copy(halo.position);scene.add(runeLight);
  const portalBounce=new THREE.PointLight(0xff9a36,36,11,2);portalBounce.position.set(2.8,7.8,-7.3);scene.add(portalBounce);
  // The hovering relic is an extended light source. Its finite reflection
  // covers rough tread surfaces instead of producing isolated point glints.
  RectAreaLightUniformsLib.init();
  const relicArea=new THREE.RectAreaLight(0xffb95d,6,1.7,1.4);
  relicArea.position.set(2.8,5.6,-8.1);relicArea.lookAt(4.7,1.2,-3.3);scene.add(relicArea);
  // Distant silhouettes use the same architecture and local geometry, in deep fog.
  assemblyOffset=false;
  distantMode=true;
  const ruins=[[-15,-12,-5,.53],[-24,-24,-7,.64],[-11,-30,-3,.47],[17,-22,-7,.56],[26,-34,-8,.68],[-19,5,-13,.65],[20,1,-11,.6],[-7,-48,-2,.49],[13,-47,-4,.58],[-36,-35,-4,.62],[38,-45,-6,.49],[-8,-15,-6,.49],[-20,-3,-7,.55],[14,-8,-10,.52],[10,-16,-3,.65],[7,-24,-4,.5],[3,-25,-7,.6],[-14,-2,-8,.65],[-20,-11,-9,.7],[-12,-22,-4,.4]];
  for(let i=0;i<ruins.length;i++) {
    if(![0,5,6,11,13].includes(i))continue;
    const [x,z,base,scale]=ruins[i];arch(x,z,base,scale,false);
    wallRun(x+(i%2?3:-3),z,4,between(1.8,3.5),0,base);
    pillar(x+(i%2?-3.5:3.5),z-1,base,between(4,7),.8);
    // Thin fractured rock/masonry shafts instead of huge untextured slabs.
    for(let col=0;col<12;col++) {
      const px=x+(col-5.5)*.7*scale,bottom=base-between(11,22);
      block(px,(base+bottom)*.5,z,.67*scale,base-bottom,between(.8,1.5),stone,between(-.025,.025),.28);
      for(let y=base-.2;y>base-4;y-=.7)block(px,y,z+.7,.64*scale,.65,.27,stone);
    }
  }
  for(let i=0;i<8;i++) {
    const x=between(-48,48),z=between(-65,-37),base=between(-10,-2);
    pillar(x,z,base,between(8,19),between(.9,1.5));
  }
  distantMode=false;
  // Broken offcuts, fallen capitals and stone fragments gathered at the walls.
  for(let i=0;i<300;i++) {
    const side=rand()<.5?-1:1;const x=side*between(7.3,8.75),z=between(-5.9,12);
    const size=between(.10,.46);
    block(x,size*.35,z,size,between(.1,.38),between(.13,.54),stone,between(0,Math.PI),.27,between(-.15,.15));
  }
  for(let i=0;i<65;i++) {
    const side=rand()<.5?-1:1;const x=side*between(4.7,7.3),z=between(-7.8,-1.8),size=between(.13,.49);
    block(x,size*.4,z,size,size*.75,size*between(.5,1.6),stone,between(0,3),.25,between(-.2,.2));
  }
  for(let i=0;i<8;i++) {
    let x=between(-7.8,7.8),z=between(.1,11.4);
    if(Math.abs(x)<4)continue;
    block(x,.04,z,between(.16,.36),.1,between(.1,.4),stone,between(0,3),.2,.12);
  }
  // Sparse bronze grasses, built as bent blade geometry with vertex wind.
  const grassVerts=[],grassColors=[];
  for(let tuft=0;tuft<140;tuft++) {
    let x=(rand()<.5?-1:1)*between(6.7,8.8),z=between(-6,12);
    if(tuft<30){x=between(-8.5,8.5);z=between(-1.5,11.5);}
    for(let blade=0;blade<between(3,7);blade++) {
      const a=rand()*Math.PI*2,w=between(.015,.037),h=between(.12,.5),lean=between(.08,.25);
      const px=x+between(-.12,.12),pz=z+between(-.12,.12),dx=Math.cos(a),dz=Math.sin(a);
      grassVerts.push(px-dz*w,0,pz+dx*w,px+dz*w,0,pz-dx*w,px+dx*lean,h,pz+dz*lean);
      const shade=between(.65,1);for(let v=0;v<3;v++)grassColors.push(.35*shade,.28*shade,.14*shade);
    }
  }
  const grassGeo=new THREE.BufferGeometry();grassGeo.setAttribute('position',new THREE.Float32BufferAttribute(grassVerts,3));grassGeo.setAttribute('color',new THREE.Float32BufferAttribute(grassColors,3));grassGeo.computeVertexNormals();
  const grassMat=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.88,side:THREE.DoubleSide});
  let grassShader;
  grassMat.onBeforeCompile=s=>{grassShader=s;s.uniforms.windTime={value:0};s.vertexShader='uniform float windTime;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x += sin(windTime*1.5+position.x*1.7+position.z)*position.y*0.09;');};
  mesh(grassGeo,grassMat,0,0,0);
  const flames=[],fireLights=[],emberOrigins=[];
  const flameTexture=new THREE.TextureLoader().load('/textures/flame-v1.png');flameTexture.colorSpace=THREE.SRGBColorSpace;
  const flameTime={value:0};
  const plumeMaterial=new THREE.SpriteMaterial({map:flameTexture,color:new THREE.Color(1.8,1.25,.9),blending:THREE.AdditiveBlending,depthWrite:false,fog:false,transparent:true,opacity:.9});
  plumeMaterial.onBeforeCompile=s=>{s.uniforms.fireTime=flameTime;s.fragmentShader='uniform float fireTime;\n'+s.fragmentShader;s.fragmentShader=s.fragmentShader.replace('#include <map_fragment>','vec2 fireUv=vMapUv;fireUv.x+=sin(fireUv.y*11.-fireTime*4.)*.012*fireUv.y;fireUv.y+=(sin(fireTime*3.+fireUv.x*9.)*.012)*fireUv.y;diffuseColor*=texture2D(map,fireUv);');};
  const flameMat=new THREE.ShaderMaterial({uniforms:{uTime:{value:0}},transparent:true,depthWrite:false,side:THREE.DoubleSide,
    vertexShader:`uniform float uTime;varying float vHeight;void main(){vHeight=uv.y;vec3 p=position;p.x+=sin(uTime*8.+modelMatrix[3].x*3.+uv.y*7.)*uv.y*uv.y*.075;p.z+=cos(uTime*6.+uv.y*8.)*uv.y*uv.y*.05;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,
    fragmentShader:`varying float vHeight;void main(){vec3 color=mix(vec3(2.7,.9,.075),vec3(.9,.08,.003),smoothstep(.0,.9,vHeight));gl_FragColor=vec4(color,1.-vHeight*vHeight*.55);
#include <tonemapping_fragment>
#include <colorspace_fragment>
}`});
  function brazier(x,z,y=0) {
    block(x,y+.13,z,1.48,.26,1.42,stone);
    block(x,y+.38,z,1.2,.25,1.13,trim);
    block(x,y+.77,z,.83,.55,.8,stone);
    block(x,y+1.08,z,1.02,.13,.98,bronze);
    const bowl=mesh(new THREE.CylinderGeometry(.59,.34,.35,4,1,true),bronze,x,y+1.28,z);bowl.rotation.y=Math.PI/4;
    mesh(new THREE.CylinderGeometry(.39,.3,.1,8),coal,x,y+1.39,z);
    for(let n=0;n<6;n++) {
      const log=mesh(new THREE.CylinderGeometry(.07,.09,.65,5),dark,x+between(-.15,.15),y+1.42,z+between(-.15,.15));log.rotation.set(Math.PI/2,0,n*1.1);
    }
    const plume=new THREE.Sprite(plumeMaterial);plume.position.set(x,y+2.06,z);plume.scale.set(1.25,1.65,1);plume.userData.reflectInWater=true;scene.add(plume);flames.push({mesh:plume,y:plume.position.y,phase:rand()*10,sx:1.25,sy:1.65});
    const light=new THREE.PointLight(0xff902e,35,9.8,2);light.position.set(x,y+2,z);scene.add(light);fireLights.push(light);emberOrigins.push(new THREE.Vector3(x,y+1.7,z));
  }
  brazier(-1.65,-1.45);brazier(6.9,-1.45);
  // Variant geometry is grouped into batches; no per-stone draw calls.
  for(const [mat,items] of batches) {
    const count=mat.userData.distant?1:mat===floorMat?8:2;
    for(let variant=0;variant<count;variant++){
      const selected=items.filter((_,i)=>i%count===variant);
      const inst=new THREE.InstancedMesh(mat.userData.distant?new THREE.BoxGeometry(1,1,1):box,mat,selected.length);
      selected.forEach((item,i)=>{inst.setMatrixAt(i,item.matrix);inst.setColorAt(i,item.color);});
      inst.userData.variant=(mat===floorMat?0:8)+variant;
      inst.castShadow=!mat.userData.distant;inst.receiveShadow=!mat.userData.distant;inst.computeBoundingSphere();scene.add(inst);
      if(!mat.userData.distant)stoneInstances.push(inst);else farObjects.push(inst);
    }
  }
  const puddleShader={
    uniforms:{...THREE.UniformsUtils.clone(Reflector.ReflectorShader.uniforms),uTime:{value:0},uWetMap:{value:null},uStoneNormal:{value:null}},
    vertexShader:`uniform mat4 textureMatrix; varying vec4 vUv; varying vec3 vWorld; void main(){ vUv=textureMatrix*vec4(position,1.);vWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`uniform sampler2D tDiffuse,uStoneNormal; uniform float uTime; varying vec4 vUv; varying vec3 vWorld;${wetLookup}
      float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
      void main(){ vec2 p=vWorld.xz;float mask=puddleField(p);vec2 uv=vUv.xy/vUv.w;vec3 grain=texture2D(uStoneNormal,p*.32).rgb;float ripple=sin(p.x*51.+sin(p.y*22.)+uTime*.8)*.00016;uv+=(grain.xy-.5)*.008+vec2(ripple,noise(p*3.)*.001);vec3 col=texture2D(tDiffuse,uv).rgb*.5;
      col+=(texture2D(tDiffuse,uv+vec2(0.,.007)).rgb+texture2D(tDiffuse,uv-vec2(0.,.007)).rgb)*.14;
      col+=(texture2D(tDiffuse,uv+vec2(0.,.014)).rgb+texture2D(tDiffuse,uv-vec2(0.,.014)).rgb)*.07;
      col+=(texture2D(tDiffuse,uv+vec2(0.,.021)).rgb+texture2D(tDiffuse,uv-vec2(0.,.021)).rgb)*.04;
      float sky=pow(noise(p*vec2(2.7,1.2))*.4+noise(p*6.)*.35+noise(p*20.)*.25,3.)*.8;float reflectionLuma=dot(col,vec3(.2126,.7152,.0722));float visibleReflection=smoothstep(.025,.16,reflectionLuma);col=max(col,vec3(.035,.055,.072));float broken=smoothstep(.32,.65,noise(p*vec2(6.,14.))*.6+noise(p*vec2(19.,41.))*.4);gl_FragColor=vec4(col,mask*(.028+visibleReflection*.55)*(.22+broken*.78));
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
      }`
  };
  const water=new Reflector(new THREE.PlaneGeometry(17.75,21.73),{textureWidth:768,textureHeight:512,clipBias:0,multisample:0,shader:puddleShader});
  water.material.uniforms.uWetMap.value=wetTarget.texture;water.material.uniforms.uStoneNormal.value=stoneNormal;
  water.rotation.x=-Math.PI/2;water.position.set(0,.005,9.42);water.material.transparent=true;water.material.depthWrite=false;water.renderOrder=2;scene.add(water);
  // Distant city lies behind the reflected courtyard's occluding walls. Skip its
  // expensive geometry in the secondary view; keep the hero, flames and rune.
  const reflectionRender=water.onBeforeRender.bind(water);
  water.onBeforeRender=(...args)=>{
    const skipped=[...farObjects];scene.traverse(o=>{if(o.isSprite&&!o.userData.reflectInWater)skipped.push(o);});
    const states=skipped.map(o=>o.visible);skipped.forEach(o=>o.visible=false);
    try{reflectionRender(...args);}finally{skipped.forEach((o,i)=>o.visible=states[i]);}
  };
  // Wisps, drifting cinders and near-invisible falling rain are animated in shaders.
  const emberCount=150,positions=new Float32Array(emberCount*3),phases=new Float32Array(emberCount);
  for(let i=0;i<emberCount;i++){const origin=emberOrigins[i%2];positions.set([origin.x+between(-.35,.35),origin.y,origin.z+between(-.35,.35)],i*3);phases[i]=rand();}
  const emberGeo=new THREE.BufferGeometry();emberGeo.setAttribute('position',new THREE.BufferAttribute(positions,3));emberGeo.setAttribute('phase',new THREE.BufferAttribute(phases,1));
  const emberMat=new THREE.ShaderMaterial({uniforms:{uTime:{value:0}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute float phase;uniform float uTime;varying float alpha;void main(){float life=fract(phase+uTime*.12);vec3 p=position;p.y+=life*3.2;p.x+=sin(life*7.+phase*30.)*.2+life*.5;p.z+=cos(life*6.+phase*30.)*.2;alpha=sin(life*3.14159);gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);gl_PointSize=2.5*(1.-life*.6);}`,
    fragmentShader:`varying float alpha;void main(){float d=length(gl_PointCoord-.5);if(d>.5)discard;gl_FragColor=vec4(2.8,1.1,.22,alpha*(1.-d*2.));}`});scene.add(new THREE.Points(emberGeo,emberMat));
  const motePos=new Float32Array(100*3);
  for(let i=0;i<100;i++)motePos.set([between(-15,15),between(.3,9),between(-13,15)],i*3);
  const moteGeo=new THREE.BufferGeometry();moteGeo.setAttribute('position',new THREE.BufferAttribute(motePos,3));
  const moteMat=new THREE.PointsMaterial({color:0xadc4bf,size:.022,transparent:true,opacity:.27,depthWrite:false});const motes=new THREE.Points(moteGeo,moteMat);scene.add(motes);
  const fogMat=new THREE.ShaderMaterial({uniforms:{uTime:{value:0},uColor:{value:new THREE.Color(0x304b65)},uOpacity:{value:.28}},transparent:true,depthWrite:false,side:THREE.DoubleSide,
    vertexShader:`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
    fragmentShader:`uniform float uTime;uniform float uOpacity;uniform vec3 uColor;varying vec2 vUv;float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.54);}float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}void main(){vec2 p=vUv*vec2(6.,3.);float f=n(p+vec2(uTime*.017,0.))*.65+n(p*2.1-vec2(uTime*.012,0.))*.35;float edge=sin(vUv.x*3.14159)*sin(vUv.y*3.14159);gl_FragColor=vec4(uColor,smoothstep(.40,.68,f)*edge*uOpacity);}`});
  fogMat.forceSinglePass=true;
  for(let i=0;i<10;i++){let fog=mesh(new THREE.PlaneGeometry(55,15),fogMat,between(-14,14),-3-i*1.5,-15+i*5);fog.castShadow=false;fog.rotation.x=-.2;fog.renderOrder=3;}
  const baseHazeMat=fogMat.clone();baseHazeMat.uniforms.uOpacity.value=.73;baseHazeMat.uniforms.uColor.value.set(0x344855);
  for(const [x,y,z,w,h] of [[-17,-8,-8,21,14],[18,-10,2,22,18],[-15,-5,-9,24,12],[18,-16,4,24,15],[-17,-15,-6,25,16]]){
    const f=mesh(new THREE.PlaneGeometry(w,h),baseHazeMat,x,y,z);f.castShadow=false;f.renderOrder=3;
  }
  for(let i=0;i<5;i++){let fog=mesh(new THREE.PlaneGeometry(70,28),fogMat,-5+i*2,4,-13-i*8);fog.castShadow=false;fog.renderOrder=3;}
  const blockers=[{x:-7.2,z:3.7,r:1.42},{x:-2.15,z:-2.3,r:1.05},{x:7.75,z:-2.3,r:1.05},{x:-1.65,z:-1.45,r:.87},{x:6.9,z:-1.45,r:.87}];
  function loadStone(){const loader=new GLTFLoader();return Promise.all([loader.loadAsync('/models/stone-v5.glb'),loader.loadAsync('/models/stone-v4-far.glb')]).then(([asset,farAsset])=>{
    const names=['Flagstone_Split','Flagstone_Spalled','Flagstone_Laminated','Flagstone_Weathered','Flagstone_Cleft','Flagstone_Granular','Flagstone_Worn','Flagstone_Branched','Masonry_Broken','Masonry_Quarried'];
    const geometries=names.map(name=>asset.scene.getObjectByName(name)?.geometry);
    if(geometries.some(g=>!g))throw new Error('Stone variant missing');
    stoneInstances.forEach(inst=>{inst.geometry=geometries[inst.userData.variant];inst.computeBoundingSphere();});farObjects.filter(o=>o.isInstancedMesh).forEach((inst,i)=>{inst.geometry=farAsset.scene.getObjectByName(names[8+i%2]).geometry;inst.computeBoundingSphere();});renderer.shadowMap.needsUpdate=true;
  });}

  return {materials:{stone,floorMat},wetMaskProbe, water, halo, blockers, rand, between,loadStone,farObjects,stoneInstances,
    update(time){
      halo.position.y=platformY+2.72+Math.sin(time*.85)*.07;orbit1.rotation.y=1.1+time*.16;orbit2.rotation.x=.92+time*.12;center.rotation.y=time*.4;
      flames.forEach(f=>{f.mesh.scale.set(f.sx*(1+Math.sin(time*7+f.phase)*.07),f.sy*(1+Math.sin(time*10+f.phase)*.12),1);f.mesh.position.y=f.y+Math.sin(time*8+f.phase)*.045;f.mesh.rotation.y=time*.7+f.phase;});
      fireLights.forEach((l,i)=>l.intensity=(i===0?23:33)+Math.sin(time*9+i*2)*1.8+Math.sin(time*17+i)*1.2);flameMat.uniforms.uTime.value=time;flameTime.value=time;
      water.material.uniforms.uTime.value=time;emberMat.uniforms.uTime.value=time;fogMat.uniforms.uTime.value=time;baseHazeMat.uniforms.uTime.value=time;if(grassShader)grassShader.uniforms.windTime.value=time;
      motes.position.x=Math.sin(time*.09)*.4;motes.position.y=Math.sin(time*.15)*.12;
    }
  };
}







