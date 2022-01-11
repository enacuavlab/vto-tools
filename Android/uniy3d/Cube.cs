using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class CubeScript : MonoBehaviour
{
  private int receivePort = 5555;
  private UdpClient udpClient;
  private Thread receiveThread;
  private bool threadRunning = false;
  private string message = "";
    
  void Start() {
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
      tmp=message;
      message="";
      print("value is "+tmp);
      float[] floatData = Array.ConvertAll(tmp.Split(','), float.Parse);
      print("["+floatData[0]+" "+floatData[1]+" "+floatData[2]+"]");
      transform.Rotate(floatData[0],floatData[1],floatData[2], Space.World);
    }
  }
  
  private void ListenForMessages(UdpClient client) {   
    IPEndPoint remoteIpEndPoint = new IPEndPoint(IPAddress.Any, 0);
    while (threadRunning) {
      try {
        Byte[] receiveBytes = client.Receive(ref remoteIpEndPoint); // Blocking
        string returnData = Encoding.UTF8.GetString(receiveBytes);
        lock (message) {
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
