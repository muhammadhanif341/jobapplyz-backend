def mock_generate_cover_letter(resume_data, job):
    """Free, template-based cover letter — no AI, just fills in placeholders.
    Rougher than real AI but works with zero API cost."""
    name = resume_data.get("full_name") or "Applicant"
    skills = resume_data.get("skills", [])
    matched = [s for s in job.get("required_skills", []) if s.lower() in [x.lower() for x in skills]]
    skills_line = ", ".join(matched) if matched else ", ".join(skills[:3])

    letter = f"""Dear Hiring Manager,

I am writing to express my interest in the {job['title']} position at {job['company']}. \
With hands-on experience in {skills_line}, I believe I would be a strong fit for this role.

{resume_data.get('summary', 'I bring relevant experience and a strong work ethic to every project I take on.')}

I would welcome the opportunity to discuss how my background aligns with your team's needs.

Sincerely,
{name}

(Mock mode: this is a basic template, not real AI writing. Switch to Real AI mode for a genuinely tailored letter.)"""
    return letter


def ai_generate_cover_letter(resume_data, job, client):
    """Real AI-written cover letter, tailored to the specific job description."""
    import json
    resume_summary = json.dumps(resume_data, indent=2)

    prompt = f"""Write a concise, professional cover letter (150-200 words) for this candidate
applying to this specific job. Reference their actual relevant skills and experience from
the resume data, and connect them directly to what the job description asks for. Do not
invent facts not present in the resume data. Write in a natural, non-generic tone — avoid
cliches like "I am excited to apply". Sign off with the candidate's name if available,
otherwise "Sincerely, [Your Name]".

Respond with ONLY the cover letter text, no preamble, no markdown, no explanation.

Candidate resume data:
---
{resume_summary}
---

Job:
Title: {job['title']}
Company: {job['company']}
Description: {job['description']}
---"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
