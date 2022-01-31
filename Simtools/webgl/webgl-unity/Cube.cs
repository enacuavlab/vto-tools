// The default started configuration containes 'Main Camera' and 'Directional Light'
// Create a GameObject / 3D Object / Cube
// Associate this file to the Cube

/*
Build and store webgl next to http-websocket server
*/

using System;
using System.Collections;
using System.Collections.Generic;
using System.Windows;
using System.Text;
using UnityEngine;

using NativeWebSocket;

public class Cube : MonoBehaviour
{

  private WebSocket websocket = null;  
  private string url = "ws://10.42.0.64:8080";

  private string message = "";
  
  string myLog="";
  List<string> items = new List<string>();
  private int nLogs=10;
  
  void Start() { 
    transform.localScale=new Vector3(5.0f,1.0f,10.0f);
    transform.position=new Vector3(0.0f,0.0f,10.0f);
    websocket = new WebSocket(url);
    websocket.OnMessage += (receiveBytes) => {
      string returnData = Encoding.UTF8.GetString(receiveBytes);
      lock (message) {
        string [] lines = returnData.Split('\n');
          if (lines.Length > 1) returnData=lines[lines.Length-2]; // Keep last line
          message=returnData;
      } 
    };        
    MyConnect();
  }

  async void MyConnect() {
      await websocket.Connect();
  }
      
  void Update() {
    string tmp="";
    if (message!="") {
      lock (message) {
        tmp=message;
        message="";
      }
      float[] floatData = Array.ConvertAll(tmp.Split(' '), float.Parse); 
      Quaternion objOrientation=new Quaternion(-floatData[0],-floatData[1],floatData[2],floatData[3]);
      print("["+objOrientation.x+" "+objOrientation.y+" "+objOrientation.z+" "+objOrientation.w+"]");       
      transform.rotation=objOrientation;
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
    //GUI.Label(new Rect(Screen.width / 2f, Screen.height / 2f, Screen.width, Screen.height),myLog);
    GUILayout.Label(myLog);
  }
  
}
