import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="EduGenie - Google Gemini Powered Learning Assistant",
    version="1.0.0",
    description="AI-powered educational assistant for Q&A, explanations, quizzes, summaries and learning paths."
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")


def gemini_generate(prompt: str) -> str:
    """Call Gemini when configured; otherwise return a local demo response."""
    if not GEMINI_API_KEY:
        return demo_response(prompt)

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = getattr(response, "text", None)
        if text:
            return text.strip()
        return "No response was returned by Gemini."
    except Exception as exc:
        return f"Gemini is unavailable right now. Demo response: {demo_response(prompt)}"


def demo_response(prompt: str) -> str:
    """Offline fallback so the complete project can be tested without an API key."""
    lower = prompt.lower()

    if "largest ocean" in lower:
        return "The Pacific Ocean is the largest ocean on Earth."

    if "explain" in lower:
        topic = prompt.split(":", 1)[-1].strip()
        return (
            f"{topic} is explained in simple terms as follows:\n\n"
            f"This is a demo explanation generated locally by EduGenie. "
            f"Add a Gemini API key in .env to receive AI-generated explanations."
        )

    if "summarize" in lower:
        text = prompt.split(":", 1)[-1].strip()
        words = text.split()
        short = " ".join(words[:45])
        return short + ("..." if len(words) > 45 else "")

    if "learning path" in lower or "recommend" in lower:
        topic = prompt.split(":", 1)[-1].strip()
        return (
            f"Learning Path for {topic}\n\n"
            "1. Beginner: Learn the basic concepts and terminology.\n"
            "2. Beginner: Practice simple examples.\n"
            "3. Intermediate: Work with practical exercises and small projects.\n"
            "4. Advanced: Study optimization, advanced concepts and real-world projects.\n"
            "5. Resources: Use textbooks, tutorials, videos and hands-on practice."
        )

    return (
        "EduGenie demo answer:\n\n"
        "This is a local response because GEMINI_API_KEY is not configured. "
        "Configure the API key in .env for Gemini-powered answers."
    )


def clean_json_block(text: str) -> str:
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def generate_quiz(text: str) -> list[dict[str, Any]]:
    prompt = f"""
You are a quiz generator for students.

From the following passage, create exactly 3 multiple-choice questions.
Each question must contain:
- question
- options: exactly 4 strings
- answer: exactly one option from the options

Return ONLY valid JSON in this format:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Passage:
{text}
"""

    if not GEMINI_API_KEY:
        return [
            {
                "question": "What is the main purpose of EduGenie?",
                "options": [
                    "Educational learning support",
                    "Video editing",
                    "Online shopping",
                    "File compression"
                ],
                "answer": "Educational learning support"
            },
            {
                "question": "Which backend framework does EduGenie use?",
                "options": ["FastAPI", "Django", "Flask", "Spring"],
                "answer": "FastAPI"
            },
            {
                "question": "Which feature creates multiple-choice questions?",
                "options": [
                    "Quiz generation",
                    "Image editing",
                    "File upload",
                    "Theme selection"
                ],
                "answer": "Quiz generation"
            }
        ]

    try:
        raw = gemini_generate(prompt)
        data = json.loads(clean_json_block(raw))
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return []


def answer_question(question: str) -> str:
    return gemini_generate(
        f"Answer this academic/general knowledge question clearly and concisely: {question}"
    )


def explain_topic(topic: str) -> str:
    return gemini_generate(
        f"Explain this topic in simple language for a student: {topic}"
    )


def summarize_text(text: str) -> str:
    return gemini_generate(
        f"Summarize the following educational text in simple language while retaining the important points: {text}"
    )


def get_learning_recommendations(topic: str) -> str:
    return gemini_generate(
        f"""
Create a structured learning path for the topic: {topic}.
Organize it from beginner to intermediate to advanced.
Include key topics, suggested practice, estimated progression and useful resource types.
Keep it clear and student-friendly.
"""
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": "EduGenie",
        "gemini_configured": bool(GEMINI_API_KEY)
    }


@app.get("/qa")
async def qa(question: str):
    if not question.strip():
        return JSONResponse({"error": "Please provide a question."}, status_code=400)
    return {"question": question, "answer": answer_question(question)}


@app.post("/explain")
async def explain(request: Request):
    data = await request.json()
    topic = str(data.get("topic", "")).strip()
    if not topic:
        return JSONResponse({"error": "Please provide a topic."}, status_code=400)
    return {"topic": topic, "explanation": explain_topic(topic)}


@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    text = str(data.get("text", "")).strip()
    if not text:
        return JSONResponse({"error": "Please provide text to summarize."}, status_code=400)
    return {"summary": summarize_text(text)}


@app.post("/quiz")
async def quiz(request: Request):
    data = await request.json()
    text = str(data.get("text", "")).strip()
    if not text:
        return JSONResponse({"error": "Please provide text for quiz generation."}, status_code=400)
    return {"quiz": generate_quiz(text)}


@app.get("/learn/recommendations")
async def learning_recommendations(topic: str):
    if not topic.strip():
        return JSONResponse({"error": "Please provide a topic."}, status_code=400)
    return {
        "topic": topic,
        "recommendation": get_learning_recommendations(topic)
    }


@app.post("/action")
async def action(request: Request):
    """Single endpoint used by the HTML frontend."""
    data = await request.json()
    task = data.get("task", "")
    text = str(data.get("text", "")).strip()

    if not text:
        return JSONResponse({"error": "Please enter some input."}, status_code=400)

    if task == "qa":
        return {"result": answer_question(text)}
    if task == "explain":
        return {"result": explain_topic(text)}
    if task == "quiz":
        return {"result": generate_quiz(text), "type": "quiz"}
    if task == "summary":
        return {"result": summarize_text(text)}
    if task == "recommend":
        return {"result": get_learning_recommendations(text)}

    return JSONResponse({"error": "Unknown task."}, status_code=400)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
