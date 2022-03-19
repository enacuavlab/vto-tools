using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AvoidingFlyer : MonoBehaviour
{
  public float targetVelocity = 10.0f;
  public int numberOfRays = 17;
  public float angle = 90;
  public int rayRange = 8;

  void Start() {
  }
    
  void Update() {

    Vector3 deltaPosition=Vector3.zero;
    for (int i=0;i<numberOfRays;i++) {
      Vector3 direction=Quaternion.AngleAxis((i/(float)(numberOfRays-1))*2*angle-angle,transform.up)
	                *transform.TransformDirection(Vector3.forward);
      Ray ray = new Ray(transform.position,direction);
      RaycastHit hit;
      if(Physics.Raycast(ray,out hit,rayRange)) {
        Debug.DrawRay(transform.position, direction*hit.distance, Color.yellow);
        Debug.Log("Did Hit");
        deltaPosition-=(1.0f / numberOfRays)*targetVelocity*direction;
      } else {
        Debug.DrawRay(transform.position, transform.TransformDirection(Vector3.forward)*rayRange, Color.white);
        Debug.Log("Did not Hit");
        deltaPosition+=(1.0f / numberOfRays)*targetVelocity*direction;
      }
    }
    transform.position+=deltaPosition*Time.deltaTime;
  }

/*
  void OnDrawGizmos() {
    Gizmos.color = Color.red;
    for (int i=0;i<numberOfRays;i++) {
      Gizmos.DrawRay(transform.position,
        Quaternion.AngleAxis((i/(float)(numberOfRays-1))*2*angle-angle,transform.up)
	*transform.TransformDirection(Vector3.forward)*rayRange);
    }
  }
*/
}

/*
https://www.youtube.com/watch?v=SVazwHyfB7g
*/
