using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class rotate : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    public float rotateSpeed = 50f;
    void Update()
    {
        transform.Rotate(Vector3.up * Time.deltaTime * rotateSpeed);
    }
}
