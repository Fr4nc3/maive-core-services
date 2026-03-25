using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BotUIController : MonoBehaviour
  public static BotUIController Instance { get; private set; }

    [SerializeField] GameObject dialogueContainer;
    [SerializeField] TextMeshProUGUI dialogueText;
    [SerializeField] Button creditsButton;
    [SerializeField] Button closeCreditsButton;
    [SerializeField] GameObject creditsContainer;

    // Four different WaitForSeconds objects. These are created as variables & re-used.
    readonly WaitForSeconds _jokePause = new WaitForSeconds(1f);
    readonly WaitForSeconds _characterPause = new WaitForSeconds(.025f);
    readonly WaitForSeconds _pauseForEffect = new WaitForSeconds(3.5f);
    readonly WaitForSeconds _interval = new WaitForSeconds(2f);

    /// <summary>
    /// Boolean variable that indicates whether The Hack is "speaking".
    /// </summary>
    bool _isSpeaking = false;
    
    /// <summary>
    /// Random object used to generate a random number.
    /// </summary>
    static System.Random random = new System.Random();

    /// <summary>
    /// A list of strings used to introduce the joke.
    /// </summary>
    readonly List<string> _introTexts = new()
    {
        "This next one is good.",
        "Please don't leave.",
        "You'll love this one.",
        "OK, check this out...",
        "Here's a good one.",
        "Don't stop me if you've heard this one.",
        "Have you heard this one?",
        "This next one is my favorite.",
        "This one's guaranteed to land.",
        "Perfect birthday party joke...",
        "Have you heard the one that goes...",
        "Your mom told me this one...",
        "This next one I found in the bathroom stall...",
        "My boss didn't appreciate this next one...",
        "So...anyway...",
        "Heh. Heh..."
    };

    /// <summary>
    /// Event executed when The Hack begins telling the joke.
    /// </summary>
    public event Action OnJokeDelivery;
    /// <summary>
    /// Event executed when The Hack has finished telling the joke.
    /// </summary>
    public event Action OnJokeDelivered;

    /// <summary>
    /// Singleton implementation
    /// </summary>
    private void Awake()
    {
        if (Instance != null && Instance != this)
            Destroy(this);
        else
            Instance = this;
    }

    void Start()
    {        
        // Setting the TextMeshPro element's visible characters to zero. This lets us do a neato
        // typewriter effect when displaying the text.
        dialogueText.maxVisibleCharacters = 0;

        // Subscribing (listening) to the DadJokeHandler's OnJokeReceived event
        DadJokeHandler.Instance.OnJokeReceived += Instance_OnJokeReceived;

        creditsButton.onClick.AddListener(ViewCredits);
        closeCreditsButton.onClick.AddListener(CloseCredits);
    }

    /// <summary>
    /// When the DadJokeHandler receives the joke from the Web Request, the joke telling process begins.
    /// </summary>
    /// <param name="obj"></param>
    private void Instance_OnJokeReceived(Joke obj)
    {            
        StartCoroutine(TellJoke(obj));
    } 
    
    private IEnumerator TellJoke(Joke joke)
    {
        // Retrieving a random number, which is used to select an intro text
        int index = random.Next(_introTexts.Count);

        // "Animate" the intro text
        StartCoroutine(DisplayText(_introTexts[index]));

        // Slight pause
        yield return _pauseForEffect;

        // "Animate" the joke text
        StartCoroutine(DisplayText(joke.joke, true));
    }

    /// <summary>
    /// Function used to display text in a TextMeshPro text element, in a typewriter-style animation.
    /// </summary>
    /// <param name="text">The text to display</param>
    /// <param name="isJoke">Whether this is the joke or just the intro text</param>
    /// <returns></returns>
    private IEnumerator DisplayText(string text, bool isJoke = false)
    {
        yield return _jokePause;

        // Set the TextMeshPro's text
        dialogueText.SetText(text);

        // Using LeanTween to animate the dialogue element into existence
        LeanTween.scale(dialogueContainer, Vector3.one, .25f).setEase(LeanTweenType.easeOutElastic);
        dialogueText.ForceMeshUpdate();

        // The Hack is speaking! You must listen!
        _isSpeaking = true;

        int totalCharacters = dialogueText.textInfo.characterCount;        
        int counter = 0;

        // If this is the intro text, fire off the OnJokeDelivery event
        if(!isJoke)
            OnJokeDelivery?.Invoke();

        // This does the "typewriter" style text animation
        // This code was adapted from Unity's TextMeshPro samples.
        while (_isSpeaking)
        {            
            int visibleCount = counter % (totalCharacters + 1); 
            dialogueText.maxVisibleCharacters = visibleCount; 

            if (visibleCount >= totalCharacters)
            {
                _isSpeaking = false;                
                yield return _interval;

                if(isJoke)
                    yield return _interval;

                LeanTween.scale(dialogueContainer, Vector3.zero, .25f).setEase(LeanTweenType.easeInElastic);
                if (isJoke)
                    OnJokeDelivered?.Invoke();

                yield break;
            }                

            counter += 1;
            
            yield return _characterPause;
        }        
    }

    /// <summary>
    /// Important to give credit where credit is due. This could have easily been done in the inspector by setting
    /// the game object active, but using C# we get to use LeanTween, which adds a nice effect.
    /// </summary>
    private void ViewCredits()
    {
        LeanTween.scale(creditsContainer, Vector3.one, .25f).setEase(LeanTweenType.easeOutElastic);
    }
    
    private void CloseCredits()
    {
        LeanTween.scale(creditsContainer, Vector3.zero, .25f).setEase(LeanTweenType.easeInElastic);
    }

    /// <summary>
    /// Be sure to unsubscribe to events that have been subscribed to.
    /// </summary>
    private void OnDestroy()
    {
        DadJokeHandler.Instance.OnJokeReceived -= Instance_OnJokeReceived;
        creditsButton.onClick.RemoveListener(ViewCredits);
        closeCreditsButton.onClick.RemoveListener(CloseCredits);
    }
}
