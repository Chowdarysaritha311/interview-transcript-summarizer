"""
summarizer.py
-------------
Interview Transcript Summarizer using Google Gemini API.

Usage:
    python summarizer.py <path_to_transcript.txt>

Example:
    python summarizer.py interview_john_doe.txt

Outputs:
    - Topics Covered
    - Candidate Profile Fit
    - Candidate Summary
"""

import sys
import os
import textwrap
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ── Configuration ──────────────────────────────────────────────────────────────

MODEL_NAME = "gemini-1.5-flash"   # Fast, capable, free-tier friendly
MAX_OUTPUT_TOKENS = 1024


# ── Prompt ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert technical recruiter assistant. Your job is to read an interview transcript and produce a clean, structured summary that helps a hiring manager make a fast and informed decision.

The interview may be technical, behavioral, or a mix of both. The transcript may be short or long, formal or conversational.

Analyze the transcript carefully and respond using EXACTLY this format — no extra text before or after:

---
TOPICS COVERED
- [List each major topic discussed, one per line. Be specific. E.g., "Python data structures", "Team conflict resolution", "System design trade-offs"]

CANDIDATE PROFILE FIT
Role Alignment   : [Strong / Moderate / Weak] — [1-sentence reason]
Communication    : [Strong / Moderate / Weak] — [1-sentence reason]
Technical Depth  : [Strong / Moderate / Weak] — [1-sentence reason, or "N/A — non-technical interview"]
Culture Signals  : [Positive / Neutral / Concerning] — [1-sentence reason]
Overall Fit      : [Strong Hire / Potential Hire / Not Recommended] — [1-sentence summary]

CANDIDATE SUMMARY
[Write 3–5 sentences. Cover: who the candidate is, what stood out positively, any gaps or red flags, and one concrete hiring recommendation. Write it so a recruiter can paste it directly into a hiring report. Keep it factual and grounded in what was said — do not speculate beyond the transcript.]
---

If a section cannot be determined from the transcript, write "Insufficient information" rather than guessing.
"""


# ── Core Functions ─────────────────────────────────────────────────────────────

def load_transcript(filepath: str) -> str:
    """Read the transcript file and return its contents as a string."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Transcript file not found: '{filepath}'")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"Transcript file is empty: '{filepath}'")

    return content


def build_user_message(transcript: str) -> str:
    """Wrap the transcript in a clear user message for the model."""
    return f"Please summarize the following interview transcript:\n\n{transcript}"


def call_gemini(api_key: str, transcript: str) -> str:
    """
    Send the transcript to Gemini and return the model's raw text response.
    Uses a combined system+user prompt since Gemini Flash handles it well.
    """
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.3,   # Low temp = more consistent, structured output
        ),
        system_instruction=SYSTEM_PROMPT,
    )

    user_message = build_user_message(transcript)
    response = model.generate_content(user_message)

    # Safety check — model may return empty content on safety blocks
    if not response.text:
        raise RuntimeError("Gemini returned an empty response. The transcript may have triggered a safety filter.")

    return response.text.strip()


def print_summary(summary: str, source_file: str) -> None:
    """Print the summary with a clean header and footer."""
    width = 64
    print()
    print("=" * width)
    print(f"  INTERVIEW TRANSCRIPT SUMMARY")
    print(f"  Source: {os.path.basename(source_file)}")
    print("=" * width)
    print()
    # Normalize the separator lines from the model output
    for line in summary.splitlines():
        if line.strip() == "---":
            print("-" * width)
        else:
            print(line)
    print()
    print("=" * width)
    print()


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    # ── 1. Validate CLI argument ───────────────────────────────────────────────
    if len(sys.argv) != 2:
        print("Usage: python summarizer.py <path_to_transcript.txt>")
        sys.exit(1)

    transcript_path = sys.argv[1]

    # ── 2. Load API key ────────────────────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        print("  → Add it to a .env file: GEMINI_API_KEY=your_key_here")
        print("  → Or export it: export GEMINI_API_KEY=your_key_here")
        sys.exit(1)

    # ── 3. Read transcript ─────────────────────────────────────────────────────
    try:
        transcript = load_transcript(transcript_path)
        print(f"\nLoaded transcript: {transcript_path} ({len(transcript)} characters)")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # ── 4. Call Gemini ─────────────────────────────────────────────────────────
    print("Sending to Gemini... ", end="", flush=True)
    try:
        summary = call_gemini(api_key, transcript)
        print("Done.")
    except RuntimeError as e:
        print(f"\nAPI Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error calling Gemini: {e}")
        sys.exit(1)

    # ── 5. Print result ────────────────────────────────────────────────────────
    print_summary(summary, transcript_path)


if __name__ == "__main__":
    main()
