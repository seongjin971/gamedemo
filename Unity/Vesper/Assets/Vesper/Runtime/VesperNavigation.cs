using System;
using System.Collections.Generic;
using UnityEngine;

// Browser courtyard A* port. Input/output are Unity coordinates (Three X negated).
public sealed class VesperNavigation {
    const float Step=.34f,Min=-7.8f,Max=7.8f,MinZ=-1.25f,MaxZ=11.4f;
    readonly int cols=Mathf.FloorToInt((Max-Min)/Step)+1,rows=Mathf.FloorToInt((MaxZ-MinZ)/Step)+1;
    readonly bool[] grid;readonly Vector3[] blockers={new Vector3(-7.2f,3.7f,1.42f),new Vector3(-2.15f,-2.3f,1.05f),new Vector3(7.75f,-2.3f,1.05f),new Vector3(-1.65f,-1.45f,.87f),new Vector3(6.9f,-1.45f,.87f)};
    readonly VesperNavigationObstacle[] obstacles;
    public VesperNavigation(){obstacles=UnityEngine.Object.FindObjectsByType<VesperNavigationObstacle>();grid=new bool[cols*rows];for(int i=0;i<grid.Length;i++)grid[i]=Valid(Point(i));}
    Vector3 Point(int id)=>new Vector3(-(Min+(id%cols)*Step),0,MinZ+(id/cols)*Step);
    public bool Valid(Vector3 p){float x=-p.x,z=p.z;if(x<Min||x>Max||z<MinZ||z>MaxZ)return false;for(int i=obstacles.Length>0?1:0;i<blockers.Length;i++){var b=blockers[i];if(Vector2.Distance(new Vector2(x,z),new Vector2(b.x,b.y))<b.z+.28f)return false;}foreach(var obstacle in obstacles)if(obstacle.Blocks(p,.28f))return false;return true;}
    int Closest(Vector3 p){int result=-1;float best=float.PositiveInfinity;for(int i=0;i<grid.Length;i++){if(!grid[i])continue;float d=(Point(i)-p).sqrMagnitude;if(d<best){best=d;result=i;}}return result;}
    public List<Vector3> Path(Vector3 from,Vector3 to){var result=new List<Vector3>();if(!Valid(to))return result;int start=Closest(from),goal=Closest(to);if(start<0||goal<0)return result;
      var open=new HashSet<int>{start};var came=new int[grid.Length];var g=new float[grid.Length];var f=new float[grid.Length];for(int i=0;i<grid.Length;i++){came[i]=-1;g[i]=f[i]=float.PositiveInfinity;}g[start]=0;f[start]=Vector3.Distance(Point(start),Point(goal));
      while(open.Count>0){int current=-1;float best=float.PositiveInfinity;foreach(int id in open)if(f[id]<best){best=f[id];current=id;}if(current==goal){for(int id=current;id!=start;id=came[id])result.Add(Point(id));result.Reverse();return result;}open.Remove(current);int cx=current%cols,cz=current/cols;
        for(int dz=-1;dz<=1;dz++)for(int dx=-1;dx<=1;dx++){if((dx==0&&dz==0)||cx+dx<0||cx+dx>=cols||cz+dz<0||cz+dz>=rows)continue;int n=current+dz*cols+dx;if(!grid[n]||(dx!=0&&dz!=0&&(!grid[current+dx]||!grid[current+dz*cols])))continue;float cost=g[current]+Step*(dx!=0&&dz!=0?Mathf.Sqrt(2):1);if(cost<g[n]){came[n]=current;g[n]=cost;f[n]=cost+Vector3.Distance(Point(n),Point(goal));open.Add(n);}}
      }return result;
    }
}
