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

  struct elt_t {
    public Vector3 pos;
  };
  List<elt_t>elts = new List<elt_t>();

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
    cube1.transform.position = new Vector3(4.0f, 0.0f, 6.0f);
/*
    GameObject cube2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube2.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube2.transform.position = new Vector3(2.0f, 0.0f, 4.5f);
    GameObject cube3 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube3.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube3.transform.localRotation = Quaternion.Euler(0,45,0);
    cube3.transform.position = new Vector3(5.12f, 0.0f, 8.25f);
*/   
    source1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    source1.transform.localScale = new Vector3(0.15f,0.01f,0.05f);
    source1.transform.position = new Vector3(4.5f,0.0f,2.0f);
    sink1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    sink1.transform.localScale = new Vector3(0.15f,0.01f,0.05f);
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


 
  const float dronemetersize = 0.5f;  
  const float slidestep = 10.0f;  

  void FixedUpdate() {
    Camera.main.transform.LookAt(new Vector3(4.5f, 0.0f, 6.0f));

    if(elts.Count==0) elts.Add(new elt_t() {pos=source1.transform.position});
    Vector3 dir = (sink1.transform.position-elts[elts.Count-1].pos);   
    float scale=(dir.magnitude/dronemetersize);
    RaycastHit Lhit,Rhit;
    Physics.Raycast(new Ray(elts[elts.Count-1].pos+new Vector3(dir.z,0,dir.x)/(dir.magnitude*scale),
			    dir.normalized),out Rhit,dir.magnitude);
    Physics.Raycast(new Ray(elts[elts.Count-1].pos+new Vector3(-dir.z,0,-dir.x)/(dir.magnitude*scale),
			    dir.normalized),out Lhit,dir.magnitude);
    bool Rhitflag = ((Rhit.distance/dir.magnitude)<0.96f);
    bool Lhitflag = ((Lhit.distance/dir.magnitude)<0.96f);

    string str="";for(int i=0;i<elts.Count;i++) str+=elts[i].pos;
    Debug.Log(elts.Count+" "+elts[elts.Count-1].pos+" "+Lhitflag+" "+Lhit.point+" "+Rhitflag+Rhit.point+" Update"+str);

    if (!Rhitflag && Lhitflag) {
      Debug.Log("1");
      elts.Add(new elt_t() {pos=(Lhit.point+new Vector3(dir.z,0,dir.x)/(dir.magnitude*slidestep))}); // Slide Right
    }
    
    if (!Lhitflag && Rhitflag) {
      Debug.Log("2");
      //elts.Add(new elt_t() {pos=(Rhit.point+new Vector3(dir.z,0,dir.x)/(dir.magnitude*slidestep))}); // Slide Right
    }
  
    if (Lhitflag && Rhitflag) {
      Debug.Log("3");
    }
    

    if (!Rhitflag && !Lhitflag) {
      Debug.Log("0");

      elts.Add(new elt_t() {pos=sink1.transform.position});

      for (int i=0;i<(elts.Count-1);i++) {
        dir = elts[i+1].pos - elts[i].pos;
        Debug.DrawRay(elts[i].pos+new Vector3(dir.z,0,dir.x)/(dir.magnitude*scale),dir,Color.yellow); // Right
        Debug.DrawRay(elts[i].pos+new Vector3(-dir.z,0,-dir.x)/(dir.magnitude*scale),dir,Color.yellow); // Left
      }

      elts.Clear();
    }
  }
}


/*
      Lpos = Lhit.point - dir.normalized * 0.1f;
      Rpos = Rhit.point - dir.normalized * 0.1f;

      if((Vector3.Dot(dir.normalized,Lhit.normal.normalized)==-1) &&
        (Vector3.Dot(dir.normalized,Lhit.normal.normalized)==-1)) {

        elts1.Clear();
        elts2.Clear();
        elts1.Add(new elt_t() {Lpos=Lpos, Rpos=Rpos, trans=new Vector3(dir.z,0,dir.x)});
        elts2.Add(new elt_t() {Lpos=Lpos, Rpos=Rpos, trans=new Vector3(-dir.z,0,-dir.x)});

        bool ret1=true,ret2=true;
        while (ret1 && ret2) {
          if(ret2) ret1=GoAroundObstacle(elts1);
          if(ret1) ret2=GoAroundObstacle(elts2);
        }
        if(ret1) elts0.AddRange(elts2);
        if(ret2) elts0.AddRange(elts1);
      }
*/


  /*
  private bool GoAroundObstacle(List<elt_t> lst) {
    bool ret=true;
    int idx=lst.Count-1;
/*
    Vector3 Lpos = lst[idx].Lpos + lst[idx].trans.normalized * 0.05f;
    Vector3 Rpos = lst[idx].Rpos + lst[idx].trans.normalized * 0.05f;

    Vector3 Lsink = sink1.transform.position-new Vector3(dir.z,0,dir.x);
    Vector3 dir = (Lsink - Lpos);   

    lst.Add(new elt_t() {Lpos=Lpos,Rpos=Rpos, trans=(Lpos-lst[idx].Lpos)});

    Ray Lray = new Ray(Lpos,dir.normalized);
    Ray Rray = new Ray(Rpos,dir.normalized);

    RaycastHit Lhit,Rhit;
    Physics.Raycast(Lray,out Lhit,dir.magnitude);
    Physics.Raycast(Rray,out Rhit,dir.magnitude);

    if (((dir.magnitude - Lhit.distance)<0.26) && ((dir.magnitude - Rhit.distance)<0.26)) {
        ret=false;
      } 
    }
    ret=false;
    return(ret);
  }
*/
        
//        Vector3 myrefdir = Vector3.ProjectOnPlane(dir.normalized, hit.normal);
