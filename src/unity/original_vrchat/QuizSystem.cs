
using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRC.Udon;
using UnityEngine.UI;
using System;
using System.Collections.Generic;
using System.Reflection;



public class QuizSystem : UdonSharpBehaviour
{

    // Validators
    public int numberQuestion;
    public int currentQuestion;
    public int currentCorrect;
    public int currentIsCorrect;

    public int numberAlternatives = 4;


    /// <summary>
    /// question variables
    /// </summary>
    public string[] questions;
    public string[] answers0;
    public string[] answers1;
    public string[] answers2;
    public string[] answers3;
    public string[] answers4;
    /*
        public string[] answers5;
        public string[] answers6;
        public string[] answers7;
        public string[] answers8;
        public string[] answers9;
    */
    public int[] corrects;

    /// <summary>
    /// display
    /// </summary>
    public Image original;
    public Image originalA;
    public Image originalB;
    public Image originalC;
    public Image originalD;

    public Sprite AnswerWhite;
    public Sprite AnswerCorrect;
    public Sprite AnswerIncorrect;

    public Sprite quizMain;
    public Sprite quizQuestion;
    public Sprite quizCorrect;
    public Sprite quizIncorrect;
    public Sprite quizEnd;
    public Text questionText;
    public Text AnswerA;
    public Text AnswerB;
    public Text AnswerC;
    public Text AnswerD;
    public Text QuizAboutHandler;
    public String QuizAbout;


    /// <summary>
    /// results
    /// </summary>
    public int correctCount;
    public int wrongCount;
    public bool started = false;


    public void Start()
    {
        QuizAboutHandler.text = QuizAbout;
    }

    public void generateQuestion(int index)
    {
        questionText.text = "";
        if (index < 0)
        {
            resetValues();
            original.sprite = quizMain;
            QuizAboutHandler.text = QuizAbout;
            // set to the quiz start
        }
        else if (index >= questions.Length)
        {
            // set to the quiz end
            resetValues();
            original.sprite = quizEnd;
        }
        else
        {
            resetValues();
            original.sprite = quizQuestion;
            string[] questionAnswers = answersBuilder(index);
            AnswerA.text = questionAnswers[0];
            AnswerB.text = questionAnswers[1];
            AnswerC.text = questionAnswers[2];
            AnswerD.text = questionAnswers[3];
            questionText.text = questions[index];
            currentCorrect = corrects[index];
            QuizAboutHandler.text = "";


        }

    }
    public string[] answersBuilder(int index)
    {
        switch (index)
        {
            case 0:
                return answers0;
            case 1:
                return answers1;
            case 2:
                return answers2;
            case 3:
                return answers3;
            case 4:
                return answers4;
            /*           
                        case 5:
                            return answers5;
                        case 6:
                            return answers6;
                        case 7:
                            return answers7;
                        case 8:
                            return answers8;
                        case 9: 
                            return answers9;*/
            default:
                return answers0;


        }


    }

    public void ButtonA()
    {
        Answer(0);
    }
    public void ButtonB()
    {
        Answer(1);
    }
    public void ButtonC()
    {
        Answer(2);
    }
    public void ButtonD()
    {
        Answer(3);
    }

    public void ShowCorrect()
    {
        if (started == false)
        {
            return;
        }
        if (quizEnd.name == original.sprite.name)
        {
            return;
        }
        ResetQuestion();
        original.sprite = quizCorrect;
        SetCorrectIcon(currentCorrect);

    }
    public void Answer(int index)
    {
        if (started == false)
        {
            return;
        }
        if (quizEnd.name == original.sprite.name)
        {
            return;
        }

        if (index == currentCorrect)
        {

            currentIsCorrect += 1;
            original.sprite = quizCorrect;
            SetCorrectIcon(index);
        }
        else
        {
            SetInCorrectIcon(index);
            currentIsCorrect -= 1;
            original.sprite = quizIncorrect;
            SetInCorrectIcon(index);
        }
    }
    public void SetCorrectIcon(int index)
    {
        switch (index)
        {
            case 0:
                originalA.sprite = AnswerCorrect;
                break;
            case 1:
                originalB.sprite = AnswerCorrect;
                break;
            case 2:
                originalC.sprite = AnswerCorrect;
                break;
            case 3:
                originalD.sprite = AnswerCorrect;
                break;
            default:
                originalA.sprite = AnswerWhite;
                break;

        }
    }
    public void SetInCorrectIcon(int index)
    {
        switch (index)
        {
            case 0:
                originalA.sprite = AnswerIncorrect;
                break;
            case 1:
                originalB.sprite = AnswerIncorrect;
                break;
            case 2:
                originalC.sprite = AnswerIncorrect;
                break;
            case 3:
                originalD.sprite = AnswerIncorrect;
                break;
            default:
                originalA.sprite = AnswerIncorrect;
                break;

        }
    }
    public void StartQuiz()
    {
        started = true;
        original.sprite = quizQuestion;
        correctCount = 0;
        wrongCount = 0;
        currentQuestion = 0;
        QuizAboutHandler.text = "";
        resetValues();
        generateQuestion(0);
    }
    public void ResetQuiz()
    {
        started = false;
        original.sprite = quizMain;
        correctCount = 0;
        wrongCount = 0;
        currentQuestion = 0;
        QuizAboutHandler.text = QuizAbout;
        resetValues();

    }

    public void resetValues()
    {
        originalA.sprite = AnswerWhite;
        originalB.sprite = AnswerWhite;
        originalC.sprite = AnswerWhite;
        originalD.sprite = AnswerWhite;

        AnswerA.text = "";
        AnswerB.text = "";
        AnswerC.text = "";
        AnswerD.text = "";
        questionText.text = "";

    }
    public void ResetQuestion()
    {
        if (started == false)
        {
            return;
        }
        if (quizEnd.name == original.sprite.name)
        {
            return;
        }
        original.sprite = quizQuestion;
        originalA.sprite = AnswerWhite;
        originalB.sprite = AnswerWhite;
        originalC.sprite = AnswerWhite;
        originalD.sprite = AnswerWhite;
    }

    public void NextQuestion()
    {
        if (started == false)
        {
            return;
        }
        currentQuestion += 1;
        generateQuestion(currentQuestion);


    }
    public void BackQuestion()
    {
        if (started == false)
        {
            return;
        }

        currentQuestion -= 1;
        generateQuestion(currentQuestion);

    }
}
