using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class Cube : MonoBehaviour
{
  private int receivePort = 5554;
  private UdpClient udpClient;
  private Thread receiveThread;
  private bool threadRunning = false;
  private string message = "";
  
  private Rect GraphRect1,GraphRect2;
  private float xSize;
  private float ySize;
  private float xPos;
  private float yPos;
    
  void Start() {

    xSize = 0.9f * Screen.width;
    ySize = 0.1f * Screen.height;
    xPos = 0.05f * Screen.width;
    yPos = 0.0f * Screen.height;
    GraphRect1 = new Rect(xPos, yPos, xSize, ySize);
    GraphRect2 = new Rect(xPos, Screen.height-100.0f, xSize, ySize);
            
    transform.localScale=new Vector3(5.0f,1.0f,10.0f);
    transform.position=new Vector3(0.0f,0.0f,10.0f);
    
    Debug.Log("Start");
    try { 
      udpClient = new UdpClient(receivePort); 
    } catch (Exception e) {
      Debug.Log("Failed to listen for UDP at port " + receivePort + ": " + e.Message);
      return;
    }
    receiveThread = new Thread(() => ListenForMessages(udpClient));
    receiveThread.IsBackground = true;
    threadRunning = true;
    receiveThread.Start();
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

      //GraphManager.Graph.Plot("Test_WorldSpace", objOrientation.x, Color.green, new GraphManager.Matrix4x4Wrapper(transform.position, transform.rotation, transform.localScale));
      GraphManager.Graph.Plot("Test_ScreenSpace1", objOrientation.x, Color.green, GraphRect1);
      //GraphManager.Graph.Plot("Test_ScreenSpace1", objOrientation.x, Color.green, GraphRect2);
      //GraphManager.Graph.Plot("Test_ScreenSpace", objOrientation.y, Color.green, GraphRect1);
    }
  }
    
   private void ListenForMessages(UdpClient client) {   
    IPEndPoint remoteIpEndPoint = new IPEndPoint(IPAddress.Any, 0);
    while (threadRunning) {
      try {
        Byte[] receiveBytes = client.Receive(ref remoteIpEndPoint); // Blocking
        string returnData = Encoding.UTF8.GetString(receiveBytes);
        lock (message) {
          string [] lines = returnData.Split('\n');
          if (lines.Length > 1) returnData=lines[lines.Length-2]; // Keep last line
          message=returnData;
          //Debug.Log(returnData);
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
}
