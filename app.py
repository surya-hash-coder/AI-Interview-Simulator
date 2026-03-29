"""
InterviewAI - app.py
Keys loaded from .env file — safe to push to Git.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import json
import traceback
import os
from utils.resume_parser import extract_resume_text

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "interviewai-dev-secret")
CORS(app)

# ── Load keys from .env ───────────────────────────────────────
GROQ_KEY   = os.getenv("GROQ_API_KEY")
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


# ─────────────────────────────────────────────────────────────
# Call Groq AI
# ─────────────────────────────────────────────────────────────
def ask_ai(prompt, system="You are a senior technical interviewer."):
    if not GROQ_KEY:
        print("[AI ERROR] GROQ_API_KEY not set in .env file")
        return None

    print("\n" + "─" * 60)
    print(f"[AI] Prompt length: {len(prompt)} chars")
    print(f"[AI] Preview:\n{prompt[:300]}")
    print("─" * 60)

    try:
        r = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type":  "application/json"
            },
            json={
                "model":       GROQ_MODEL,
                "messages":    [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt}
                ],
                "max_tokens":  2048,
                "temperature": 0.8
            },
            timeout=60
        )
        r.raise_for_status()
        out = r.json()["choices"][0]["message"]["content"]
        print(f"[AI] Response ({len(out)} chars):\n{out[:500]}")
        return out
    except requests.exceptions.ConnectionError:
        print("[AI ERROR] Cannot reach Groq — check internet connection")
        return None
    except requests.exceptions.Timeout:
        print("[AI ERROR] Timed out after 60s")
        return None
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return None


# ─────────────────────────────────────────────────────────────
# Parse JSON from AI response
# ─────────────────────────────────────────────────────────────
def get_json(text):
    if not text:
        return None
    s = text.strip()
    if "```" in s:
        for part in s.split("```"):
            p = part.strip().lstrip("json").strip()
            if p.startswith("[") or p.startswith("{"):
                s = p
                break
    for o, c in [("[", "]"), ("{", "}")]:
        a, b = s.find(o), s.rfind(c)
        if a != -1 and b > a:
            try:
                return json.loads(s[a:b+1])
            except:
                pass
    return None


# ─────────────────────────────────────────────────────────────
# Detect skills in resume text
# ─────────────────────────────────────────────────────────────
def find_skills(text):
    all_skills = [
        "Python","JavaScript","TypeScript","Java","C++","C#","Go","Rust","Ruby","PHP","Kotlin","Swift","Scala","R",
        "React","Vue","Angular","Node.js","Express","Django","Flask","FastAPI","Spring Boot","Laravel","Next.js","Nuxt.js",
        "SQL","MySQL","PostgreSQL","MongoDB","Redis","Elasticsearch","SQLite","Oracle","DynamoDB","Firebase","Cassandra",
        "AWS","Azure","GCP","Google Cloud","Docker","Kubernetes","Terraform","Jenkins","GitHub Actions","CI/CD","Ansible",
        "Git","GitHub","REST API","GraphQL","gRPC","HTML","CSS","Tailwind","Bootstrap","Webpack","Vite","SASS",
        "Machine Learning","Deep Learning","TensorFlow","PyTorch","Pandas","NumPy","Scikit-learn","Keras","OpenAI","LLM",
        "Data Science","NLP","Computer Vision","OpenCV","Spark","Kafka","Airflow","Power BI","Tableau",
        "Linux","Bash","Shell","Agile","Scrum","Microservices","System Design","DevOps","SRE","Serverless",
        "Android","iOS","React Native","Flutter","Unity","Blockchain","Solidity","Web3",
        "Selenium","Pytest","Jest","Cypress","JUnit","TDD","Testing",
        "RabbitMQ","Celery","Socket.io","OAuth","JWT","LDAP","SSO","Nginx","Apache"
    ]
    tl = text.lower()
    seen, result = set(), []
    for s in all_skills:
        if s.lower() in tl and s not in seen:
            seen.add(s)
            result.append(s)
    print(f"[SKILLS] Found {len(result)}: {result}")
    return result[:20]


# ─────────────────────────────────────────────────────────────
# Page Routes
# ─────────────────────────────────────────────────────────────
@app.route("/")
def index():     return render_template("index.html")
@app.route("/login")
def login():     return render_template("login.html")
@app.route("/signup")
def signup():    return render_template("signup.html")
@app.route("/dashboard")
def dashboard(): return render_template("dashboard.html")
@app.route("/upload")
def upload():    return render_template("upload.html")
@app.route("/interview")
def interview(): return render_template("interview.html")
@app.route("/result")
def result():    return render_template("result.html")
@app.route("/analytics")
def analytics(): return render_template("analytics.html")


# ─────────────────────────────────────────────────────────────
# TEST — http://localhost:5000/test
# ─────────────────────────────────────────────────────────────
@app.route("/test")
def test():
    if not GROQ_KEY:
        return jsonify({
            "api_working": False,
            "message": "GROQ_API_KEY not set. Add it to your .env file.",
            "fix": "Create a .env file with: GROQ_API_KEY=your_key_here"
        })
    raw = ask_ai('Reply with exactly: {"working": true}', system="Reply with JSON only.")
    ok  = raw is not None and "true" in str(raw).lower()
    return jsonify({
        "api_working": ok,
        "message": "AI connected and working!" if ok else "AI not reachable — check internet connection",
        "groq_key_loaded": bool(GROQ_KEY),
        "next_step": "Upload your resume at /upload" if ok else "Fix internet/firewall first"
    })


# ─────────────────────────────────────────────────────────────
# UPLOAD RESUME
# ─────────────────────────────────────────────────────────────
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    print("\n" + "★" * 60)
    print("[UPLOAD] Resume received")

    if "resume" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "error": "Only PDF files accepted"}), 400

    try:
        pdf_bytes   = file.read()
        resume_text = extract_resume_text(pdf_bytes)

        print(f"[UPLOAD] Extracted {len(resume_text)} characters")
        print(f"[UPLOAD] Text:\n{'─'*40}\n{resume_text}\n{'─'*40}")

        if not resume_text or len(resume_text.strip()) < 30:
            return jsonify({
                "success": False,
                "error": "Could not extract text from PDF. Make sure it is a text-based PDF, not a scanned image."
            }), 400

        skills        = find_skills(resume_text)
        skills_str    = ", ".join(skills) if skills else "various technical skills"
        resume_for_ai = resume_text.strip()[:6000]

        prompt = f"""You are a senior technical interviewer. You have just read this candidate's complete resume.

