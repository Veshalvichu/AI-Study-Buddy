import json
import os
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

# ── CONFIG ──────────────────────────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"
SCORES_FILE = "scores.json"
# ────────────────────────────────────────────────────────────────────────────


# ── SCORE TRACKING ───────────────────────────────────────────────────────────
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return {"sessions": [], "total_correct": 0, "total_questions": 0}


def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def show_history(scores):
    print("\n── Score History ──────────────────────────")
    if not scores["sessions"]:
        print("  No sessions yet.")
    else:
        for i, s in enumerate(scores["sessions"], 1):
            pct = round((s["correct"] / s["questions"]) * 100) if s["questions"] else 0
            print(f"  Session {i}: {s['correct']}/{s['questions']} ({pct}%)  [{s['topic']}]")
    total = scores["total_questions"]
    correct = scores["total_correct"]
    if total > 0:
        overall = round((correct / total) * 100)
        print(f"\n  Overall: {correct}/{total} ({overall}%)")
    print("───────────────────────────────────────────\n")


# ── AI HELPERS ───────────────────────────────────────────────────────────────
def generate_questions(notes, num_questions=5):
    print(f"\nGenerating {num_questions} questions from your notes...")
    prompt = f"""You are a quiz generator. Read the notes below and create exactly {num_questions} multiple-choice questions.

RULES:
- Each question must have 4 options labeled A, B, C, D
- Clearly mark the correct answer
- Return ONLY valid JSON, no extra text, no markdown

FORMAT (return exactly this structure):
[
  {{
    "question": "Question text here?",
    "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
    "answer": "A",
    "explanation": "Brief explanation why A is correct"
  }}
]

NOTES:
{notes}"""

    response = client.chat.completions.create(
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


def explain_answer(question, user_answer, correct_answer, explanation):
    prompt = f"""A student answered a quiz question incorrectly.

Question: {question}
Student answered: {user_answer}
Correct answer: {correct_answer}
Explanation: {explanation}

Give a short, encouraging 2-sentence explanation to help them understand why {correct_answer} is correct."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


# ── QUIZ RUNNER ───────────────────────────────────────────────────────────────
def run_quiz(questions, topic):
    correct = 0
    total = len(questions)

    print(f"\n── Quiz: {topic} ({'─' * (30 - len(topic))})")
    print(f"   {total} questions  |  Type A, B, C, or D\n")

    for i, q in enumerate(questions, 1):
        print(f"Q{i}. {q['question']}")
        for letter, option in q["options"].items():
            print(f"    {letter}) {option}")

        while True:
            answer = input("\n   Your answer: ").strip().upper()
            if answer in ["A", "B", "C", "D"]:
                break
            print("   Please enter A, B, C, or D")

        if answer == q["answer"]:
            print("   Correct!\n")
            correct += 1
        else:
            print(f"   Wrong. The correct answer is {q['answer']}.")
            clarification = explain_answer(
                q["question"], answer, q["answer"], q["explanation"]
            )
            print(f"   {clarification}\n")

    return correct, total


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    scores = load_scores()

    print("╔══════════════════════════════════╗")
    print("║       AI Study Buddy  v1.0       ║")
    print("╚══════════════════════════════════╝")

    while True:
        print("\nWhat would you like to do?")
        print("  1. Start a new quiz from notes")
        print("  2. View score history")
        print("  3. Quit")

        choice = input("\nEnter 1, 2, or 3: ").strip()

        if choice == "2":
            show_history(scores)

        elif choice == "3":
            print("\nGood luck with your studies!")
            break

        elif choice == "1":
            print("\nHow do you want to provide your notes?")
            print("  1. Type / paste notes directly")
            print("  2. Load from a .txt file")
            src = input("\nEnter 1 or 2: ").strip()

            notes = ""
            topic = "General"

            if src == "1":
                topic = input("Topic name (e.g. 'Python Loops'): ").strip() or "General"
                print("Paste your notes below. When done, type END on a new line and press Enter:\n")
                lines = []
                while True:
                    line = input()
                    if line.strip().upper() == "END":
                        break
                    lines.append(line)
                notes = "\n".join(lines)

            elif src == "2":
                path = input("Enter the full path to your .txt file: ").strip().strip('"')
                if not os.path.exists(path):
                    print(f"File not found: {path}")
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    notes = f.read()
                topic = os.path.splitext(os.path.basename(path))[0]

            if not notes.strip():
                print("No notes provided. Try again.")
                continue

            try:
                num = input("How many questions? (default 5): ").strip()
                num = int(num) if num.isdigit() else 5
                questions = generate_questions(notes, num)
            except Exception as e:
                print(f"Could not generate questions: {e}")
                continue

            correct, total = run_quiz(questions, topic)

            pct = round((correct / total) * 100)
            print(f"\n── Result: {correct}/{total} ({pct}%) ──────────────")
            if pct == 100:
                print("   Perfect score!")
            elif pct >= 70:
                print("   Good job! Keep it up.")
            else:
                print("   Keep studying — you'll get there!")

            scores["sessions"].append({"topic": topic, "correct": correct, "questions": total})
            scores["total_correct"] += correct
            scores["total_questions"] += total
            save_scores(scores)
            print("   Score saved.\n")

        else:
            print("Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()