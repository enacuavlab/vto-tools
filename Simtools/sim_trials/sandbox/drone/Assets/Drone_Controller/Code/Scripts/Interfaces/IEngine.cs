using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace XP
{
  public interface IEngine
  {
    void InitEngine();
    void UpdateEngine(Rigidbody rb, XP_Drone_Inputs input);    
  }  
}
