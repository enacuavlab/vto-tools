// The default started configuration containes 'Main Camera' and 'Directional Light'
// Create a GameObject / 3D Object / Cube and name it 'Mycube'
// Associate this file to the Cube

/*
test.x86_64
test.x86_64 5559 
test.x86_64 5559 237.252.249.227
*/

using UnityEngine;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;
using System.Linq;

public class Mycube : MonoBehaviour
{
  private int receivePort = 5558;
  private UdpClient udpClient;
  private IPEndPoint remoteIpEndPoint;
  private IPAddress mcastAddr;
  private Thread receiveThread;
  private bool threadRunning = false;
  private string message = "";    
  private bool mcastBool = false;
      
  private static string[] GetArg() {
    return(System.Environment.GetCommandLineArgs());
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
    transform.localScale=new Vector3(5.0f,1.0f,10.0f);
    transform.position=new Vector3(0.0f,0.0f,10.0f);    
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
      Quaternion objOrientation=new Quaternion(floatData[4],-floatData[5],-floatData[6],floatData[7]);
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
