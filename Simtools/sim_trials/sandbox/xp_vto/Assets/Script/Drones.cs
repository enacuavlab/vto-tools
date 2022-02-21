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
  private int receivePort = 5558;
  private UdpClient udpClient;
  private IPEndPoint remoteIpEndPoint;
  private IPAddress mcastAddr;
  private Thread receiveThread;
  private bool threadRunning = false;
  private string message = "";
  private bool mcastBool = false;
  
  string myLog="";
  List<string> items = new List<string>();
  private int nLogs=30;

  private Dictionary <int, GameObject> drones = new Dictionary <int, GameObject> ();

  private Color[] colors = {Color.green,Color.red, Color.blue, Color.white};

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
    string tmp="",head="";
    string[] words;
    if (message!="") {
      lock (message) {
        tmp=message;
        message="";
      }
      words=tmp.Split(' ');head=words[0];
      words = words.Skip(1).ToArray();     
      float[] floatData = Array.ConvertAll(words, float.Parse);
//      float[] floatData = Array.ConvertAll(tmp.Split(' '), float.Parse); 
      Vector3 pos=new Vector3(-floatData[1],floatData[3],-floatData[2]);
      Quaternion att=new Quaternion(floatData[4],-floatData[5],-floatData[6],floatData[7]);
      if(drones.ContainsKey((int)floatData[0])) {
        drones[(int)floatData[0]].transform.position=pos;
        drones[(int)floatData[0]].transform.rotation=att;
      } else {
	GameObject instance = Instantiate(prefab,pos,att);
	MeshRenderer mr = instance.GetComponentsInChildren<MeshRenderer>()[0];
	mr.material.color = colors[drones.Count];
        mr.enabled = true;
        drones.Add((int)floatData[0],instance);
      }
    }
  }


  private void ListenForMessages() {   
    while (threadRunning) {
      try {
        Byte[] receiveBytes = udpClient.Receive(ref remoteIpEndPoint); // Blocking
        string returnData = Encoding.UTF8.GetString(receiveBytes);
        lock (message) {
          string [] lines = returnData.Split('\n');
          if (lines.Length > 1) returnData=lines[lines.Length-2]; // Keep last line
          message=returnData;          
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
