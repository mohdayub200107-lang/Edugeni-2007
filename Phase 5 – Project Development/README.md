# EduGenie – Google Gemini Powered Learning Assistant

EduGenie is a lightweight AI-powered educational assistant. The project supports:

- Question and answer
- Simple concept explanations
- Quiz generation
- Paragraph summarization
- Personalized learning recommendations

The project follows the supplied EduGenie documentation: FastAPI backend, HTML + CSS frontend, Gemini 1.5 Pro for Q&A/summarization/quiz/learning paths, and a lightweight local explanation concept. The runnable version includes a local fallback so the application can be tested even before configuring a Gemini API key.

## Project Structure

```text
EduGenie/
├── main.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The source document specifies the above modular architecture and the endpoints `/qa`, `/explain`, `/quiz`, `/summarize`, and `/learn/recommendations`.

## Run in VS Code on Windows

### 1. Open the project

Extract the ZIP and open the `EduGenie_VSCode_Runnable` folder in VS Code.

### 2. Create virtual environment

```powershell
python -m venv venv
```

### 3. Activate

```powershell
.env\Scripts\Activate.ps1
```

### 4. Install packages

```powershell
pip install -r requirements.txt
```

### 5. Configure Gemini

Copy `.env.example` to `.env` and add your Google Gemini API key:

```text
GEMINI_API_KEY=your_key_here
```

Do not upload `.env` to GitHub.

### 6. Run

```powershell
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Available Features

### Ask a Question
Example:
```text
Which is the largest ocean?
```

### Explain a Topic
Example:
```text
Quantum computing
```

### Summarize
Paste a long educational paragraph.

### Generate Quiz
Example:
```text
Pythagoras theorem
```

The application generates three MCQs with four options and supports answer checking.

### Learning Recommendations
Example:
```text
SQL
```

The application produces a structured beginner-to-advanced learning path with learning guidance.

## API Endpoints

- `GET /` – Web interface
- `GET /qa?question=...` – Question answering
- `POST /explain` – Concept explanation
- `POST /summarize` – Text summarization
- `POST /quiz` – Quiz generation
- `GET /learn/recommendations?topic=...` – Learning recommendations
- `POST /action` – Frontend task router
- `GET /health` – Health check
- `GET /docs` – FastAPI Swagger UI

## Demo Mode

If no `GEMINI_API_KEY` is configured, EduGenie still runs using local demonstration responses. This allows you to test the complete frontend/backend workflow first.

## GitHub Upload

Upload the project source files, but do NOT upload:

- `.env`
- `venv/`
- API keys or passwords

## Source Basis

This project is based on the supplied EduGenie project document. The document describes EduGenie as a FastAPI + HTML/CSS educational assistant with Q&A, explanations, quizzes, summaries and personalized learning recommendations. It specifies Gemini 1.5 Pro for Q&A, summarization, quiz generation and learning paths, and lists the modular project architecture.
