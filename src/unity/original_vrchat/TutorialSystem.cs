
using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;
using UnityEngine.UI;


public class TutorialSystem : UdonSharpBehaviour
{
    public Image original;
    public Sprite[] ImageToActives;

    public void Start()
    {

    }

    public void TutorialImageNext()
    {
        Debug.Log("enter image next");
        Debug.Log(original.sprite.name);
        int index = 0;
        for (int i = 0; i < ImageToActives.Length; i++)
        {
            if (ImageToActives[i].name == original.sprite.name)
            {
                index = i; break;
            }
        }
        index += 1;

        if (index < ImageToActives.Length)
        {
            original.sprite = ImageToActives[index];
        }

    }
    public void TutorialImageBack()
    {
        Debug.Log("enter image back");
        Debug.Log(original.sprite.name);
        int index = 0;
        for (int i = 0; i < ImageToActives.Length; i++)
        {
            if (ImageToActives[i].name == original.sprite.name)
            {
                index = i; break;
            }
        }
        index -= 1;
        Debug.Log(index);

        if (index >= 0)
        {
            original.sprite = ImageToActives[index];
        }
    }
    public void TutorialImageOrigin()
    {

        original.sprite = ImageToActives[0];

    }
}
