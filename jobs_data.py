import json
import os
import requests

# Sample job listings — used as a fallback when no real API key is set,
# or if the live API call fails for any reason.
SAMPLE_JOBS = [
    {
        "id": 1,
        "title": "Senior Software Engineer",
        "company": "Systems Ltd",
        "location": "Lahore, Pakistan",
        "description": "Looking for a software engineer with 3+ years experience in React, Node.js, and AWS. Must have experience with PostgreSQL and REST API design. Remote-friendly.",
        "required_skills": ["React", "Node.js", "AWS", "PostgreSQL", "JavaScript"],
        "source": "Rozee.pk",
    },
    {
        "id": 2,
        "title": "Backend Developer",
        "company": "Gulf Tech Solutions",
        "location": "Dubai, UAE",
        "description": "Backend developer needed for fintech platform. Strong Python, Django, and PostgreSQL required. Docker and Kubernetes experience is a plus.",
        "required_skills": ["Python", "Django", "PostgreSQL", "Docker", "Kubernetes"],
        "source": "Bayt.com",
    },
    {
        "id": 3,
        "title": "Frontend Engineer",
        "company": "Retail Innovations",
        "location": "Riyadh, Saudi Arabia",
        "description": "React and TypeScript expert needed to build e-commerce interfaces. Experience with Tailwind CSS and state management preferred.",
        "required_skills": ["React", "TypeScript", "CSS", "JavaScript"],
        "source": "Naukrigulf",
    },
    {
        "id": 4,
        "title": "Data Analyst",
        "company": "FinCorp",
        "location": "Karachi, Pakistan",
        "description": "Analyze sales and marketing data. Strong Excel and SQL skills required. Python experience is a bonus for automation tasks.",
        "required_skills": ["SQL", "Excel", "Python"],
        "source": "Rozee.pk",
    },
    {
        "id": 5,
        "title": "DevOps Engineer",
        "company": "CloudFirst Gulf",
        "location": "Abu Dhabi, UAE",
        "description": "DevOps engineer to manage CI/CD pipelines, AWS infrastructure, and Docker/Kubernetes deployments. 2+ years experience required.",
        "required_skills": ["AWS", "Docker", "Kubernetes", "Git"],
        "source": "Bayt.com",
    },
    {
        "id": 6,
        "title": "Full Stack Developer",
        "company": "StartupHub",
        "location": "Islamabad, Pakistan",
        "description": "Full stack role building web apps end-to-end. React frontend, Node.js/Express backend, MongoDB database. Startup environment, fast-paced.",
        "required_skills": ["React", "Node.js", "MongoDB", "JavaScript"],
        "source": "Rozee.pk",
    },
    {
        "id": 7,
        "title": "Accountant",
        "company": "Gulf Finance Group",
        "location": "Doha, Qatar",
        "description": "Certified accountant needed for month-end close, reporting, and audits. Strong Excel skills and 3+ years experience required.",
        "required_skills": ["Excel", "Accounting"],
        "source": "Naukrigulf",
    },
    {
        "id": 8,
        "title": "Marketing Executive",
        "company": "Brandworks",
        "location": "Lahore, Pakistan",
        "description": "Digital marketing executive to run campaigns across social media and email. Experience with analytics tools and content strategy required.",
        "required_skills": ["Marketing", "Communication"],
        "source": "Rozee.pk",
    },
    {
        "id": 9,
        "title": "Java Backend Developer",
        "company": "Enterprise Systems KSA",
        "location": "Jeddah, Saudi Arabia",
        "description": "Java developer for enterprise banking systems. Spring Boot, SQL, and microservices architecture experience required. 4+ years experience.",
        "required_skills": ["Java", "SQL"],
        "source": "Bayt.com",
    },
    {
        "id": 10,
        "title": "Project Manager - IT",
        "company": "TechBridge",
        "location": "Dubai, UAE",
        "description": "IT project manager to lead cross-functional teams delivering software projects. PMP certification preferred, strong communication and stakeholder management skills required.",
        "required_skills": ["Project Management", "Communication"],
        "source": "Naukrigulf",
    },
]


RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
JSEARCH_HOST = "jsearch.p.rapidapi.com"

# Countries in our target market. JSearch uses ISO country codes.
TARGET_COUNTRIES = ["pk", "ae", "sa", "qa", "om"]


def fetch_real_jobs(query="software engineer", country="pk", num_pages=1):
    """Fetch live job listings from the JSearch API (covers LinkedIn, Indeed,
    Glassdoor, Bayt, and more). Returns a list of jobs in our standard format,
    or an empty list if the API call fails."""
    if not RAPIDAPI_KEY:
        return []

    url = f"https://{JSEARCH_HOST}/search-v2"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST,
    }
    params = {
        "query": query,
        "country": country,
        "num_pages": str(num_pages),
        "date_posted": "all",
    }

    try:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.exceptions.Timeout:
            print("[JSearch API] First attempt timed out, retrying once...")
            response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"[JSearch API] Status code: {response.status_code}")
        print(f"[JSearch API] Raw response (first 500 chars): {response.text[:500]}")
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[JSearch API] Failed to fetch jobs: {e}")
        return []

    jobs = []
    job_list = data.get("data", {})
    if isinstance(job_list, dict):
        job_list = job_list.get("jobs", [])

    for i, item in enumerate(job_list):
        jobs.append({
            "id": item.get("job_id", str(i)),
            "title": item.get("job_title", "Unknown title"),
            "company": item.get("employer_name", "Unknown company"),
            "location": item.get("job_city") or item.get("job_country", "Unknown location"),
            "description": (item.get("job_description") or "")[:800],
            "required_skills": item.get("job_required_skills") or [],
            "source": item.get("job_publisher", "JSearch"),
            "apply_link": item.get("job_apply_link", ""),
        })
    return jobs


def load_sample_jobs(query="software engineer", country="pk"):
    """Returns real jobs if RAPIDAPI_KEY is set and the API call succeeds,
    otherwise falls back to static sample jobs (useful for free testing)."""
    if RAPIDAPI_KEY:
        real_jobs = fetch_real_jobs(query=query, country=country)
        if real_jobs:
            return real_jobs
        print("[JSearch API] No real jobs returned, falling back to sample jobs.")
    return SAMPLE_JOBS


if __name__ == "__main__":
    print(json.dumps(load_sample_jobs(), indent=2))
