import json


def mock_generate_bullets(job_title, raw_input, mode="improve"):
    """Free fallback: lightly reformats the user's raw input into bullet-point
    style without real AI rewriting."""
    if not raw_input.strip():
        return {"bullets": ["(Add a few sentences about your responsibilities above, then try again.)"], "feedback": None}
    parts = [p.strip() for p in raw_input.replace("\n", ". ").split(".") if p.strip()]
    bullets = [p[0].upper() + p[1:] if p else p for p in parts[:5]]
    note = "(Mock mode: lightly reformatted, not real AI rewriting. Switch to Real AI mode for polished, achievement-focused bullets.)"
    bullets.append(note)
    feedback = "(Mock mode: recruiter-style feedback needs Real AI mode.)" if mode == "recruiter" else None
    return {"bullets": bullets, "feedback": feedback}


def ai_generate_bullets(job_title, raw_input, client, mode="improve"):
    """Real AI: turns a rough description of responsibilities into sharp,
    ATS-friendly resume bullet points. Three modes:
    - "improve": rewrite into strong, action-oriented, quantified bullets (default)
    - "recruiter": critique the content like a recruiter reviewing it, plus improved bullets
    - "inspire": offer varied, creative phrasing alternatives to choose from
    """
    mode_instructions = {
        "improve": """Rewrite this into 3-5 sharp, action-oriented, ATS-friendly resume bullet
points. Start each with a strong action verb. Quantify impact where the notes suggest a
number, without inventing false numbers. Keep each bullet under 20 words. Plain text only,
no special characters or emojis.""",
        "recruiter": """Act as a recruiter reviewing these notes. First, write 1-2 sentences of
direct, honest feedback on what's currently weak (e.g. too vague, missing metrics, passive
language). Then provide 3-5 improved bullet points that fix those issues. Be constructive
but specific — the kind of feedback a real recruiter would give in 30 seconds of scanning
a resume.""",
        "inspire": """Provide 3-5 alternative, creative-but-professional ways to phrase this
experience as resume bullets — vary the structure and word choice across the options so the
candidate has real choices, not just minor tweaks of the same sentence. Stay honest to the
facts in the notes, don't invent achievements. Plain text only.""",
    }
    instruction = mode_instructions.get(mode, mode_instructions["improve"])

    prompt = f"""You are a professional resume writer helping a candidate write resume content
for their role as "{job_title}".

{instruction}

Respond with ONLY valid JSON, no preamble, no markdown fences, using this schema:
{{"feedback": "<1-2 sentences of feedback, or null if mode is not 'recruiter'>", "bullets": ["bullet 1", "bullet 2", ...]}}

Raw notes:
---
{raw_input}
---"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def mock_generate_summary(builder_data):
    """Free fallback summary generator."""
    name = builder_data.get("full_name", "This candidate")
    role = builder_data.get("target_role", "professional")
    skills = builder_data.get("skills", [])
    skills_text = ", ".join(skills[:4]) if skills else "a range of relevant skills"
    return (
        f"{name} is a {role} with experience in {skills_text}. "
        f"(Mock mode: basic template summary, not real AI writing. Switch to Real AI mode for a genuinely tailored summary.)"
    )


def ai_generate_summary(builder_data, client):
    """Real AI: writes a polished 2-3 sentence professional summary from all
    the resume builder data collected so far."""
    data_json = json.dumps(builder_data, indent=2)
    prompt = f"""Write a concise, professional 2-3 sentence resume summary for this candidate,
based ONLY on the information below. Do not invent facts. Write in third person is NOT
required — write it the way resume summaries are normally written (can be implied first
person, no "I"). Keep it ATS-friendly: plain text, no special characters.

Respond with ONLY the summary text, no preamble, no quotes, no markdown.

Candidate data:
---
{data_json}
---"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def mock_quick_draft(job_title, experience_level):
    """Free fallback: generates a rough starter draft to edit, no real AI cost."""
    return {
        "summary": f"{experience_level} {job_title} with a track record of delivering results. (Mock mode: generic placeholder — edit this or switch to Real AI mode for a tailored draft.)",
        "skills": ["Communication", "Problem Solving", "Team Leadership", "Time Management"],
        "sample_experience": {
            "title": job_title,
            "bullets": [
                "Add your company name and dates above, then describe what you did here.",
                "(Mock mode: this is placeholder text, not AI-written content.)",
            ],
        },
    }


