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
  public GameObject source1,sink1;
  
  void Start() {
    Camera.main.orthographicSize = 6;
    Camera.main.transform.position = new Vector3(4.5f,50.0f,6.0f);
    //Camera.main.transform.rotation = Quaternion.Euler(90,0,90);
    
    string[] strs = str.Split('\n');
    bool[,] sp=new bool[strs.Length,strlength];
    for(int i=0;i<strs.Length;i++){
      for(int j=0;j<(strs[i].Length);j++){
        SpawnTile(i,j,(strs[i][j].Equals('x')));
      }
    }
    
    GameObject cube1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube1.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube1.transform.position = new Vector3(4.5f, 0.0f, 6.0f);
    GameObject cube2 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube2.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube2.transform.position = new Vector3(2.0f, 0.0f, 4.5f);
    GameObject cube3 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube3.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube3.transform.localRotation = Quaternion.Euler(0,45,0);
    cube3.transform.position = new Vector3(5.12f, 0.0f, 8.25f);
    
    source1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    source1.transform.localScale = new Vector3(0.5f,0.01f,0.5f);
    source1.transform.position = new Vector3(5.5f,0.0f,2.0f);
    sink1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    sink1.transform.localScale = new Vector3(0.5f,0.01f,0.5f);
    sink1.transform.position = new Vector3(4.8f,0.0f,9.5f);
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
 
  void Update() {
    Vector3 dir = (sink1.transform.position - source1.transform.position).normalized;   
    Ray ray = new Ray(source1.transform.position,dir);
    RaycastHit hit;
    if(Physics.Raycast(ray,out hit,10.0f)) {
      Debug.DrawRay(source1.transform.position, dir*hit.distance, Color.yellow);
      Vector3 refdir = Vector3.Reflect(dir, hit.normal);
      Debug.DrawRay(hit.point,refdir,Color.blue);
      //Vector3 tangent = Vector3.ProjectOnPlane(this.velocity, hit.normal).normalized;
               
      Debug.Log("Did Hit");
    } else {
      Debug.DrawRay(source1.transform.position, dir*10.0f, Color.green);
      Debug.Log("Not Hit");
    }
  }

}
