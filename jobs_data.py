import json

# Sample job listings — realistic but static data for testing the matching
# engine before we plug in real scraping from Rozee.pk, Bayt, etc.

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


def load_sample_jobs():
    return SAMPLE_JOBS


if __name__ == "__main__":
    print(json.dumps(SAMPLE_JOBS, indent=2))
