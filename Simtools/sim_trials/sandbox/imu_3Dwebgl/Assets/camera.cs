// The default started configuration containes 'Main Camera' and 'Directional Light'
// Create a GameObject / 3D Object / Cube
// Associate this file to the Cube

/*
./Imu.x86_64 5554 237.252.249.227
*/

using UnityEngine;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;


public class camera : MonoBehaviour
{
  private int receivePort = 5554;
  private UdpClient udpClient;
  private IPEndPoint remoteIpEndPoint;
  private IPAddress mcastAddr;
  private Thread receiveThread;
  private bool threadRunning = false;
  private string message = "";
    
  void Start() {
 
    string[] args = Environment.GetCommandLineArgs();  
    if(args.Length > 1) {
      receivePort=Convert.ToInt32(args[1].ToString(), 10);
      if(args.Length > 2) mcastAddr = IPAddress.Parse(args[2]);
    }
      
    transform.position=new Vector3(0.0f,1.0f,0.0f);
    
    Debug.Log("Start");
    try { 
       remoteIpEndPoint = new IPEndPoint(IPAddress.Any, receivePort);
       udpClient = new UdpClient(remoteIpEndPoint);
        if(args.Length > 2) udpClient.JoinMulticastGroup(mcastAddr);     
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
    
   private void ListenForMessages() {   
    while (threadRunning) {
      try {
        Byte[] receiveBytes = udpClient.Receive(ref remoteIpEndPoint); // Blocking
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
