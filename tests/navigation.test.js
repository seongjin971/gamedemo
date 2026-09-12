import test from 'node:test';
import assert from 'node:assert/strict';
import { createNavigation } from '../src/navigation.js';

const obstacle={x:0,z:5,r:1.4};
const navigation=createNavigation([obstacle]);
test('a path crosses the courtyard without intersecting a large obstacle',()=>{
  const start={x:-6,z:5},end={x:6,z:5},path=navigation.path(start,end);
  assert.ok(path.length>0);assert.ok(Math.hypot(path.at(-1).x-end.x,path.at(-1).z-end.z)<.5);
  let previous=start;
  for(const p of path){
    assert.ok(navigation.valid(p.x,p.z));
    for(let t=0;t<=1;t+=.1){const x=previous.x+(p.x-previous.x)*t,z=previous.z+(p.z-previous.z)*t;assert.ok(Math.hypot(x,z-5)>obstacle.r+.24);}
    previous=p;
  }
});
test('world outside the courtyard and obstacle centers are nonwalkable',()=>{
  for(const p of [[-8,5],[8,5],[0,-2],[0,12],[0,5]])assert.equal(navigation.valid(...p),false);
});
test('all sampled destinations terminate in the valid bounded region',()=>{
  for(let x=-7;x<=7;x+=2)for(let z=0;z<11;z+=2){
    if(!navigation.valid(x,z))continue;
    const path=navigation.path({x:6,z:10},{x,z});
    assert.ok(path.length>0);assert.ok(path.every(p=>navigation.valid(p.x,p.z)));
    assert.ok(Math.hypot(path.at(-1).x-x,path.at(-1).z-z)<.5);
  }
});
