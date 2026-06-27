import json
import os
import datetime
import certifi
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "studybuddy-super-secret-2024")

# ── CLIENTS ───────────────────────────────────────────────────────────────────
groq_client  = Groq(api_key=os.getenv("GROQ_API_KEY"))
import certifi
mongo_client = MongoClient(
    os.getenv("MONGO_URI"),
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)
db           = mongo_client["studybuddy"]

users_col    = db["users"]
sessions_col = db["quiz_sessions"]

MODEL = "llama-3.3-70b-versatile"

# ── AUTH ──────────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ── AI HELPERS ────────────────────────────────────────────────────────────────
def generate_questions(notes, num=5):
    prompt = f"""You are a quiz generator. Read the notes below and create exactly {num} multiple-choice questions.
RULES:
- Each question must have 4 options labeled A, B, C, D
- Return ONLY valid JSON array, no extra text, no markdown fences
FORMAT:
[
  {{
    "question": "Question text?",
    "options": {{"A": "opt1", "B": "opt2", "C": "opt3", "D": "opt4"}},
    "answer": "A",
    "explanation": "Why A is correct"
  }}
]
NOTES:
{notes}"""
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def generate_flashcards(notes, num=8):
    prompt = f"""You are a flashcard generator. Read the notes below and create exactly {num} flashcards.
Return ONLY valid JSON array, no extra text, no markdown fences.
FORMAT:
[
  {{
    "front": "Term or question",
    "back": "Definition or answer",
    "hint": "A short one-word hint"
  }}
]
NOTES:
{notes}"""
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── AUTH ROUTES ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data     = request.json
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"error": "Please enter a username"}), 400

    # Find or create user by username
    user = users_col.find_one({"username": username.lower()})
    if not user:
        new_user = {
            "username":   username.lower(),
            "name":       username,
            "avatar":     f"https://api.dicebear.com/7.x/thumbs/svg?seed={username}",
            "created_at": datetime.datetime.utcnow(),
            "streak":     0,
            "last_study": None,
            "bio":        "",
        }
        result  = users_col.insert_one(new_user)
        user_id = str(result.inserted_id)
        is_new  = True
    else:
        user_id = str(user["_id"])
        is_new  = False

    session["user_id"]  = user_id
    session["username"] = username.lower()
    return jsonify({"ok": True, "redirect": "/dashboard", "new": is_new})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── APP ROUTES ────────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    from bson import ObjectId
    user = users_col.find_one({"_id": ObjectId(session["user_id"])})
    today = datetime.date.today()
    last  = user.get("last_study")
    if last:
        last_date = last.date() if isinstance(last, datetime.datetime) else last
        if (today - last_date).days > 1:
            users_col.update_one({"_id": ObjectId(session["user_id"])}, {"$set": {"streak": 0}})
            user["streak"] = 0
    quiz_sessions = list(sessions_col.find({"user_id": session["user_id"]}).sort("date", -1).limit(50))
    for s in quiz_sessions:
        s["_id"] = str(s["_id"])
        if isinstance(s.get("date"), datetime.datetime):
            s["date"] = s["date"].strftime("%Y-%m-%d")
    return render_template("dashboard.html", user=user, sessions=quiz_sessions)

@app.route("/quiz")
@login_required
def quiz():
    from bson import ObjectId
    user = users_col.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("quiz.html", user=user)

@app.route("/flashcards")
@login_required
def flashcards():
    from bson import ObjectId
    user = users_col.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("flashcards.html", user=user)

@app.route("/profile")
@login_required
def profile():
    from bson import ObjectId
    user = users_col.find_one({"_id": ObjectId(session["user_id"])})
    all_s    = list(sessions_col.find({"user_id": session["user_id"]}))
    total_q  = sum(s.get("total", 0) for s in all_s)
    total_c  = sum(s.get("correct", 0) for s in all_s)
    accuracy = round((total_c / total_q) * 100) if total_q else 0
    return render_template("profile.html", user=user,
                           total_sessions=len(all_s),
                           total_questions=total_q, accuracy=accuracy)

