/*
test.x86_64
test.x86_64 5553 
test.x86_64 5553 237.252.249.227
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;
using System.Linq;


public class Drones : MonoBehaviour
{
  private struct move_t {
    public int id;
    public Vector3 pos;
    public Quaternion att;
  }
  private List<move_t> buffer = new List<move_t>();
      
  private int receivePort = 5558;
  private UdpClient udpClient;
  private IPEndPoint remoteIpEndPoint;
  private IPAddress mcastAddr;
  private bool mcastBool = false;
  private Thread receiveThread;
  private bool threadRunning = false;

  
  string myLog="";
  List<string> items = new List<string>();
  private int nLogs=30;

  private Dictionary <int, GameObject> drones = new Dictionary <int, GameObject> ();

  private Color[] colors = {Color.green,Color.red, Color.blue, Color.cyan, Color.magenta, Color.yellow};

  private static string[] GetArg() {
    return(System.Environment.GetCommandLineArgs());
  }  
  
  private GameObject prefab;

  void Awake() {
    prefab = new GameObject();
    GameObject obj = new GameObject();
    obj.transform.parent = prefab.transform;
    MeshRenderer mr = obj.AddComponent<MeshRenderer>();
    mr.enabled = false;
    MeshFilter mf = obj.AddComponent<MeshFilter>();
    mf.mesh = Resources.Load<Mesh>("robobee"); 
    obj.transform.transform.position=new Vector3(0.0f,0.1f,0.0f);
    obj.transform.rotation=Quaternion.Euler(0, 90, 0);
    obj.transform.localScale=new Vector3(2.0f,2.0f,2.0f);
  }


  void Start() {
    Debug.Log("Start");
    string[] args = GetArg();
    if(args.Length>1) {
      if(args[1].All(char.IsDigit)) { 
        receivePort=Convert.ToInt32(args[1].ToString(), 10);
        if((args.Length>2)&&(IPAddress.TryParse(args[2], out mcastAddr))) mcastBool = true;
      }
    }
    try { 
      remoteIpEndPoint = new IPEndPoint(IPAddress.Any, receivePort);
      udpClient = new UdpClient(remoteIpEndPoint);
      Debug.Log(receivePort);
      if(mcastBool) {
        udpClient.JoinMulticastGroup(mcastAddr);     
        Debug.Log(mcastAddr);
      }
    } catch (Exception e) {
      Debug.Log("Failed to listen for UDP at port " + receivePort + ": " + e.Message);
      return;
    }        
    receiveThread = new Thread(() => ListenForMessages());
    receiveThread.IsBackground = true;
    threadRunning = true;
    receiveThread.Start();  
  }


  void Update() {
    while(buffer.Count>0){
      move_t elt=buffer.ElementAt(0);
      if(drones.ContainsKey(elt.id)) {
        drones[elt.id].transform.position=elt.pos;
        drones[elt.id].transform.rotation=elt.att;
      } else {
	GameObject instance = Instantiate(prefab,elt.pos,elt.att);
        MeshRenderer mr = instance.GetComponentsInChildren<MeshRenderer>()[0];
	mr.material.color = colors[drones.Count];
        mr.enabled = true;
        drones.Add(elt.id,instance);
      }
      buffer.RemoveAt(0);
    }
  }


  private void ListenForMessages() {   
    while (threadRunning) {
      try {
        Byte[] receiveBytes = udpClient.Receive(ref remoteIpEndPoint); // Blocking
        string tmp = Encoding.UTF8.GetString(receiveBytes);
        string [] lines = tmp.Split('\n');
        for(int i=0;i<lines.Length;i++) {  
          if(lines[i].Length!=0) {      
            string[] words=lines[i].Split(' ');
            words = words.Skip(1).ToArray();       
            float[] floatData = Array.ConvertAll(words, float.Parse);
            buffer.Add(new move_t(){id=(int)floatData[0],
              pos=new Vector3(-floatData[1],floatData[3],-floatData[2]),
              att=new Quaternion(floatData[4],-floatData[5],-floatData[6],floatData[7])});            
          }
        }
      }
      catch (SocketException e) {
        if (e.ErrorCode != 10004) Debug.Log("Socket exception while receiving data from udp client: " + e.Message);
      }
      catch (Exception e) {
        Debug.Log("Error receiving data from udp client: " + e.Message);
      }
      Thread.Sleep(1);  
    }
  }
     
     
  void OnEnable () {
    Application.logMessageReceived += HandleLog;
  }
   
     
  void OnDisable () {
    Application.logMessageReceived -= HandleLog;
  }
 
 
  void HandleLog(string logString, string stackTrace, LogType type) {
    items.Add(logString);
    if(items.Count > nLogs) items.RemoveAt(0);
    myLog="";
    foreach (string k in items) {
      myLog += "[" + k + "]\n";
    }
  }
  
  
  void OnGUI () {
    GUI.Label(new Rect(0, Screen.height-450f, Screen.width, Screen.height),myLog);
    //GUI.Label(new Rect(Screen.width / 2f, Screen.height / 2f, Screen.width, Screen.height),myLog);
    //GUILayout.Label(myLog);
  }
}
