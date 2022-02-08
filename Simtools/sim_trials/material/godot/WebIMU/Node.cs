using Godot;
using System;
using System.Net.WebSockets;

public class Node : Godot.Node
{
	private WebSocket ws;
	
	private Camera camera;
	private MeshInstance meshinstance;
	private CubeMesh cube;
	
	private float angle=0;
	
	public override void _Ready()
	{        
		cube = new CubeMesh();
		cube.Size = new Vector3(5,1,10);
		meshinstance = new MeshInstance();
		meshinstance.Mesh = cube;
		meshinstance.Translation = new Vector3(0,0,-20);
		AddChild(meshinstance);
		camera = new Camera();
		camera.Translation = new Vector3(0,1,0);
		AddChild(camera);
		
		ws = new WebSocket("ws://localhost:8080");
		ws.Connect();
		ws.OnMessage += (sender, e) =>
		{
			Debug.Log("Message Received from "+((WebSocket)sender).Url+", Data : "+e.Data);
		};
	}

	public override void _Process(float delta)
	{
		angle=angle+0.1f;
		Quat objOrientation=new Quat(new Vector3(0,angle,0));
		Transform t = meshinstance.Transform;
		t.basis = new Basis(objOrientation);
		meshinstance.Transform = t;     
	}
}
