
using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;

public class QuestionMark : UdonSharpBehaviour
{
    private void Update()
    {
        transform.Rotate(Vector3.up, 90f * Time.deltaTime);
    }
}
