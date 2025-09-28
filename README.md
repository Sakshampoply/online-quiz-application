# Online Quiz Application 🧠

A modern, full-stack quiz application built with **Next.js** frontend and **FastAPI** backend. Test your knowledge with interactive quizzes, real-time scoring, and comprehensive analytics.

![Quiz Application](https://img.shields.io/badge/Status-Active-brightgreen)
![Frontend](https://img.shields.io/badge/Frontend-Next.js%2015-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Tests](https://img.shields.io/badge/Tests-41%20Passing-success)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange)

## 🌟 Features

### Core Functionality

- **Interactive Quiz Interface** - Clean, responsive UI for taking quizzes
- **Real-time Timer** - Countdown timer with auto-submission
- **Multiple Choice Questions** - Support for various question types
- **Instant Results** - Detailed scoring and answer analysis
- **Progress Tracking** - Navigate between questions with progress indication

### Technical Features

- **RESTful API** - Well-documented FastAPI backend
- **Database Management** - SQLAlchemy ORM with SQLite
- **Data Validation** - Pydantic schemas for type safety
- **Comprehensive Testing** - 41 automated tests covering all functionality
- **Code Quality** - ESLint for frontend, Flake8 for backend
- **CI/CD Pipeline** - Automated testing and deployment checks

## 🏗️ Tech Stack

### Frontend

- **Framework**: Next.js 15 (React 19)
- **Styling**: Tailwind CSS 4
- **Language**: JavaScript (ES2023)
- **Linting**: ESLint with Next.js config

### Backend

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **Language**: Python 3.9+
- **Testing**: pytest with 41+ test cases
- **Linting**: Flake8 (PEP8 compliance)

### DevOps & Tooling

- **CI/CD**: GitHub Actions
- **Testing**: Automated test suite with coverage reporting
- **Code Quality**: ESLint (frontend) + Flake8 (backend)
- **Environment**: Virtual environments (venv)

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (recommended: 3.11)
- **Node.js 18+** and npm
- **Git** for cloning the repository

### 1. Clone Repository

```bash
git clone https://github.com/Sakshampoply/online-quiz-application.git
cd online-quiz-application
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install fastapi[all] sqlalchemy pydantic pytest httpx

# Run database setup (creates tables and seeds data)
python -c "from seed import seed_database; from database import SessionLocal; seed_database(SessionLocal())"
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Install additional packages if needed
npm ci
```

### 4. Start Development Servers

**Backend Server** (Terminal 1):

```bash
cd backend
source .venv/bin/activate

# Run from project root to avoid import issues
cd ..
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Server** (Terminal 2):

```bash
cd frontend
npm run dev
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)

## 🧪 Testing

### Frontend Testing

```bash
cd frontend

# Run ESLint
npm run lint

# Fix linting issues
npm run lint:fix
```

### Backend Testing

```bash
cd backend
source .venv/bin/activate

# Run all tests (41 test cases)
python -m pytest tests/ -v

# Run specific test files
python run_tests.py unit      # Core functionality tests
python run_tests.py api       # API integration tests
python run_tests.py edge      # Edge cases and error handling
python run_tests.py fast      # Quick run without verbose output

# Run linting
flake8 . --count --max-line-length=88 --statistics
```

### Test Coverage

- **Total Tests**: 41 test cases
- **Coverage Areas**: CRUD operations, API endpoints, edge cases, data validation
- **Test Types**: Unit tests, integration tests, API tests, performance tests

📚 **Detailed Testing Guide**: [backend/tests/README.md](backend/tests/README.md)

## 🏃‍♂️ Usage Guide

### Taking a Quiz

1. **Start**: Click "Start Quiz" on the homepage
2. **Answer**: Select answers for each multiple-choice question
3. **Navigate**: Use Previous/Next buttons to review answers
4. **Submit**: Click "Submit Quiz" or wait for auto-submission
5. **Results**: View detailed results with correct answers highlighted

### API Endpoints

| Method | Endpoint      | Description                         |
| ------ | ------------- | ----------------------------------- |
| `GET`  | `/`           | Welcome message                     |
| `GET`  | `/questions/` | Fetch all quiz questions            |
| `POST` | `/submit/`    | Submit quiz answers and get results |

**Example API Usage:**

```bash
# Get questions
curl http://localhost:8000/questions/

# Submit answers
curl -X POST http://localhost:8000/submit/ \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": 1, "choice_id": 2}]}'
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The project includes automated CI/CD pipeline that runs on every push:

#### Pipeline Jobs:

1. **Frontend Linting** - ESLint checks for code quality
2. **Backend Linting** - Flake8 checks for PEP8 compliance
3. **Backend Tests** - Complete test suite (41 tests)

#### Workflow Features:

- ✅ Runs on push to `main`/`master` branches
- ✅ Fail-fast approach (stops on first failure)
- ✅ Multi-Python version support (3.9, 3.10, 3.11)
- ✅ Automatic dependency caching
- ✅ Clear success/failure reporting

```bash
# Local validation (matches CI pipeline)
cd frontend && npm run lint          # Frontend linting
cd backend && flake8 . --statistics  # Backend linting
cd backend && python -m pytest tests/ -v  # Backend tests
```

## 📁 Project Structure

```
online-quiz-application/
├── 📁 frontend/                 # Next.js React application
│   ├── 📁 src/
│   │   ├── 📁 app/             # App router pages
│   │   └── 📁 components/      # React components
│   ├── 📄 package.json        # NPM dependencies
│   └── 📄 eslint.config.mjs   # ESLint configuration
├── 📁 backend/                 # FastAPI Python application
│   ├── 📄 main.py             # FastAPI app entry point
│   ├── 📄 models.py           # SQLAlchemy database models
│   ├── 📄 schemas.py          # Pydantic validation schemas
│   ├── 📄 crud.py             # Database operations
│   ├── 📄 database.py         # Database configuration
│   ├── 📄 seed.py             # Database seeding script
│   ├── 📁 tests/              # Test suite (41 tests)
│   │   ├── 📄 test_backend.py # Core functionality tests
│   │   ├── 📄 test_api.py     # API integration tests
│   │   ├── 📄 test_edge_cases.py # Edge cases and errors
│   │   └── 📄 README.md       # Testing documentation
│   └── 📄 run_tests.py        # Test runner script
├── 📁 .github/workflows/       # CI/CD pipeline
│   └── 📄 ci.yml              # GitHub Actions workflow
└── 📄 README.md               # This file
```

## 🛠️ Development

### Backend Development

```bash
cd backend
source .venv/bin/activate

# Install development dependencies
pip install black flake8 isort mypy

# Format code
black .
isort .

# Type checking
mypy . --ignore-missing-imports
```

### Frontend Development

```bash
cd frontend

# Development mode with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Adding New Features

#### Backend (Add API Endpoint):

1. **Model**: Add database model in `models.py`
2. **Schema**: Add Pydantic schema in `schemas.py`
3. **CRUD**: Add database operations in `crud.py`
4. **Endpoint**: Add API route in `main.py`
5. **Tests**: Add test cases in `tests/`

#### Frontend (Add Component):

1. **Component**: Create in `src/components/`
2. **Page**: Add to `src/app/` if needed
3. **Styling**: Use Tailwind CSS classes
4. **Integration**: Connect to backend API

## 🚀 Deployment

### Production Setup

```bash
# Backend production
cd backend
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app

# Frontend production
cd frontend
npm run build
npm start
```

### Environment Variables

Create `.env` files for production:

**Backend `.env`**:

```
DATABASE_URL=postgresql://user:pass@localhost/quiz_db
SECRET_KEY=your-secret-key
DEBUG=False
```

**Frontend `.env.local`**:

```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- ✅ Write tests for new features
- ✅ Follow existing code style (ESLint/Flake8)
- ✅ Update documentation as needed
- ✅ Ensure CI pipeline passes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework with great DX
- **SQLAlchemy** for robust database ORM
- **Tailwind CSS** for utility-first styling
- **pytest** for comprehensive testing framework

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/Sakshampoply/online-quiz-application/issues)
- 📚 **Documentation**: Check `/backend/tests/README.md` for testing details
- 🔗 **API Docs**: http://localhost:8000/docs (when server is running)

---

**Happy Coding!** 🎉 If you find this project helpful, please consider giving it a ⭐ on GitHub!
