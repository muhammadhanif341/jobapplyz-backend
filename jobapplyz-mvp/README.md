# JobApplyz — Phase 1: Resume Upload + AI Parsing

This is the first working piece of the JobApplyz MVP. It lets a user upload a
resume (PDF or .txt) and uses Claude (Anthropic's AI) to extract structured
data: name, skills, job titles, years of experience, education, and a
professional summary.

## What you need before running this

**Option A — Free, no API credits needed (Mock Mode):**
Skip the Anthropic API key entirely. This uses simple keyword-matching instead
of real AI, so it's less accurate, but it lets you test the full app for $0.

**Option B — Real AI parsing (needs API credits):**
1. **Python 3.10+** installed on your computer.
2. **An Anthropic API key.** Get one free at https://console.anthropic.com
   (sign up, verify your phone number, claim the one-time $5 free trial
   credit from the Dashboard, then go to "API Keys" and create a new key).

## Setup steps

1. Open a terminal in this folder (`jobapplyz-mvp`).

2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   # Mac/Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Choose your mode:

   **Mock Mode (free, no API key needed):**
   ```
   # Mac/Linux:
   export MOCK_MODE=true
   # Windows (cmd):
   set MOCK_MODE=true
   # Windows (PowerShell):
   $env:MOCK_MODE="true"
   ```

   **Real AI Mode (needs API key + credits):**
   ```
   # Mac/Linux:
   export ANTHROPIC_API_KEY=your_key_here
   # Windows (cmd):
   set ANTHROPIC_API_KEY=your_key_here
   # Windows (PowerShell):
   $env:ANTHROPIC_API_KEY="your_key_here"
   ```
   (Leave MOCK_MODE unset or set it to false for this mode.)

5. Run the app:
   ```
   python app.py
   ```

6. Open your browser and go to: **http://localhost:5000**

7. Upload `sample_resume.txt` (included in this folder) to test it, or use
   your own resume (PDF or .txt).

Note: Mock Mode results are much rougher than real AI — it only catches
common skill keywords and can't infer job titles, education, or years of
experience. It's meant purely for testing the upload/display flow while you
don't have API credits. Switch to Real AI Mode once you can add credits.

## What this does NOT do yet (upcoming phases)

- Does not fetch real job listings yet (Phase 2)
- Does not generate tailored cover letters yet (Phase 2)
- Does not autofill or auto-apply to jobs yet (Phase 3 and 4)

This is just the foundation: turning a messy resume into clean, structured
data that later phases will use for matching and applying.

## Files in this folder

- `app.py` — the Flask backend (upload handling + AI parsing logic)
- `templates/index.html` — the simple upload page you'll see in the browser
- `sample_resume.txt` — a test resume you can use right away
- `requirements.txt` — Python packages needed
