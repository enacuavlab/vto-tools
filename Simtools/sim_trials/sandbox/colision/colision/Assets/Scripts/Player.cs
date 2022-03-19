using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{
  private float movespeed = 20;
  private float rotatespeed = 50;
  
  void Start() {
  }
    
  void Update() {
    transform.Translate(0,0,Input.GetAxis("Vertical")*Time.deltaTime*movespeed);
    transform.Rotate(0,Input.GetAxis("Horizontal")*Time.deltaTime*rotatespeed,0);
  }
}
