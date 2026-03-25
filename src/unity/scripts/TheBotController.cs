using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TheBotController : MonoBehaviour
{
    Animator _animatorController;
    System.Random _random;
    private void Start()
    {
        _animatorController = GetComponent<Animator>();
        _random = new System.Random();
        BotUIController.Instance.OnJokeDelivery += Instance_OnJokeDelivery;
    }

    private void Instance_OnJokeDelivery()
    {        
        int randomInt = _random.Next(0, 2);

        if (randomInt == 0)
            _animatorController.SetTrigger("TellJoke");
        else
            _animatorController.SetTrigger("TellJokeAlt");
    }

    private void OnDestroy()
    {
        BotUIController.Instance.OnJokeDelivery -= Instance_OnJokeDelivery;
    }
