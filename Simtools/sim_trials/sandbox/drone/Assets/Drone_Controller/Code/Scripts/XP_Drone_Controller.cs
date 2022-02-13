using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

namespace XP
{
  [RequireComponent(typeof(XP_Drone_Inputs))]
  public class XP_Drone_Controller : XP_Base_Rigidbody
  {
    #region Variables
    [Header("Control Properties")]
    [SerializeField] private float minMaxPitch = 30f;
    [SerializeField] private float minMaxRoll = 30f;
    [SerializeField] private float yawPower = 4f;
    [SerializeField] private float lerpSpeed = 2f;
    private XP_Drone_Inputs input;
    private List<IEngine> engines = new List<IEngine>();
    
    private float finalPitch;
    private float finalRoll;
    private float yaw;
    private float finalYaw;
    #endregion
    
    #region Main Methods
    void Start()
    {
      input = GetComponent<XP_Drone_Inputs>();
      engines = GetComponentsInChildren<IEngine>().ToList<IEngine>();
    }

    #endregion
    
    #region Custom Methods
    protected override void HandlePhysics()
    {
      //HandleEngines();
      //HandleControls();
      HandleXP();
    }
    
    protected virtual void HandleEngines()
    {
      //rb.AddForce(Vector3.up * (rb.mass * Physics.gravity.magnitude));
      foreach(IEngine engine in engines) {
        engine.UpdateEngine(rb,input);
      }
    }
    
    protected virtual void HandleControls()
    {
       float pitch = input.Cyclic.y * minMaxPitch;
       float roll = input.Cyclic.x * minMaxRoll;
       yaw += input.Pedals * yawPower;

       finalPitch = Mathf.Lerp(finalPitch, pitch, Time.deltaTime * lerpSpeed);
       finalRoll = Mathf.Lerp(finalRoll, roll, Time.deltaTime * lerpSpeed);
       finalYaw = Mathf.Lerp(finalYaw, yaw, Time.deltaTime * lerpSpeed);
                     
       Quaternion rot = Quaternion.Euler(finalPitch,finalYaw,finalRoll);
       rb.MoveRotation(rot);    
    }
    
    protected virtual void HandleXP()
    {
       float pitch = input.Cyclic.y * minMaxPitch;
       float roll = input.Cyclic.x * minMaxRoll;
       yaw += input.Pedals * yawPower;

       finalPitch = Mathf.Lerp(finalPitch, pitch, Time.deltaTime * lerpSpeed);
       finalRoll = Mathf.Lerp(finalRoll, roll, Time.deltaTime * lerpSpeed);
       
       //Vector3 engineForce = new Vector3(0,((rb.mass * Physics.gravity.magnitude) + (input.Throttle * 4f)),0);
       Vector3 engineForce = Vector3.zero;
       engineForce = rb.transform.up * ((rb.mass * Physics.gravity.magnitude) + (input.Throttle * 4f));
       Debug.Log(engineForce);
       rb.AddForce(engineForce,ForceMode.Force);
       
       Quaternion rot = Quaternion.Euler(finalPitch,0f,finalRoll);
       rb.MoveRotation(rot);    
                     
       //Quaternion rot = Quaternion.AngleAxis(yaw,Vector3.up);
       //rb.transform.rotation = Quaternion.Slerp(transform.rotation, rot, 5f * Time.deltaTime);

    }
    #endregion    
  }
}
