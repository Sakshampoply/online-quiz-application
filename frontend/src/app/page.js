'use client';

import { useState, useEffect } from 'react';
import QuizStart from '../components/QuizStart';
import QuizView from '../components/QuizView';
import QuizResults from '../components/QuizResults';

const initialState = {
  quizState: 'not_started',
  currentQuestionIndex: 0,
  userAnswers: {},
  results: null,
  timeLeft: 120, // 2-minute timer for the whole quiz
};

export default function Home() {
  const [questions, setQuestions] = useState([]);
  const [quizState, setQuizState] = useState(initialState.quizState);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(initialState.currentQuestionIndex);
  const [userAnswers, setUserAnswers] = useState(initialState.userAnswers);
  const [results, setResults] = useState(initialState.results);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeLeft, setTimeLeft] = useState(initialState.timeLeft);
  const [fetchTrigger, setFetchTrigger] = useState(0); // New state to trigger fetch

  // Centralized data fetching logic
  useEffect(() => {
    const fetchQuestions = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/questions/');
        if (!response.ok) {
          throw new Error('Failed to fetch questions. Is the backend running?');
        }
        const data = await response.json();
        
        // --- FIX 1: Handle empty response from the API ---
        // This provides a helpful error if the database isn't seeded.
        if (!data || data.length === 0) {
            throw new Error('No questions found. Please run the backend seeder script.');
        }
        setQuestions(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuestions();
  }, [fetchTrigger]); // Re-runs whenever fetchTrigger changes

  // Global Timer Logic
  useEffect(() => {
    if (quizState !== 'in_progress' || timeLeft === 0) return;

    const timerId = setInterval(() => {
      setTimeLeft((prevTime) => prevTime - 1);
    }, 1000);
    
    // Auto-submit when timer reaches zero
    if (timeLeft === 1) { // Check for 1 to trigger on the next render cycle at 0
        setTimeout(() => handleSubmitQuiz(), 1000);
    }

    return () => clearInterval(timerId);
  }, [quizState, timeLeft]);

  const handleStartQuiz = () => {
    setTimeLeft(initialState.timeLeft);
    setQuizState('in_progress');
  };

  const handleAnswerSelect = (choiceId) => {
    const questionId = questions[currentQuestionIndex].id;
    setUserAnswers({ ...userAnswers, [questionId]: choiceId });
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    if (quizState === 'calculating' || quizState === 'completed') return; // Prevent double submission
    setQuizState('calculating');
    const answersPayload = {
      answers: Object.entries(userAnswers).map(([qId, cId]) => ({
        question_id: parseInt(qId, 10),
        choice_id: cId,
      })),
    };

    try {
      const response = await fetch('http://localhost:8000/submit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(answersPayload),
      });
      if (!response.ok) throw new Error('Failed to submit answers.');
      const resultsData = await response.json();
      setResults(resultsData);
      setQuizState('completed');
    } catch (err) {
      setError(err.message);
    }
  };
  
  // --- FIX 2: More robust restart logic ---
  const handleRestartQuiz = () => {
    // Reset all state
    setQuizState(initialState.quizState);
    setCurrentQuestionIndex(initialState.currentQuestionIndex);
    setUserAnswers(initialState.userAnswers);
    setResults(initialState.results);
    // Trigger the useEffect to refetch questions
    setFetchTrigger(c => c + 1);
  };

  const renderContent = () => {
    if (isLoading) {
      return <p className="text-center text-2xl font-semibold">Loading Quiz...</p>;
    }
    if (error) {
      return <p className="text-center text-red-500 text-xl p-8 bg-white rounded-lg shadow-md">Error: {error}</p>;
    }

    switch (quizState) {
      case 'not_started':
        return <QuizStart onStartQuiz={handleStartQuiz} />;
      case 'in_progress':
        const currentQuestion = questions[currentQuestionIndex];
        if (!currentQuestion) {
            // This now shows while the refetch on restart happens
            return <p className="text-center text-2xl font-semibold">Preparing Questions...</p>;
        }
        return (
          <QuizView
            question={currentQuestion}
            questionNumber={currentQuestionIndex + 1}
            totalQuestions={questions.length}
            selectedAnswer={userAnswers[currentQuestion.id] || null}
            onAnswerSelect={handleAnswerSelect}
            onNext={handleNextQuestion}
            onPrevious={handlePreviousQuestion}
            onSubmit={handleSubmitQuiz}
            isLastQuestion={currentQuestionIndex === questions.length - 1}
            timeLeft={timeLeft}
          />
        );
      case 'calculating':
        return <p className="text-center text-2xl font-semibold">Calculating your score...</p>;
      case 'completed':
        return <QuizResults results={results} onRestart={handleRestartQuiz} />;
      default:
        return null;
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 md:p-24 bg-gray-100">
      <div className="w-full max-w-2xl mx-auto">
        {renderContent()}
      </div>
    </main>
  );
}

