using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class rotate_axis : MonoBehaviour
{
    // Start is called before the first frame update
    public float rotateSpeed = 50f;
    public float axialTilt = 23.5f; // Tilt angle in degrees (Earth = 23.5)

    private Vector3 rotationAxis;
    void Start()
    {
        rotationAxis = Quaternion.Euler(0f, 0f, axialTilt) * Vector3.up; 
    }

    // Update is called once per frame
    void Update()
    {
        transform.Rotate(rotationAxis * Time.deltaTime * rotateSpeed);
    }
}
