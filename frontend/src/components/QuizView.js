// This component no longer needs its own state or effects, so we can remove the import.

// This component no longer manages the timer. It just displays it.
export default function QuizView({
  question,
  questionNumber,
  totalQuestions,
  selectedAnswer,
  onAnswerSelect,
  onNext,
  onPrevious,
  onSubmit,
  isLastQuestion,
  timeLeft, // Receives the global time as a prop
}) {

  if (!question) {
    return <div>Loading question...</div>;
  }

  // --- Time Formatting ---
  // A helper function to format seconds into a M:SS display.
  const formatTime = (seconds) => {
    if (seconds === null || seconds < 0) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${String(remainingSeconds).padStart(2, '0')}`;
  };

  // --- Dynamic Styling for the Timer ---
  const timerColor = timeLeft <= 10 ? 'text-red-500' : 'text-gray-900';
  const timerAnimation = timeLeft <= 10 ? 'animate-pulse' : '';

  return (
    <div className="bg-white p-8 rounded-2xl shadow-xl w-full transition-all duration-300 ease-in-out transform hover:shadow-2xl">
      {/* Header with Question Number and the GLOBAL Timer */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-700">
          Question {questionNumber} of {totalQuestions}
        </h2>
        <div className={`text-2xl font-bold p-3 rounded-full bg-gray-100 ${timerColor} ${timerAnimation}`}>
          {formatTime(timeLeft)}
        </div>
      </div>

      {/* Question Text */}
      <h3 className="text-3xl font-bold mb-8 text-gray-900">{question.text}</h3>

      {/* Answer Choices */}
      <div className="space-y-4">
        {question.choices.map((choice) => {
          const isSelected = selectedAnswer === choice.id;
          const buttonClass = isSelected
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-800 hover:bg-gray-100 border-gray-300';

          return (
            <button
              key={choice.id}
              onClick={() => onAnswerSelect(choice.id)}
              className={`w-full text-left p-5 text-lg rounded-xl border-2 transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 ${buttonClass}`}
            >
              {choice.text}
            </button>
          );
        })}
      </div>

      {/* Navigation Buttons */}
      <div className="mt-10 flex justify-between items-center">
        <button
          onClick={onPrevious}
          disabled={questionNumber === 1}
          className="px-8 py-3 text-lg font-semibold rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>

        {isLastQuestion ? (
          <button
            onClick={onSubmit}
            className="px-8 py-3 text-lg font-semibold rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors shadow-md hover:shadow-lg"
          >
            Submit Quiz
          </button>
        ) : (
          <button
            onClick={onNext}
            className="px-8 py-3 text-lg font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
