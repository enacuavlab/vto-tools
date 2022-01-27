    using System;
    using System.Collections.Generic;
    using UnityEngine;
    using UnityEngine.XR;
    internal static class ExampleUtil
    {
        public static bool isPresent()
        {
            var xrDisplaySubsystems = new List<XRDisplaySubsystem>();
            SubsystemManager.GetInstances<XRDisplaySubsystem>(xrDisplaySubsystems);
            foreach (var xrDisplay in xrDisplaySubsystems)
            {
                if (xrDisplay.running)
                {
                    return true;
                }
            }
            return false;
        }
    }

