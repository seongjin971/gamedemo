// Small fixed navigation region with A* around architectural obstacles.
// The visible world is much larger than this walkable courtyard.
export function createNavigation(blockers) {
  const step=.34,minX=-7.8,maxX=7.8,minZ=-1.25,maxZ=11.4;
  const cols=Math.floor((maxX-minX)/step)+1,rows=Math.floor((maxZ-minZ)/step)+1;
  function valid(x,z,margin=.28) {return x>=minX&&x<=maxX&&z>=minZ&&z<=maxZ&&!blockers.some(b=>Math.hypot(x-b.x,z-b.z)<b.r+margin);}
  const point=(id)=>({x:minX+(id%cols)*step,z:minZ+Math.floor(id/cols)*step});
  const grid=new Uint8Array(cols*rows);
  for(let i=0;i<grid.length;i++){const p=point(i);grid[i]=valid(p.x,p.z)?1:0;}
  function closest(x,z){let best=-1,d=Infinity;for(let i=0;i<grid.length;i++){if(!grid[i])continue;const p=point(i),v=(p.x-x)**2+(p.z-z)**2;if(v<d){d=v;best=i;}}return best;}
  function path(from,to) {
    const start=closest(from.x,from.z),goal=closest(to.x,to.z);
    const open=new Set([start]),came=new Int32Array(grid.length).fill(-1),g=new Float32Array(grid.length).fill(Infinity),f=new Float32Array(grid.length).fill(Infinity);g[start]=0;
    const target=point(goal),heuristic=id=>{const p=point(id);return Math.hypot(p.x-target.x,p.z-target.z);};f[start]=heuristic(start);
    while(open.size){let current=-1,best=Infinity;for(const id of open)if(f[id]<best){best=f[id];current=id;}
      if(current===goal){const result=[];let id=current;while(id!==start){result.push(point(id));id=came[id];}return result.reverse();}
      open.delete(current);const cx=current%cols,cz=Math.floor(current/cols);
      for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++) {
        if((dx===0&&dz===0)||cx+dx<0||cx+dx>=cols||cz+dz<0||cz+dz>=rows)continue;
        const n=current+dz*cols+dx;if(!grid[n])continue;
        if(dx&&dz&&(!grid[current+dx]||!grid[current+dz*cols]))continue;
        const score=g[current]+step*(dx&&dz?Math.SQRT2:1);
        if(score<g[n]){came[n]=current;g[n]=score;f[n]=score+heuristic(n);open.add(n);}
      }
    }
    return [];
  }
  return {valid,path,bounds:{minX,maxX,minZ,maxZ},closest:(x,z)=>point(closest(x,z))};
}
