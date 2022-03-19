using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class Enemy : MonoBehaviour
{
  private Transform player;
  private NavMeshAgent nav;
    
  void Start() {
    player = GameObject.FindGameObjectWithTag("Player").transform;
    nav = GetComponent<NavMeshAgent>();
  }
  
  void Update() {
    nav.SetDestination(player.position);
  }
  
}
