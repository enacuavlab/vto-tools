using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// GameObject.FixedUpdate example.
//
// Measure frame rate comparing FixedUpdate against Update.
// Show the rates every second.

public class ExampleScript : MonoBehaviour
{
    private float updateCount = 0;
    private float fixedUpdateCount = 0;
    private float updateUpdateCountPerSecond;
    private float updateFixedUpdateCountPerSecond;

  private GameObject source1,sink1;
  private void buildArena() {
    GameObject cube1 = GameObject.CreatePrimitive(PrimitiveType.Cube);
    cube1.transform.localScale = new Vector3(0.5f,1.5f,0.5f);
    cube1.transform.position = new Vector3(4.5f, 0.0f, 6.0f);
    source1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    source1.transform.localScale = new Vector3(0.5f,0.01f,0.5f);
    source1.transform.position = new Vector3(4.5f,0.0f,2.0f);
    sink1 = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
    sink1.transform.localScale = new Vector3(0.5f,0.01f,0.5f);
    sink1.transform.position = new Vector3(4.5f,0.0f,9.5f);
  }   
    
    void Awake()
    {
      buildArena();
        // Uncommenting this will cause framerate to drop to 10 frames per second.
        // This will mean that FixedUpdate is called more often than Update.
        //Application.targetFrameRate = 10;
        StartCoroutine(Loop());
    }

    // Increase the number of calls to Update.
    void Update()
    {
        updateCount += 1;
    }

    // Increase the number of calls to FixedUpdate.
    void FixedUpdate()
    {
        fixedUpdateCount += 1;
    }

    // Show the number of calls to both messages.
    void OnGUI()
    {
        GUIStyle fontSize = new GUIStyle(GUI.skin.GetStyle("label"));
        fontSize.fontSize = 24;
        GUI.Label(new Rect(100, 100, 200, 50), "Update: " + updateUpdateCountPerSecond.ToString(), fontSize);
        GUI.Label(new Rect(100, 150, 200, 50), "FixedUpdate: " + updateFixedUpdateCountPerSecond.ToString(), fontSize);
        
        Debug.Log(updateUpdateCountPerSecond.ToString()+" "+updateFixedUpdateCountPerSecond.ToString());
    }

    // Update both CountsPerSecond values every second.
    IEnumerator Loop()
    {
        while (true)
        {
            yield return new WaitForSeconds(1);
            updateUpdateCountPerSecond = updateCount;
            updateFixedUpdateCountPerSecond = fixedUpdateCount;

            updateCount = 0;
            fixedUpdateCount = 0;
        }
    }
}
