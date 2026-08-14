import os
import json
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pypdf import PdfReader
import anthropic
from jobs_data import load_sample_jobs
from matcher import mock_match_jobs, ai_match_jobs
from cover_letter import mock_generate_cover_letter, ai_generate_cover_letter
from resume_tailor import mock_tailor_resume, ai_tailor_resume
from resume_builder import mock_generate_bullets, ai_generate_bullets, mock_generate_summary, ai_generate_summary, mock_ats_check, ai_ats_check, mock_quick_draft, ai_quick_draft

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Where we store the most recently parsed resume, so the browser extension
# can fetch it via /api/resume without needing a full database yet.
LAST_RESUME_FILE = os.path.join(os.path.dirname(__file__), "last_resume.json")

# MOCK_MODE lets you test the whole app without any Anthropic API credits.
# Set MOCK_MODE=true to use simple keyword-based parsing instead of real AI.
# Set MOCK_MODE=false (or leave unset) once you have API credits, to use real AI.
MOCK_MODE = os.environ.get("MOCK_MODE", "false").lower() == "true"

client = None if MOCK_MODE else anthropic.Anthropic()

COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Flask", "Django",
    "Java", "C++", "C#", "SQL", "PostgreSQL", "MySQL", "MongoDB", "AWS", "Azure",
    "Docker", "Kubernetes", "Git", "HTML", "CSS", "Excel", "PowerPoint",
    "Communication", "Project Management", "Sales", "Marketing", "Accounting",
    "Maintenance", "Production", "Plant Operations", "Equipment Reliability",
    "Preventive Maintenance", "Quality Control", "Safety Management", "Logistics",
    "Supply Chain", "Procurement", "SAP", "Six Sigma", "Lean Manufacturing",
    "Team Leadership", "Budgeting", "Customer Service", "Nursing", "Teaching",
    "Civil Engineering", "Mechanical Engineering", "Electrical Engineering",
    "HVAC", "AutoCAD", "Welding", "Operations Management", "Inventory Management",
]


def mock_parse_resume(resume_text):
    """Simple keyword-based parser used when there's no API credit available.
    Not as smart as real AI, but lets you test the rest of the app for free."""
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
    phone_match = re.search(r"(\+?\d[\d\-\s]{7,}\d)", resume_text)
    found_skills = [s for s in COMMON_SKILLS if s.lower() in resume_text.lower()]
    lines = [l.strip() for l in resume_text.strip().split("\n") if l.strip()]
    first_line = lines[0] if lines else ""

    # Heuristic: the line right after the name is often the job title on
    # most resumes (e.g. "MUHAMMAD HANIF" / "Maintenance & Production Manager").
    guessed_title = None
    if len(lines) > 1:
        candidate = lines[1]
        if len(candidate) < 60 and "@" not in candidate and not re.search(r"\d{3,}", candidate):
            guessed_title = candidate

    job_titles = [guessed_title] if guessed_title else []
    search_keywords = ([guessed_title] if guessed_title else []) + found_skills[:4]

    return {
        "full_name": first_line if len(first_line) < 60 else None,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "job_titles": job_titles,
        "years_experience": None,
        "skills": found_skills,
        "education": [],
        "summary": "(Mock mode: this is a basic keyword extraction, not real AI parsing. Add API credits and set MOCK_MODE=false for full accuracy.)",
        "suggested_search_keywords": search_keywords[:5],
    }