CANDIDATE RESUME:
{resume_for_ai}

SKILLS FOUND: {skills_str}

Generate exactly 15 interview questions for THIS specific candidate.

RULES:
1. Every question must come from something written in the resume above
2. Each question must name a real skill, project, tool, or experience from the resume
3. Never ask a question any random developer could be asked
4. Cover 15 different topics — no repeats
5. Write like a real interviewer: "I see you used X", "Walk me through Y", "What was hardest about Z?"

Return ONLY a JSON array of exactly 15 strings. No other text.
["Question 1?", "Question 2?", ..., "Question 15?"]"""

        raw = ask_ai(prompt, system="Respond ONLY with a valid JSON array of 15 question strings.")

        questions = []
        if raw:
            parsed = get_json(raw)
            if isinstance(parsed, list):
                questions = [str(q).strip() for q in parsed if str(q).strip()]
                print(f"[UPLOAD] Generated {len(questions)} questions")
                for i, q in enumerate(questions):
                    print(f"  Q{i+1}: {q}")

        summary = ""
        if raw is not None:
            s_raw   = ask_ai(
                f"Summarize this resume in 2 sentences. Focus on role, tech stack, experience level:\n\n{resume_for_ai[:2000]}",
                system="Write exactly 2 sentences."
            )
            summary = (s_raw or "").strip()
        if not summary:
            summary = f"Candidate with skills in: {skills_str[:100]}."

        print("★" * 60 + "\n")

        return jsonify({
            "success":         True,
            "resume_text":     resume_text.strip(),
            "summary":         summary,
            "questions":       questions,
            "skills_detected": skills,
            "stats": {
                "chars_extracted": len(resume_text),
                "skills_found":    len(skills),
                "questions_made":  len(questions),
                "ai_connected":    raw is not None
            }
        })

    except Exception as e:
        print(f"[UPLOAD ERROR] {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────────────────────────
# GET QUESTIONS FOR INTERVIEW
# ─────────────────────────────────────────────────────────────
@app.route("/get_questions", methods=["POST"])
def get_questions():
    data        = request.get_json()
    resume_text = (data.get("resume_text") or "").strip()
    skills      = data.get("skills") or []
    count       = int(data.get("count", 5))
    level       = data.get("level", "intermediate")
    exclude     = data.get("exclude") or []
    topic       = (data.get("topic") or "").strip()

    print(f"\n[GET_Q] {count} questions | resume: {len(resume_text)} chars | topic: {topic}")

    # Topic mode
    if (not resume_text or len(resume_text.strip()) < 30) and topic and topic != "resume":
        topics = {
            "general":  "general software engineering (OOP, design patterns, APIs, databases)",
            "dsa":      "data structures and algorithms (arrays, trees, graphs, sorting, complexity)",
            "system":   "system design (scalability, caching, load balancing, microservices)",
            "frontend": "frontend development (JavaScript, CSS, React, browser APIs, performance)",
            "backend":  "backend development (REST APIs, auth, databases, caching, security)",
        }
        desc  = topics.get(topic, "software engineering")
        avoid = ("Do NOT repeat:\n" + "\n".join(f"- {q}" for q in exclude)) if exclude else ""
        raw2  = ask_ai(
            f"Generate {count} unique {level}-level interview questions about {desc}.\nEach covers a different concept.\n{avoid}\nReturn ONLY a JSON array of {count} strings.",
            system="Reply ONLY with a JSON array of question strings."
        )
        qs = []
        if raw2:
            p = get_json(raw2)
            if isinstance(p, list):
                qs = [str(q).strip() for q in p if str(q).strip()]
        if qs:
            return jsonify({"success": True, "questions": qs[:count]})
        return jsonify({"success": False, "questions": [], "error": "Could not generate questions"})

    if not resume_text or len(resume_text.strip()) < 30:
        return jsonify({"success": False, "questions": [], "error": "Resume text is empty. Re-upload your resume."}), 400

    skills_str  = ", ".join(skills) if skills else "see resume"
    exclude_txt = ("\n\nDo NOT repeat:\n" + "\n".join(f"- {q}" for q in exclude)) if exclude else ""

    prompt = f"""You are a senior technical interviewer. Read this resume carefully.

