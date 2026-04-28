
using UdonSharp;
using UnityEditor;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;

public class PlanetSpin : UdonSharpBehaviour
{
    Vector3 movement;
    public float x, y, z;
    public void Start()
    {
        movement = new Vector3(x, y, z);
    }
    public void Update()
    {
        transform.Rotate(movement * Time.deltaTime);
    }
}