def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def parse_resume_with_ai(resume_text):
    """Send resume text to Claude and get back structured JSON data."""
    prompt = f"""You are a resume parsing assistant. Read the resume text below and extract
structured information from it ONLY from what is actually present in the text. Do not
invent, guess, or use placeholder/example data (like "John Doe" or "example.com") under
any circumstances.

If the text below is garbled, empty, mostly non-text characters, or otherwise not a
readable resume, respond with EXACTLY this JSON and nothing else:
{{"error": "unable to extract readable text from this file"}}

Otherwise, respond with ONLY valid JSON, no preamble, no markdown fences, no extra
commentary. Use this exact schema:

{{
  "full_name": string or null,
  "email": string or null,
  "phone": string or null,
  "job_titles": [list of past/target job titles found],
  "years_experience": number (best estimate, integer),
  "skills": [list of skills, technologies, tools mentioned],
  "education": [list of degrees/institutions],
  "summary": "a 2-3 sentence professional summary written in third person",
  "suggested_search_keywords": [3-6 keywords best used to search for matching jobs]
}}

Resume text:
---
{resume_text}
---"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # Safety: strip markdown fences if the model adds them anyway
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        if file.filename.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf(filepath)
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                resume_text = f.read()

        cleaned = resume_text.strip()
        print(f"[DEBUG] Extracted {len(cleaned)} characters from {file.filename}")
        print(f"[DEBUG] First 300 chars: {cleaned[:300]!r}")

        if not cleaned:
            return jsonify({"error": "Could not extract any text from this file. If this is a scanned/image-based PDF, text extraction won't work — try a text-based PDF or .txt instead."}), 400

        # Rough sanity check: too short, or too few normal letters, usually means garbled extraction
        printable_ratio = sum(c.isalnum() or c.isspace() for c in cleaned) / len(cleaned)
        if len(cleaned) < 50 or printable_ratio < 0.6:
            return jsonify({"error": f"Extracted text looks garbled or too short ({len(cleaned)} chars, {printable_ratio:.0%} readable). This PDF's text encoding may not be extractable. Try re-exporting it as PDF from Word, or use a .txt file instead."}), 400

        parsed_data = mock_parse_resume(cleaned) if MOCK_MODE else parse_resume_with_ai(cleaned)

        if isinstance(parsed_data, dict) and "error" in parsed_data and len(parsed_data) == 1:
            return jsonify({"error": "AI could not reliably read this resume's content. Try a .txt file to confirm the pipeline works, then we'll debug the PDF."}), 422

        # Save this as the "current" resume so the browser extension can fetch it
        with open(LAST_RESUME_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f)

        return jsonify({"success": True, "data": parsed_data})

    except json.JSONDecodeError:
        return jsonify({"error": "AI returned unexpected format. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file after processing
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/match", methods=["POST"])
def match_jobs():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No resume data provided"}), 400

    # Onboarding preferences (if provided) take priority over resume-derived guesses
    resume_data = payload.get("resume", payload)
    preferred_query = payload.get("preferred_query")
    preferred_country = payload.get("preferred_country")

    job_titles = resume_data.get("job_titles") or []
    keywords = resume_data.get("suggested_search_keywords") or []
    if preferred_query:
        query = preferred_query
    elif job_titles:
        query = job_titles[0]
    elif keywords:
        query = keywords[0]
    else:
        query = "jobs"

    country = preferred_country or "pk"
    jobs = load_sample_jobs(query=query, country=country)

    try:
        if MOCK_MODE:
            matched = mock_match_jobs(resume_data, jobs)
        else:
            matched = ai_match_jobs(resume_data, jobs, client)
        return jsonify({"success": True, "jobs": matched})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cover-letter", methods=["POST"])
def generate_cover_letter():
    payload = request.get_json()
    if not payload or "resume" not in payload or "job" not in payload:
        return jsonify({"error": "Missing resume or job data"}), 400

    resume_data = payload["resume"]
    job = payload["job"]

    try:
        if MOCK_MODE:
            letter = mock_generate_cover_letter(resume_data, job)
        else:
            letter = ai_generate_cover_letter(resume_data, job, client)
        return jsonify({"success": True, "cover_letter": letter})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/resume-tailor", methods=["POST"])
def tailor_resume():
    payload = request.get_json()
    if not payload or "resume" not in payload or "job" not in payload:
        return jsonify({"error": "Missing resume or job data"}), 400

    resume_data = payload["resume"]
    job = payload["job"]

    try:
        if MOCK_MODE:
            tailored = mock_tailor_resume(resume_data, job)
        else:
            tailored = ai_tailor_resume(resume_data, job, client)
        return jsonify({"success": True, "tailored": tailored})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/resume-builder/bullets", methods=["POST"])
def builder_bullets():
    payload = request.get_json()
    if not payload or "raw_input" not in payload:
        return jsonify({"error": "Missing raw_input"}), 400

    job_title = payload.get("job_title", "this role")
    raw_input = payload["raw_input"]
    mode = payload.get("mode", "improve")

    try:
        if MOCK_MODE:
            result = mock_generate_bullets(job_title, raw_input, mode)
        else:
            result = ai_generate_bullets(job_title, raw_input, client, mode)
        return jsonify({"success": True, "bullets": result["bullets"], "feedback": result.get("feedback")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/resume-builder/summary", methods=["POST"])
def builder_summary():
    builder_data = request.get_json()
    if not builder_data:
        return jsonify({"error": "Missing resume builder data"}), 400

    try:
        if MOCK_MODE:
            summary = mock_generate_summary(builder_data)
        else:
            summary = ai_generate_summary(builder_data, client)
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/resume-builder/quick-draft", methods=["POST"])
def builder_quick_draft():
    payload = request.get_json()
    if not payload or "job_title" not in payload:
        return jsonify({"error": "Missing job_title"}), 400

    job_title = payload["job_title"]
    experience_level = payload.get("experience_level", "Mid-level")

    try:
        if MOCK_MODE:
            draft = mock_quick_draft(job_title, experience_level)
        else:
            draft = ai_quick_draft(job_title, experience_level, client)
        return jsonify({"success": True, "draft": draft})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/resume-builder/ats-check", methods=["POST"])
def builder_ats_check():
    builder_data = request.get_json()
    if not builder_data:
        return jsonify({"error": "Missing resume builder data"}), 400

    try:
        if MOCK_MODE:
            result = mock_ats_check(builder_data)
        else:
            result = ai_ats_check(builder_data, client)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/resume", methods=["GET"])
def get_current_resume():
    """Used by the browser extension to fetch the most recently parsed resume."""
    if not os.path.exists(LAST_RESUME_FILE):
        return jsonify({"error": "No resume parsed yet. Upload one on the JobApplyz site first."}), 404
    with open(LAST_RESUME_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify({"success": True, "data": data})


if __name__ == "__main__":
    print("=" * 50)
    if MOCK_MODE:
        print("MOCK MODE: ON  (no API calls will be made, free testing)")
    else:
        print("MOCK MODE: OFF (using real Anthropic API — will cost credits)")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