def ai_quick_draft(job_title, experience_level, client):
    """Real AI: generates a full starter draft (summary, likely skills, and a
    sample experience entry with realistic bullet points) from just a job
    title and experience level — solves the 'blank page' problem. The user
    edits every section afterward; nothing here claims to be their real
    history until they confirm it."""
    prompt = f"""A job seeker is starting a resume from scratch. All they've told us is:
- Target job title: {job_title}
- Experience level: {experience_level}

Generate a REALISTIC STARTING DRAFT for them to edit — not a finished resume. This is a
template to save them from a blank page, not a claim about their real history.

Respond with ONLY valid JSON, no preamble, no markdown fences, using this schema:

{{
  "summary": "a 2-sentence professional summary template for this role/level (generic but well-written, the user will personalize it)",
  "skills": [6-8 commonly expected skills for this job title and level],
  "sample_experience": {{
    "title": "a realistic previous job title one step below or equal to the target",
    "bullets": [3-4 example bullet points typical for this kind of role, written as templates the user should edit with their real numbers/details]
  }}
}}

Make it clear this is a starting template, not invented facts about a specific person."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def mock_ats_check(builder_data):
    """Free, rule-based ATS compatibility check — no AI cost. Checks basic
    structural things known to matter for ATS parsing."""
    checks = []
    score = 0
    max_score = 6

    if builder_data.get("full_name") and builder_data.get("email") and builder_data.get("phone"):
        checks.append({"label": "Contact information complete", "status": "pass", "note": "Name, email, and phone are all present."})
        score += 1
    else:
        checks.append({"label": "Contact information complete", "status": "fail", "note": "Add your name, email, and phone number."})

    if builder_data.get("summary"):
        checks.append({"label": "Professional summary present", "status": "pass", "note": "A summary helps both ATS and recruiters quickly understand your fit."})
        score += 1
    else:
        checks.append({"label": "Professional summary present", "status": "warning", "note": "Generate an AI summary — resumes without one are less likely to stand out."})

    skills = builder_data.get("skills", [])
    if len(skills) >= 5:
        checks.append({"label": "Skills section strength", "status": "pass", "note": f"{len(skills)} skills listed — good keyword coverage."})
        score += 1
    elif skills:
        checks.append({"label": "Skills section strength", "status": "warning", "note": f"Only {len(skills)} skills listed. Add more relevant keywords from your target job."})
    else:
        checks.append({"label": "Skills section strength", "status": "fail", "note": "No skills listed yet."})

    experience = builder_data.get("experience", [])
    if experience and all(len(e.get("bullets", [])) >= 2 for e in experience):
        checks.append({"label": "Work experience has detail", "status": "pass", "note": "Each role has multiple bullet points."})
        score += 1
    elif experience:
        checks.append({"label": "Work experience has detail", "status": "warning", "note": "Some roles have very few bullet points. Use the AI bullet generator to add more detail."})
    else:
        checks.append({"label": "Work experience has detail", "status": "fail", "note": "No work experience added yet."})

    total_bullet_words = sum(len(b.split()) for e in experience for b in e.get("bullets", []))
    total_bullets = sum(len(e.get("bullets", [])) for e in experience)
    avg_len = (total_bullet_words / total_bullets) if total_bullets else 0
    if 0 < avg_len <= 20:
        checks.append({"label": "Bullet points are concise", "status": "pass", "note": "Bullets are an ATS- and recruiter-friendly length."})
        score += 1
    elif total_bullets:
        checks.append({"label": "Bullet points are concise", "status": "warning", "note": "Some bullets may be too long. Aim for under ~20 words each."})
    else:
        checks.append({"label": "Bullet points are concise", "status": "fail", "note": "No bullet points yet."})

    if builder_data.get("education"):
        checks.append({"label": "Education section present", "status": "pass", "note": "Education is listed."})
        score += 1
    else:
        checks.append({"label": "Education section present", "status": "warning", "note": "Add your education, even if it's your highest level of study."})

    return {
        "score": round((score / max_score) * 100),
        "checks": checks,
        "note": "(Mock mode: rule-based structural check only. Real AI mode can also review wording quality and keyword relevance to a specific job.)",
    }


def ai_ats_check(builder_data, client):
    """Real AI: reviews the resume for both structural ATS-friendliness and
    wording quality, the way a resume checker like Enhancv or Jobscan would."""
    data_json = json.dumps(builder_data, indent=2)
    prompt = f"""You are an ATS (Applicant Tracking System) resume checker, similar to tools
like Jobscan or Enhancv's resume checker. Review this resume data for both structural
ATS-friendliness AND content quality (clarity, use of action verbs, quantified impact,
generic vs specific language).

Respond with ONLY valid JSON, no preamble, no markdown fences, using this schema:

{{
  "score": <integer 0-100>,
  "checks": [
    {{"label": "short check name", "status": "pass" | "warning" | "fail", "note": "one sentence, specific and actionable"}},
    ... (5-8 checks covering things like: contact info, summary quality, skills relevance,
    bullet point strength/quantification, action verbs, education, overall ATS structure)
  ]
}}

Resume data:
---
{data_json}
---"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
