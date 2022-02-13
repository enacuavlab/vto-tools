using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace XP
{
  [RequireComponent(typeof(BoxCollider))]
  public class XP_Drone_Engine : MonoBehaviour, IEngine
  {
    #region Variables
    [Header("Engine Properties")]
    [SerializeField] private float maxPower = 4f;
    
    [Header("Propeller Properties")]
    [SerializeField] private Transform propeller;
    [SerializeField] private float propRotSpeed = 300f;
    #endregion
    
    #region Interface Methods
    public void InitEngine() {
      throw new System.NotImplementedException();
    }
    public void UpdateEngine(Rigidbody rb, XP_Drone_Inputs input) {
      Vector3 upVec = transform.up;
      upVec.x = 0f;
      upVec.z = 0f;
      float diff = 1 - upVec.magnitude;
      float finalDiff = Physics.gravity.magnitude * diff;
            
      Vector3 engineForce = Vector3.zero;
      
      //engineForce = transform.up * ((rb.mass * Physics.gravity.magnitude) + (input.Throttle * maxPower))/4f;
      
      // auto hover : additional force to compensate inclination
      engineForce = transform.up * ((rb.mass * Physics.gravity.magnitude + finalDiff) + (input.Throttle * maxPower))/4f;

      rb.AddForce(engineForce,ForceMode.Force);   
            
      HandlePropellers();
    }
    
    void HandlePropellers() 
    {
      if(!propeller) {
        return;
      }
      
      propeller.Rotate(Vector3.up, propRotSpeed);      
    }
    
    #endregion
    
  }
}