RESUME:
{resume_text[:6000]}

SKILLS: {skills_str}
DIFFICULTY: {level}

Generate exactly {count} questions for THIS candidate.

RULES:
1. Every question references something specific from THIS resume
2. Do NOT write questions any random developer could answer
3. Each question covers a DIFFERENT skill from the resume
4. Use styles like: "You listed X — explain how you used it", "Walk me through Y", "What was hardest about Z?"
{exclude_txt}

Return ONLY a JSON array of exactly {count} strings. Nothing else."""

    raw = ask_ai(prompt, system="Return ONLY a valid JSON array of question strings.")

    questions = []
    if raw:
        parsed = get_json(raw)
        if isinstance(parsed, list):
            questions = [str(q).strip() for q in parsed if str(q).strip()]
            print(f"[GET_Q] Got {len(questions)} questions")

    if questions:
        return jsonify({"success": True, "questions": questions[:count]})

    return jsonify({"success": False, "questions": [], "error": "AI could not generate questions. Visit /test to diagnose."})


# ─────────────────────────────────────────────────────────────
# EVALUATE ANSWER
# ─────────────────────────────────────────────────────────────
@app.route("/evaluate_answer", methods=["POST"])
def evaluate_answer():
    data     = request.get_json()
    question = data.get("question", "")
    answer   = data.get("answer", "")

    if not question or not answer:
        return jsonify({"success": False, "error": "Missing data"}), 400

    raw = ask_ai(
        f"""Evaluate this interview answer.

Question: {question}
Answer: {answer}

Return ONLY this JSON:
{{
  "score": <1-10>,
  "technical_score": <1-10>,
  "communication_score": <1-10>,
  "feedback": "<2-3 sentence assessment>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"],
  "ideal_answer_hint": "<one sentence hint>"
}}""",
        system="You are a technical interviewer. Respond ONLY with valid JSON."
    )

    result = get_json(raw)
    if isinstance(result, dict) and "score" in result:
        return jsonify({"success": True, "evaluation": result})

    return jsonify({"success": True, "evaluation": {
        "score": 5, "technical_score": 5, "communication_score": 6,
        "feedback": "Could not evaluate — AI unavailable.",
        "strengths": [], "improvements": [], "ideal_answer_hint": ""
    }})


# ─────────────────────────────────────────────────────────────
# GENERATE REPORT
# ─────────────────────────────────────────────────────────────
@app.route("/generate_report", methods=["POST"])
def generate_report():
    data     = request.get_json()
    qa_pairs = data.get("qa_pairs", [])

    if not qa_pairs:
        return jsonify({"success": False, "error": "No data"}), 400

    qa_text = "\n\n".join([
        f"Q{i+1}: {qa.get('question','')}\nAnswer: {qa.get('answer','')}\nScore: {qa.get('score','?')}/10"
        for i, qa in enumerate(qa_pairs)
    ])

    raw = ask_ai(
        f"""Review this completed technical interview.

{qa_text}

Return ONLY this JSON:
{{
  "overall_score": <1-10>,
  "technical_score": <1-10>,
  "communication_score": <1-10>,
  "summary": "<3-4 sentence assessment>",
  "top_strengths": ["<s1>", "<s2>", "<s3>"],
  "areas_to_improve": ["<a1>", "<a2>", "<a3>"],
  "recommended_topics": ["<t1>", "<t2>", "<t3>"],
  "hire_recommendation": "<Strong Yes / Yes / Maybe / No>"
}}""",
        system="You are a hiring manager. Respond ONLY with valid JSON."
    )

    report = get_json(raw)
    if isinstance(report, dict) and "overall_score" in report:
        return jsonify({"success": True, "report": report})

    return jsonify({"success": False, "error": "Could not generate report"}), 500


if __name__ == "__main__":
    print("\n" + "★" * 50)
    print("  InterviewAI Server")
    print("  App:  http://localhost:5000")
    print("  Test: http://localhost:5000/test")
    if not GROQ_KEY:
        print("  WARNING: GROQ_API_KEY not set in .env file!")
    print("★" * 50 + "\n")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
