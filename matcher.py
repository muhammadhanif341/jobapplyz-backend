import json


def mock_match_jobs(resume_data, jobs):
    """Free, no-API matching based on simple skill overlap counting.
    Less smart than AI matching (no context understanding) but works
    with zero cost — useful while testing without API credits."""
    resume_skills = set(s.lower() for s in resume_data.get("skills", []))

    results = []
    for job in jobs:
        required = set(s.lower() for s in job.get("required_skills", []))
        if not required:
            score = 0
        else:
            overlap = resume_skills & required
            score = round(len(overlap) / len(required) * 100)

        matched_skills = [s for s in job["required_skills"] if s.lower() in resume_skills]
        results.append({
            **job,
            "match_score": score,
            "matched_skills": matched_skills,
            "match_reason": f"Matched {len(matched_skills)} of {len(job['required_skills'])} required skills." if matched_skills else "No overlapping skills found.",
        })

    results.sort(key=lambda j: j["match_score"], reverse=True)
    return results


def ai_match_jobs(resume_data, jobs, client):
    """Real AI matching using Claude — understands context, not just
    keyword overlap. Costs API tokens per call."""
    resume_summary = json.dumps(resume_data, indent=2)
    jobs_summary = json.dumps(jobs, indent=2)

    prompt = f"""You are a job-matching assistant. Given a candidate's parsed resume data
and a list of job listings, score how well the candidate matches EACH job from 0-100,
and give a one-sentence reason for each score. Consider skills overlap, job title
relevance, and experience level — not just exact keyword matches.

Respond with ONLY valid JSON, no preamble, no markdown fences. Use this exact schema —
an array with one object per job, in the same order as the input jobs list:

[
  {{
    "id": <job id, matching the input>,
    "match_score": <integer 0-100>,
    "match_reason": "<one sentence explaining the score>"
  }},
  ...
]

Candidate resume data:
---
{resume_summary}
---

Job listings:
---
{jobs_summary}
---"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    scores = json.loads(raw)

    score_map = {s["id"]: s for s in scores}
    results = []
    for job in jobs:
        score_info = score_map.get(job["id"], {"match_score": 0, "match_reason": "Not scored."})
        results.append({
            **job,
            "match_score": score_info["match_score"],
            "match_reason": score_info["match_reason"],
        })

    results.sort(key=lambda j: j["match_score"], reverse=True)
    return results
