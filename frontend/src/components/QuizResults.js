'use client';

export default function QuizResults({ results, onRestart }) {
  // Safety check: if results are not yet available, show a loading/error message.
  if (!results) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-xl text-center">
        <h2 className="text-2xl font-bold text-gray-800">Calculating...</h2>
      </div>
    );
  }

  const scorePercentage = Math.round((results.score / results.total) * 100);

  const getScoreMessage = () => {
    if (scorePercentage === 100) return "Perfect Score!";
    if (scorePercentage >= 70) return "Great Job!";
    if (scorePercentage >= 50) return "Good Effort!";
    return "Keep Practicing!";
  };

  return (
    <div className="bg-white p-6 sm:p-8 rounded-2xl shadow-2xl w-full max-w-4xl mx-auto animate-fade-in">
      <div className="text-center">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-800">Quiz Complete!</h1>
        <div className="my-4">
          <p className="text-6xl font-bold text-yellow-500">{scorePercentage}%</p>
          <p className="text-lg text-gray-600 mt-2">{getScoreMessage()}</p>
        </div>
        <p className="text-gray-700 text-base sm:text-lg">
          You answered {results.score} out of {results.total} questions correctly.
        </p>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-semibold text-gray-800 border-b-2 pb-2 mb-4">Review Your Answers</h2>
        <div className="space-y-4">
          {results.results.map((result) => (
            <div 
              key={result.question_id} 
              className={`p-4 rounded-lg shadow-md ${result.is_correct ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'} border-l-4`}
            >
              {/* --- FIX #1: Using question_text directly from the result object --- */}
              <p className="font-semibold text-gray-800 mb-2">{result.question_text}</p>
              <p className="text-sm text-gray-700">
                Your answer: <span className="font-medium">{result.user_answer_text}</span>
              </p>
              {!result.is_correct && (
                <p className="text-sm text-green-700 mt-1">
                  Correct answer: <span className="font-medium">{result.correct_answer_text}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
      
      <div className="text-center mt-8">
        <button
          onClick={onRestart}
          className="bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 transition-transform transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

