// The default started configuration is empty
// Create a Node
// Associate this file to the Node

/*
./Imu.x86_64 5554 237.252.249.227
*/

using Godot;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
	
public class Node : Godot.Node
{
	private int receivePort = 5554;
	private UdpClient udpClient;
	private IPEndPoint remoteIpEndPoint;
	private IPAddress mcastAddr;
	private Camera camera;
	private MeshInstance meshinstance;
	private CubeMesh cube;
	private System.Threading.Thread receiveThread;
	private bool threadRunning = false;
	private string message = "";
	
	public override void _Ready()
	{
		string[] args = System.Environment.GetCommandLineArgs();  
		if(args.Length > 1) {
	  		receivePort=Convert.ToInt32(args[1].ToString(), 10);
	  		if(args.Length > 2) mcastAddr = IPAddress.Parse(args[2]);
		}
	
		cube = new CubeMesh();
		cube.Size = new Vector3(5,1,10);
		meshinstance = new MeshInstance();
		meshinstance.Mesh = cube;
		meshinstance.Translation = new Vector3(0,0,-20);
		AddChild(meshinstance);
		camera = new Camera();
		camera.Translation = new Vector3(0,1,0);
		AddChild(camera);
		
		remoteIpEndPoint = new IPEndPoint(IPAddress.Any, receivePort);
		udpClient = new UdpClient(remoteIpEndPoint);
		if(args.Length > 2) udpClient.JoinMulticastGroup(mcastAddr); 
	
		receiveThread = new System.Threading.Thread(() => ListenForMessages());
		receiveThread.IsBackground = true;
		threadRunning = true;
		receiveThread.Start();
	}

	public override void _Process(float delta)
	{
		string tmp="";
		if (message!="") {
			lock (message) {
				tmp=message;
				message="";
			}
			float[] floatData = Array.ConvertAll(tmp.Split(' '), float.Parse); 
			Quat objOrientation=new Quat(floatData[0],floatData[1],floatData[2],floatData[3]);
			//GD.Print("["+objOrientation.x+" "+objOrientation.y+" "+objOrientation.z+" "+objOrientation.w+"]");  
			Transform t = meshinstance.Transform;
			t.basis = new Basis(objOrientation);
			meshinstance.Transform = t;
		}
	}
	
	private void ListenForMessages() {   
		while (threadRunning) {
			Byte[] receiveBytes = udpClient.Receive(ref remoteIpEndPoint); // Blocking
			string returnData = Encoding.UTF8.GetString(receiveBytes);
			lock (message) {
		 		string [] lines = returnData.Split('\n');
				if (lines.Length > 1) returnData=lines[lines.Length-2]; // Keep last line
				message=returnData;
			}
			System.Threading.Thread.Sleep(1);    
		}
	}
}
