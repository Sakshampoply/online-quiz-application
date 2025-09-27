/**
 * QuizStart Component
 * Displays the initial start screen for the quiz.
 * @param {object} props - The component props.
 * @param {function} props.onStartQuiz - Function to call when the start button is clicked.
 */
export default function QuizStart({ onStartQuiz }) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 bg-white rounded-xl shadow-2xl max-w-lg mx-auto">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">
        Welcome to the Quiz!
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Test your knowledge with our fun and challenging questions. Click the button below when you're ready to start.
      </p>
      <button
        onClick={onStartQuiz}
        className="bg-blue-600 text-white font-bold py-3 px-8 rounded-lg text-xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 transition-transform transform hover:scale-105 duration-300 ease-in-out"
      >
        Start Quiz
      </button>
    </div>
  );
}
