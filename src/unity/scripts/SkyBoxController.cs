using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Simple script that rotates a skybox material. 
/// The material MUST have a Rotation property or guess what...that's right: it won't work.
/// </summary>
public class SkyboxController : MonoBehaviour
{
    [SerializeField] Material skyboxMaterial;
    [SerializeField] float rotateSpeed = 0.4f;

    int _rotationPropertyID;
    float _rotation;

    void Start()
    {
        if (skyboxMaterial == null)
            return;

        _rotationPropertyID = Shader.PropertyToID("_Rotation");
    }
    
    void Update()
    {
        if (skyboxMaterial == null)
            return;

        _rotation = Time.time * rotateSpeed;
        skyboxMaterial.SetFloat(_rotationPropertyID, _rotation);
    }
}
