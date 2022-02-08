using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using NativeWebSocket;

public class Cube : MonoBehaviour
{
  WebSocket websocket;

  string myLog="";
  List<string> items = new List<string>();
  private int nLogs=10;
        
  private int angle=0;
  
  async void Start()
  {
    transform.position=new Vector3(0.0f,0.0f,10.0f);
    
    Debug.Log("Log1");

    // websocket = new WebSocket("ws://echo.websocket.org");
    websocket = new WebSocket("ws://localhost:8080");

    websocket.OnOpen += () =>
    {
      Debug.Log("Connection open!");
    };

    websocket.OnError += (e) =>
    {
      Debug.Log("Error! " + e);
    };

    websocket.OnClose += (e) =>
    {
      Debug.Log("Connection closed!");
    };

    websocket.OnMessage += (bytes) =>
    {
      // Reading a plain text message
      var message = System.Text.Encoding.UTF8.GetString(bytes);
      Debug.Log("Received OnMessage! (" + bytes.Length + " bytes) " + message);
    };

    // Keep sending messages at every 0.3s
    InvokeRepeating("SendWebSocketMessage", 0.0f, 0.3f);

    await websocket.Connect();
  }

  void Update()
  {
     transform.rotation = Quaternion.Euler(new Vector3(angle,angle,0));
     angle=angle+1;
    #if !UNITY_WEBGL || UNITY_EDITOR
      websocket.DispatchMessageQueue();
    #endif
  }

  async void SendWebSocketMessage()
  {
    if (websocket.State == WebSocketState.Open)
    {
      // Sending bytes
      await websocket.Send(new byte[] { 10, 20, 30 });

      // Sending plain text
      await websocket.SendText("plain text message");
    }
  }

  private async void OnApplicationQuit()
  {
    await websocket.Close();
  }
 
  void OnEnable () {
    Application.logMessageReceived += HandleLog;
  }
     
  void OnDisable () {
    Application.logMessageReceived -= HandleLog;
  }
 
  void HandleLog(string logString, string stackTrace, LogType type){
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
