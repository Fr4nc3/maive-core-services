
using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;

public class PlayerTraveler : UdonSharpBehaviour
{
    [SerializeField] Transform targetPosition;

    public override void Interact()
    {
        Networking.LocalPlayer.TeleportTo(targetPosition.position,
                                          targetPosition.rotation,
                                          VRC_SceneDescriptor.SpawnOrientation.Default,
                                          false);
    }
}
