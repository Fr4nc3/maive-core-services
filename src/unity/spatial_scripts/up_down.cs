using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class up_down : MonoBehaviour
{
    public float amplitude = 0.5f; // Height of the movement
    public float speed = 1f;      // Speed of the movement
    private Vector3 startPos;
    // Start is called before the first frame update
    void Start()
    {
        startPos = transform.position; // Store original position
    }

    // Update is called once per frame
    void Update()
    {
    // Calculate new Y position using a sine wave
        float newY = startPos.y + Mathf.Sin(Time.time * speed) * amplitude;
        transform.position = new Vector3(startPos.x, newY, startPos.z);   
    }
}
