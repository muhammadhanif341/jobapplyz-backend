def mock_tailor_resume(resume_data, job):
    """Free, template-based resume tailoring — highlights matching skills
    and reorders them by relevance to this specific job. No AI cost."""
    skills = resume_data.get("skills", [])
    required = [s.lower() for s in job.get("required_skills", [])]
    description = (job.get("description") or "").lower()

    # Push skills that are relevant to this job to the top
    relevant = [s for s in skills if s.lower() in required or s.lower() in description]
    other = [s for s in skills if s not in relevant]
    reordered_skills = relevant + other

    summary = resume_data.get("summary", "").replace("(Mock mode:", "").split(")")[0].strip()
    tailored_summary = (
        f"{resume_data.get('full_name', 'Candidate')} — {resume_data.get('job_titles', ['Professional'])[0] if resume_data.get('job_titles') else 'Professional'} "
        f"applying for {job.get('title', 'this role')} at {job.get('company', 'this company')}. "
        f"Key relevant skills: {', '.join(relevant[:5]) if relevant else ', '.join(skills[:5])}."
    )

    return {
        "tailored_summary": tailored_summary,
        "reordered_skills": reordered_skills,
        "highlighted_skills": relevant,
        "note": "(Mock mode: skills reordered by keyword relevance, not real AI rewriting. Switch to Real AI mode for genuinely rewritten bullet points.)",
    }


def ai_tailor_resume(resume_data, job, client):
    """Real AI-powered resume tailoring — rewrites the summary and reorders/
    reframes skills and experience to match this specific job description."""
    import json
    resume_summary = json.dumps(resume_data, indent=2)

    prompt = f"""You are a professional resume writer. Given a candidate's parsed resume data
and a specific job they're applying to, produce a TAILORED version of their resume content
for this job — without inventing any facts not present in the original resume data.

Respond with ONLY valid JSON, no preamble, no markdown fences, using this schema:

{{
  "tailored_summary": "a 2-3 sentence professional summary rewritten to emphasize fit for THIS job",
  "reordered_skills": ["skills from the original list, reordered with most relevant to this job first"],
  "highlighted_skills": ["subset of skills that are most directly relevant to this job"],
  "suggested_bullet_points": ["2-4 rewritten resume bullet points that reframe the candidate's real experience toward this job's requirements"]
}}

Candidate resume data:
---
{resume_summary}
---

Job:
Title: {job.get('title')}
Company: {job.get('company')}
Description: {job.get('description')}
---"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
