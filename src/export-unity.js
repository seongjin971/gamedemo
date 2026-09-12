import * as THREE from 'three';

// Read logical components: Sprite geometry shares one interleaved position/UV
// buffer, so copying its backing array would corrupt both attributes.
export function attributeComponents(attribute) {
  if (!attribute) return [];
  const result = [];
  for (let i = 0; i < attribute.count; i++) {
    for (let component = 0; component < attribute.itemSize; component++) {
      result.push(attribute.getComponent(i, component));
    }
  }
  return result;
}

// Explicit development export. Geometry and transforms remain in Three's basis;
// the Unity importer reflects X and reverses triangle winding exactly once.
export async function exportUnity(scene, camera, world, player, composer, canvas) {
  scene.updateMatrixWorld(true);
  const geometries = new Map(), materials = new Map(), nodes = [];
  const far = new Set(world.farObjects);
  const textureName = t => {
    const s=t?.source?.data?.currentSrc || t?.source?.data?.src || '';
    return s.includes('/textures/') ? s.split('/textures/')[1].split('?')[0] : '';
  };
  function material(m) {
    if (materials.has(m.uuid)) return m.uuid;
    materials.set(m.uuid, {id:m.uuid,name:m.name||m.type,type:m.type,
      color:m.color?.toArray()||[1,1,1],emissive:m.emissive?.toArray()||[0,0,0],
      emissiveIntensity:m.emissiveIntensity||0,roughness:m.roughness??1,metalness:m.metalness??0,
      opacity:m.opacity??1,transparent:!!m.transparent,side:m.side,map:textureName(m.map),
      normalMap:textureName(m.normalMap),normalScale:m.normalScale?.toArray()||[1,1],
      clearcoat:m.clearcoat||0,vertexColors:!!m.vertexColors,distant:!!m.userData.distant});
    return m.uuid;
  }
  function geometry(g) {
    if (!geometries.has(g.uuid)) {
      const attr = n => attributeComponents(g.getAttribute(n));
      geometries.set(g.uuid,{id:g.uuid,name:g.name||g.type,positions:attr('position'),normals:attr('normal'),uv:attr('uv'),colors:attr('color'),indices:g.index?Array.from(g.index.array):[],groups:g.groups});
    }
    return g.uuid;
  }
  function visit(o,parentId='',inheritedFar=false) {
    const distant=inheritedFar||far.has(o);if(o===world.water)return;
    if(o.isLight||o.isCamera)return;
    if(o.isPoints||o.isLine||o.material?.isShaderMaterial)return;
    const mat=o.material ? (Array.isArray(o.material)?o.material:[o.material]).map(material) : [];
    const node={id:o.uuid,parent:parentId,name:o.name||o.type,type:o.type,distant,
      position:o.position.toArray(),quaternion:o.quaternion.toArray(),scale:o.scale.toArray(),
      geometry:o.geometry?geometry(o.geometry):'',materials:mat,instances:[],castShadow:!!o.castShadow,visible:o.visible};
    if(o.isInstancedMesh){const matrix=new THREE.Matrix4(),p=new THREE.Vector3(),q=new THREE.Quaternion(),s=new THREE.Vector3(),c=new THREE.Color();
      for(let i=0;i<o.count;i++){o.getMatrixAt(i,matrix);matrix.decompose(p,q,s);if(o.instanceColor)o.getColorAt(i,c);else c.setRGB(1,1,1);node.instances.push({position:p.toArray(),quaternion:q.toArray(),scale:s.toArray(),color:c.toArray()});}}
    nodes.push(node);for(const child of o.children)visit(child,o.uuid,distant);
  }
  for(const o of scene.children)visit(o);
  const post=async(label,metrics)=>{const r=await fetch('/__qa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label,metrics})});if(!r.ok)throw new Error('Unity export '+r.status);};
  for(const g of geometries.values())await post('unity-geometry-'+g.id,g);
  const saved={position:camera.position.clone(),quaternion:camera.quaternion.clone(),zoom:camera.zoom};
  const target=new THREE.Vector3(-2.3,2.1,4),angle=.46,elevation=.72,r=42;
  let image,probeCamera;
  try {
    camera.position.set(target.x+Math.sin(angle)*Math.cos(elevation)*r,target.y+Math.sin(elevation)*r,target.z+Math.cos(angle)*Math.cos(elevation)*r);
    camera.lookAt(target);camera.zoom=14.1/8.4;camera.updateProjectionMatrix();camera.updateMatrixWorld();
    composer.render();image=canvas.toDataURL('image/png');
    probeCamera={position:camera.position.toArray(),quaternion:camera.quaternion.toArray(),target:target.toArray(),orthoHeight:16.8,width:innerWidth,height:innerHeight};
  }finally{camera.position.copy(saved.position);camera.quaternion.copy(saved.quaternion);camera.zoom=saved.zoom;camera.updateProjectionMatrix();camera.updateMatrixWorld();}
  const screenshotResult=await fetch('/__qa',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({label:'unity-browser-slice',image,metrics:probeCamera})});
  if(!screenshotResult.ok)throw new Error('Slice capture failed');
  const manifest={version:1,basis:'Three.js Y-up; Unity reflects X, reverses winding',timestamp:new Date().toISOString(),camera:probeCamera,player:player.uuid,geometryIds:[...geometries.keys()],materials:[...materials.values()],nodes};
  await post('unity-scene',manifest);
  return {geometryCount:geometries.size,materialCount:materials.size,nodeCount:nodes.length};
}
