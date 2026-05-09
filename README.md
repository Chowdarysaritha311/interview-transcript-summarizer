# Interview Transcript Summarizer

A lightweight Python script that reads an interview transcript and uses Google Gemini to produce a structured, recruiter-friendly summary — in a single API call.

---

## What It Does

Given a plain-text interview transcript, the tool outputs three things:

1. **Topics Covered** — every major subject discussed, pulled directly from the transcript
2. **Candidate Profile Fit** — a rated, evidence-based assessment across four dimensions
3. **Candidate Summary** — 3–5 sentences a recruiter can paste straight into a hiring report

It handles technical interviews, behavioral interviews, and mixed-format transcripts without any special configuration.

---

## Project Structure

```
transcript_summarizer/
├── summarizer.py          # Main script
├── prompt_iterations.md   # Prompt development log (3 iterations)
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env                   # Your API key (NOT committed to git)
├── .env.example           # Safe template to commit
└── .gitignore             # Excludes .env, venv/, __pycache__/
```

---

## Setup

### 1. Clone or download the project

```bash
git clone <your-repo-url>
cd transcript_summarizer
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```
google-generativeai>=0.7.0
python-dotenv>=1.0.0
```

### 4. Add your Gemini API key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then open `.env` and fill in your key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

You can get a free Gemini API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

> ⚠️ Never commit your `.env` file to version control. Add it to `.gitignore`.

---

## How to Run

```bash
python summarizer.py <path_to_transcript.txt>
```

### Example

```bash
python summarizer.py interview_jane_smith.txt
```

### Example Output

```
================================================================
  INTERVIEW TRANSCRIPT SUMMARY
  Source: interview_jane_smith.txt
================================================================

----------------------------------------------------------------
TOPICS COVERED
- REST API design and authentication
- JWT token rotation with Redis
- Stateless vs stateful auth trade-offs
- Rate limiting strategies
- Mobile client considerations

CANDIDATE PROFILE FIT
Role Alignment   : Strong — Demonstrated hands-on backend API experience relevant to the role.
Communication    : Strong — Explained trade-offs clearly with concrete reasoning.
Technical Depth  : Strong — Discussed Redis TTL and token rotation unprompted.
Culture Signals  : Positive — Made pragmatic decisions grounded in product requirements.
Overall Fit      : Strong Hire — Shows senior-leaning judgment for a mid-level backend role.

CANDIDATE SUMMARY
The candidate demonstrated solid backend engineering skills with a focus on API security
and authentication architecture. Their unprompted depth on token rotation suggests
production-level experience. No significant gaps were identified within this interview
segment. Communication was clear and appropriately technical. Recommend advancing to a
system design round to evaluate breadth beyond auth-focused topics.
----------------------------------------------------------------

================================================================
```

---

## Model & Provider

| Setting        | Value                  |
|----------------|------------------------|
| Provider       | Google Gemini          |
| Model          | `gemini-1.5-flash`     |
| Temperature    | 0.3 (consistent output)|
| Max tokens     | 1024                   |
| API calls/run  | 1                      |

`gemini-1.5-flash` was chosen for its speed, generous free tier, and strong instruction-following on structured output tasks.

---

## Design Decisions

- **Single API call** — keeps latency low and the implementation easy to follow; no chaining or orchestration needed for this scope
- **Plain-text output over JSON** — optimized for recruiter readability; a hiring manager can read the terminal output or paste it directly without any parsing
- **Temperature set to 0.3** — summarization is an extraction task, not a creative one; lower temperature means more consistent structure across different transcript styles
- **No LangChain or agent frameworks** — the assignment emphasized simplicity, and a direct SDK call is easier to debug, read, and explain in an interview
- **System instruction + user message split** — keeps the behavioral rules (format, fallback language, tone) separate from the actual transcript content, which makes the prompt easier to iterate on
- **Explicit "Insufficient information" fallback** — prevents the model from generating confident-sounding assessments when the transcript doesn't support them

---

## Transcript Format

The script accepts any plain `.txt` file. No special formatting is required. Both of the following work:

**Labeled format:**
```
Interviewer: Tell me about your experience with Python.
Candidate: I've been using it for about three years, mostly for data pipelines...
```

**Unlabeled / conversational format:**
```
So I wanted to start by asking about your background in machine learning.
Yeah, I did my thesis on NLP — specifically named entity recognition using BERT...
```

---

## Limitations

- **No memory across transcripts** — each run is independent; no comparison across candidates
- **Token limit** — very long transcripts (>50,000 characters) may be truncated by the model's context window; consider splitting them
- **No structured JSON export** — output is formatted plain text; a future version could add `--json` flag
- **English only** — prompt and output are in English; non-English transcripts may produce inconsistent results
- **Single API call** — works well for most transcripts, but extremely short transcripts (<200 words) may yield thin assessments

---

## Error Handling

The script handles the following failure cases with readable terminal messages instead of raw stack traces:

- **Missing transcript file** — clear message with the attempted path
- **Empty transcript file** — caught before the API call to avoid wasting quota
- **Missing API key** — explains exactly where to set it (`.env` or shell export)
- **API / network failures** — caught and surfaced without exposing internal details
- **Empty model response** — handles cases where Gemini returns no content (e.g., safety filter triggered)

All errors exit with a non-zero status code, making the script safe to use in shell pipelines or automation scripts.

---

## Reflection

The main challenge in this project wasn't the code — it was the prompt.

My first attempt produced fluffy, ungrounded output ("seems like a solid hire") that looked fine on the surface but was useless for an actual hiring decision. The model was filling in gaps with optimistic filler rather than sticking to the transcript.

The fix was structural: define *exactly* what the output should look like, require ratings with labeled dimensions, and explicitly tell the model to write "Insufficient information" rather than guessing. Once the output format was rigid enough, the model stopped improvising and started extracting.

I also kept temperature low (0.3) to reduce variation between runs. A summarization task isn't creative — consistency matters more than novelty here.

The most important insight was that summarization quality depended less on the model itself and more on constraining the model's behavior through explicit structure and evidence requirements.

If I were taking this further, I'd add a `--json` output mode for ATS integration, test against edge cases (1-minute transcripts, non-native speaker transcripts, heavily redacted content), and explore a second-pass prompt that generates follow-up interview questions based on the gaps identified in the summary.

---

## Future Improvements

- `--json` flag for structured machine-readable output
- Batch mode: summarize a folder of transcripts at once
- `--compare` mode: side-by-side summary of two candidates
- Confidence scoring per dimension
- Auto-detect transcript language and respond accordingly
- Web UI wrapper (Streamlit) for non-technical recruiters
