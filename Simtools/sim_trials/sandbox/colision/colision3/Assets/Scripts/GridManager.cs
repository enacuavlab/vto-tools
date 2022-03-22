using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GridManager : MonoBehaviour
{
  const int strlength = 13;
  const string str="             \n"+
                   "   x     x   \n"+
                   "  xxxxxxxxx  \n"+
                   " xxx xxx xxx \n"+
                   " xxx xxx xxx \n"+
                   " xxxxxxxxxxx \n"+
                   " x xxxxxxx x \n"+
                   " x x     x x \n"+ 
                   "    x   x    \n"+
                   "             ";

  public Sprite sprite;
  private GameObject source1,sink1;
 

  void Start() {

    Camera.main.orthographic = true;
    Camera.main.orthographicSize = 6;
    Camera.main.transform.position = new Vector3(4.5f,50.0f,6.0f);
    //Camera.main.transform.rotation = Quaternion.Euler(90,0,90);
    
    string[] strs = str.Split('\n');
    bool[,] sp=new bool[strs.Length,strlength];
    for (int i=0;i<strs.Length;i++) {
      for (int j=0;j<(strs[i].Length);j++) {
        SpawnTile(i,j,(strs[i][j].Equals('x')));
      }
    }

    GameObject cube1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube1.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube1.transform.position = new Vector3(4.359f, 0.0f, 6.0f);
/*
    GameObject cube2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube2.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube2.transform.position = new Vector3(2.0f, 0.0f, 4.5f);
    GameObject cube3 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube3.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube3.transform.localRotation = Quaternion.Euler(0,45,0);
    cube3.transform.position = new Vector3(5.12f, 0.0f, 8.25f);
*/   
    source1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    source1.transform.localScale = new Vector3(0.5f,0.01f,0.5f);
    source1.transform.position = new Vector3(4.5f,0.0f,2.0f);
    sink1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    sink1.transform.localScale = new Vector3(0.5f,0.01f,0.5f);
    sink1.transform.position = new Vector3(4.5f,0.0f,9.5f);
  }
   

  private void SpawnTile(int x, int y, bool value) {
    GameObject g = new GameObject(); 
    g.transform.position = new Vector3(x,0,y);
    g.transform.rotation = Quaternion.Euler(90,0,0);
    SpriteRenderer r = g.AddComponent<SpriteRenderer>();
    r.sprite = sprite;
    if(value) r.color = Color.red;
    else r.color=Color.blue;
  }


  void FixedUpdate() {
    Camera.main.transform.LookAt(new Vector3(4.5f, 0.0f, 6.0f));
    //Camera.main.transform.rotation = Quaternion.Euler(90,0,90);
  }


  struct elt_t {
    public Vector3 pos;
    public Vector3 trans;
  };
  List<elt_t>elts0 = new List<elt_t>();
  List<elt_t>elts1 = new List<elt_t>();
  List<elt_t>elts2 = new List<elt_t>();
  
  void Update() {
    RaycastHit hit;
    elts0.Clear();
    elts0.Add(new elt_t() {pos=source1.transform.position});
    Vector3 dir = (sink1.transform.position - source1.transform.position);   
    Ray ray = new Ray(source1.transform.position,dir.normalized);
    if(Physics.Raycast(ray,out hit,dir.magnitude)) {
      if ((dir.magnitude - hit.distance)<0.26) {
      } else {
        Vector3 pos = hit.point - dir.normalized * 0.1f;
        if (Vector3.Dot(dir.normalized,hit.normal.normalized)==-1) {
	  elts1.Clear();
	  elts2.Clear();
          elts1.Add(new elt_t() {pos=pos, trans=new Vector3(dir.z,0,dir.x)});
          elts2.Add(new elt_t() {pos=pos, trans=new Vector3(-dir.z,0,-dir.x)});
          bool ret1=true,ret2=true;
          while (ret1 && ret2) {
            if(ret2) ret1=ComputePath(elts1);
            if(ret1) ret2=ComputePath(elts2);
	  }
          if(ret1) elts0.AddRange(elts2);
          if(ret2) elts0.AddRange(elts1);
	}
      }
    }
    elts0.Add(new elt_t() {pos=sink1.transform.position});
    for (int i=0;i<(elts0.Count-1);i++) Debug.DrawRay(elts0[i].pos,elts0[i+1].pos-elts0[i].pos,Color.blue);
    Debug.Log("Update");
  }


  private bool ComputePath(List<elt_t> lst) {
    RaycastHit hit;
    bool ret=true;
    int idx=lst.Count-1;
    Vector3 pos = lst[idx].pos + lst[idx].trans.normalized * 0.05f;
    Vector3 dir = (sink1.transform.position - pos);   
    //Debug.DrawRay(lst[idx].pos,pos-lst[idx].pos,Color.yellow);
    lst.Add(new elt_t() {pos=pos, trans=(pos-lst[idx].pos)});
    Ray ray = new Ray(pos,dir.normalized);
    if(Physics.Raycast(ray,out hit,dir.magnitude)) {
      if((dir.magnitude - hit.distance)<0.26) {
        ret=false;
      } 
    }
    return(ret);
  }
        
//        Vector3 myrefdir = Vector3.ProjectOnPlane(dir.normalized, hit.normal);
}
