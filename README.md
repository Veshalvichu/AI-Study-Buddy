# ⚡ AI Study Buddy

An AI-powered study assistant that turns your notes into quizzes and flashcards — with progress tracking, streaks, and analytics.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat-square&logo=mongodb)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-orange?style=flat-square)

---

## ✨ Features

- 🧠 **AI Quiz Generator** — Paste your notes, get instant multiple-choice questions
- 🃏 **Flashcard Mode** — Flip cards with self-grading (Got it / Almost / To Review)
- 📊 **Dashboard Analytics** — Score progress charts, topic breakdown, session history
- 🔥 **Streak Tracker** — Daily study streaks to keep you motivated
- 🏆 **Achievements** — Unlock badges as you study more
- 👤 **User Profiles** — Personal stats, bio, and accuracy overview
- 🌙 **Dark / Light Theme** — Toggle between themes with one click
- ☁️ **Cloud Storage** — All data saved to MongoDB Atlas

---

## 🖥️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask |
| AI Model | Groq API (LLaMA 3.3 70B) |
| Database | MongoDB Atlas |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Fonts | Space Grotesk, JetBrains Mono |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11
- MongoDB Atlas account (free tier)
- Groq API key (free at console.groq.com)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/Veshalvichu/AI-Study-Buddy.git
cd AI-Study-Buddy
```

**2. Install dependencies**
```bash
py -3.11 -m pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
```
Edit `.env` with your keys:
```
SECRET_KEY=your-random-secret-key
GROQ_API_KEY=your-groq-api-key
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

**4. Run the app**
```bash
py -3.11 app.py
```

**5. Open in browser**
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
AI-Study-Buddy/
├── app.py                  # Main Flask application
├── study_buddy.py          # Terminal version
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── static/
│   ├── css/
│   │   └── style.css       # All styles + dark/light theme
│   └── js/
│       └── main.js         # Theme toggle
└── templates/
    ├── base.html           # Base layout + navbar
    ├── login.html          # Username login page
    ├── dashboard.html      # Analytics dashboard
    ├── quiz.html           # Quiz mode
    ├── flashcards.html     # Flashcard mode
    └── profile.html        # User profile + achievements
```

---

## 🔑 Getting API Keys

### Groq API Key (Free)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → API Keys → Create API Key
3. Paste into `.env` as `GROQ_API_KEY`

### MongoDB Atlas (Free)
1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Create free M0 cluster
3. Create database user + allow network access from anywhere
4. Get connection string → paste into `.env` as `MONGO_URI`

---

## 📸 Pages

| Page | Description |
|------|-------------|
| `/login` | Username-based login / auto account creation |
| `/dashboard` | Score charts, streak, recent sessions, quick actions |
| `/quiz` | Paste notes → AI generates MCQ quiz |
| `/flashcards` | Paste notes → AI generates flip cards |
| `/profile` | Stats, achievements, edit name & bio |

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret key |
| `GROQ_API_KEY` | Groq API key for AI features |
| `MONGO_URI` | MongoDB Atlas connection string |
| `SMTP_USER` | Gmail address (optional, for email OTP) |
| `SMTP_PASS` | Gmail app password (optional) |

---

## 🛠️ Built With

- [Flask](https://flask.palletsprojects.com/) — Web framework
- [Groq](https://groq.com/) — Fast AI inference (LLaMA 3.3 70B)
- [PyMongo](https://pymongo.readthedocs.io/) — MongoDB driver
- [Chart.js](https://www.chartjs.org/) — Dashboard charts
- [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) — UI font

---

## 📄 License

MIT License — feel free to use and modify for your own projects.

---

Made with ❤️ by [Veshal](https://github.com/Veshalvichu)
