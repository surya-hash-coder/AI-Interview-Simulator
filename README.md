# InterviewAI

AI-powered mock interview simulator. Upload your resume and get interview questions generated specifically from your skills and experience.

## Tech Stack

- **Backend**: Python + Flask
- **AI**: Groq (Llama 3.3 70B) — free
- **Auth**: Firebase
- **PDF**: pypdf
- **Frontend**: HTML + CSS + Vanilla JS

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/interviewAI.git
cd interviewAI
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your keys:
- **GROQ_API_KEY** — get free key at https://console.groq.com
- **SECRET_KEY** — any random string

### 5. Run the app
```bash
python app.py
```

Open http://localhost:5000

## Features

- Upload PDF resume → AI scans every word
- Generates questions specific to YOUR skills and projects
- Voice input support (Chrome only)
- AI evaluates every answer with score + feedback
- Performance analytics dashboard

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GROQ_API_KEY` | Groq API key (free at console.groq.com) | Yes |
| `SECRET_KEY` | Flask session secret key | No (has default) |

## Notes

- Voice input requires Google Chrome
- PDF must be text-based (not a scanned image)
- Test AI connection at http://localhost:5000/test
