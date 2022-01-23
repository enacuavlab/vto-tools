using Godot;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
	
public class Imu : Godot.Node
{
	private int receivePort = 5554;
	private Camera camera;
	private MeshInstance meshinstance;
	private CubeMesh cube;
	private UdpClient udpClient;
	private System.Threading.Thread receiveThread;
	private bool threadRunning = false;
	private string message = "";
	
	public override void _Ready()
	{
		cube = new CubeMesh();
		cube.Size = new Vector3(5,2,1);
		meshinstance = new MeshInstance();
		meshinstance.Mesh = cube;
		meshinstance.Translation = new Vector3(0,0,-10);
		AddChild(meshinstance);
		camera = new Camera();
		AddChild(camera);
		udpClient = new UdpClient(receivePort); 
		receiveThread = new System.Threading.Thread(() => ListenForMessages(udpClient));
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
			Quat objOrientation=new Quat(-floatData[0],-floatData[1],floatData[2],floatData[3]);
			GD.Print("["+objOrientation.x+" "+objOrientation.y+" "+objOrientation.z+" "+objOrientation.w+"]");  
			Basis basis = new Basis(objOrientation);
			//meshinstance.Transform.basis = basis;
		}
	}
	
	private void ListenForMessages(UdpClient client) {   
		IPEndPoint remoteIpEndPoint = new IPEndPoint(IPAddress.Any, 0);    
		while (threadRunning) {
			Byte[] receiveBytes = client.Receive(ref remoteIpEndPoint); // Blocking
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