# ── API ROUTES ────────────────────────────────────────────────────────────────
@app.route("/api/generate-quiz", methods=["POST"])
@login_required
def api_generate_quiz():
    data  = request.json
    notes = data.get("notes", "").strip()
    topic = data.get("topic", "General").strip()
    num   = min(int(data.get("num", 5)), 20)
    if not notes:
        return jsonify({"error": "No notes provided"}), 400
    try:
        questions = generate_questions(notes, num)
        session["questions"] = questions
        session["topic"]     = topic
        session["q_index"]   = 0
        session["correct"]   = 0
        return jsonify({"ok": True, "total": len(questions)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/question")
@login_required
def api_question():
    questions = session.get("questions", [])
    idx       = session.get("q_index", 0)
    if idx >= len(questions):
        return jsonify({"done": True})
    q = questions[idx]
    return jsonify({"done": False, "index": idx, "total": len(questions),
                    "question": q["question"], "options": q["options"]})

@app.route("/api/answer", methods=["POST"])
@login_required
def api_answer():
    data      = request.json
    user_ans  = data.get("answer", "").upper()
    questions = session.get("questions", [])
    idx       = session.get("q_index", 0)
    if idx >= len(questions):
        return jsonify({"error": "No active question"}), 400
    q      = questions[idx]
    correct = q["answer"]
    is_ok  = user_ans == correct
    if is_ok:
        session["correct"] = session.get("correct", 0) + 1
    session["q_index"] = idx + 1
    session.modified   = True
    if session["q_index"] >= len(questions):
        _save_quiz_session()
    return jsonify({"correct": is_ok, "right_answer": correct,
                    "explanation": q["explanation"],
                    "score": session["correct"],
                    "answered": session["q_index"],
                    "total": len(questions)})

def _save_quiz_session():
    from bson import ObjectId
    today   = datetime.datetime.utcnow()
    total_q = len(session.get("questions", []))
    total_c = session.get("correct", 0)
    sessions_col.insert_one({
        "user_id": session["user_id"],
        "topic":   session.get("topic", "General"),
        "correct": total_c,
        "total":   total_q,
        "score":   round((total_c / total_q) * 100) if total_q else 0,
        "date":    today,
    })
    user   = users_col.find_one({"_id": ObjectId(session["user_id"])})
    last   = user.get("last_study")
    streak = user.get("streak", 0)
    if last:
        last_date = last.date() if isinstance(last, datetime.datetime) else last
        diff = (today.date() - last_date).days
        if diff == 1:
            streak += 1
        elif diff > 1:
            streak = 1
    else:
        streak = 1
    users_col.update_one({"_id": ObjectId(session["user_id"])},
                         {"$set": {"streak": streak, "last_study": today}})

@app.route("/api/generate-flashcards", methods=["POST"])
@login_required
def api_generate_flashcards():
    data  = request.json
    notes = data.get("notes", "").strip()
    num   = min(int(data.get("num", 8)), 20)
    if not notes:
        return jsonify({"error": "No notes provided"}), 400
    try:
        cards = generate_flashcards(notes, num)
        return jsonify({"ok": True, "cards": cards})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/update-profile", methods=["POST"])
@login_required
def api_update_profile():
    from bson import ObjectId
    data = request.json
    users_col.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"name": data.get("name", ""), "bio": data.get("bio", "")}}
    )
    return jsonify({"ok": True})

@app.route("/api/stats")
@login_required
def api_stats():
    all_s = list(sessions_col.find({"user_id": session["user_id"]}).sort("date", 1))
    return jsonify([{
        "topic":   s.get("topic", "General"),
        "correct": s.get("correct", 0),
        "total":   s.get("total", 0),
        "score":   s.get("score", 0),
        "date":    s["date"].strftime("%Y-%m-%d") if isinstance(s.get("date"), datetime.datetime) else str(s.get("date", "")),
    } for s in all_s])

if __name__ == "__main__":
    app.run(debug=True, port=5000)