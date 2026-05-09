# Interview Transcript Summarizer

A command-line tool that takes an interview transcript and produces a structured hiring summary using the Google Gemini API (free).

---

## How to Run

### 1. Install dependencies

```bash
pip install google-generativeai python-dotenv
```

### 2. Get a free API key

1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **"Get API key"** in the left sidebar → **"Create API key"**
4. Copy the key (looks like `AIza...`)

### 3. Set your API key

Create a `.env` file in the project folder:

```
GEMINI_API_KEY=AIza_your_key_here
```

> Never commit this file. It is listed in `.gitignore`.

### 4. Run the script

```bash
# Print summary to terminal
python summarizer.py sample_transcript_assignment_1.txt

# Write summary to a file
python summarizer.py sample_transcript_assignment_1.txt --output summary_1.md

# Run on second transcript
python summarizer.py sample_transcript_assignment_2.txt
```

### Arguments

| Argument | Description |
|---|---|
| `transcript_file` | Path to the `.txt` transcript file (required) |
| `--output` / `-o` | File path to write the summary (optional; default: stdout) |
| `--model` / `-m` | Gemini model name (default: `gemini-2.0-flash`) |

---

## LLM Provider and Model

- **Provider:** Google AI Studio (free tier)
- **Model:** `gemini-2.0-flash`

---

## Reflection

### What surprised me

The biggest surprise was how much a single **negative example** in the prompt improved output quality. Adding "avoid filler phrases like 'the candidate showed strong potential'" produced noticeably more specific, grounded language — the model generalized from one example to the whole class of vague commentary without me needing to list every phrase to avoid.

The transcript delimiters (`---TRANSCRIPT START---`) also helped more than expected on longer inputs — the model was less likely to confuse transcript content with prompt instructions.

### What I'd improve with another day

1. **Short-transcript handling.** The prompt asks for 3–6 sentences and 4–8 bullets regardless of transcript length. A very short transcript can't justify that volume. I'd detect word count before calling the API and adjust instructions accordingly.

2. **Confidence signals.** The model produces equally assertive output whether the transcript is rich or thin. I'd add an instruction to rate confidence on the profile section (Low / Medium / High), so hiring managers know when to treat the assessment with more skepticism.

3. **Batch mode.** For real recruiting workflows, you'd want to run this over a folder of transcripts and produce a comparison table. I'd add a `--batch` flag that accepts a directory and appends all outputs to a single markdown file.

### Limitations of the final prompt

- **Role coverage is limited.** Tested on a technical and a product management transcript only. May produce odd output for design, sales, or executive roles.
- **No hallucination guard.** The "base assessments on what is said" instruction reduces inference but doesn't eliminate it. A production version would benefit from a verification step.
- **Single API call.** A multi-step approach (extract quotes first, then summarize) might produce more grounded summaries for very long or noisy transcripts.
