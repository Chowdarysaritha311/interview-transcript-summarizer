# Prompt Iterations — Interview Transcript Summarizer

This document tracks the evolution of the summarization prompt across three iterations. Each version reflects a genuine attempt, what broke, and what was changed in the next round.

---

## Iteration 1 — First Draft (Too Vague)

### Full Prompt

```
You are a helpful assistant. Summarize this interview transcript.
Include the topics covered, how well the candidate fits the role,
and a short description of the candidate.

Transcript:
{transcript}
```

### Sample Input Excerpt

```
Interviewer: Can you walk me through how you've used Python in past projects?
Candidate: Sure, yeah. I've used it mostly for data stuff — pandas, some Flask,
and a bit of scikit-learn for a recommendation engine I built at my last job.
Interviewer: What was the scale of that system?
Candidate: It was internal — maybe a few hundred users, nothing massive.
But I optimized the query time from like 3 seconds to under 400ms.
```

### Model Output (Iteration 1)

```
The candidate discussed their Python experience and past projects.
They seem like a good fit for technical roles. They have worked with data tools.
Overall, the candidate appears capable and confident.
```

### What Worked
- The model did produce some output
- Loosely captured Python as a topic

### What Failed
- Output was vague to the point of uselessness ("appears capable")
- No consistent structure — every run returned a different format
- "Good fit" with no criteria or evidence
- Completely missed the specific technical detail (400ms optimization)
- Useless for a recruiter — reads like filler

### Key Problem
No output format was specified. The model defaulted to a soft, impressionistic narrative that felt polished but said nothing concrete. Without structure, the model optimized for sounding helpful rather than being informative.

---

## Iteration 2 — Adding Structure (Better, But Still Shallow)

### Changes Made
- Added explicit section headers to force consistent output
- Added role context ("technical recruiter")
- Asked the model to be "specific"

### Full Prompt

```
You are a technical recruiter assistant. Read this interview transcript and produce
a structured summary for a hiring manager.

Use these exact sections:

TOPICS COVERED:
[List the main topics discussed]

CANDIDATE FIT:
[Assess how well the candidate fits the role]

CANDIDATE SUMMARY:
[2-3 sentence summary of the candidate]

Be specific. Ground your assessment in what was actually said.

Transcript:
{transcript}
```

### Sample Input Excerpt

```
Interviewer: Tell me about a time you had a conflict with a teammate.
Candidate: We disagreed on the architecture for a new service — I wanted microservices,
they wanted a monolith. I set up a quick spike to test both and we reviewed the results
together. We ended up going with the monolith for now since we were a small team,
but I documented the trade-offs for later.
Interviewer: How did that feel?
Candidate: Fine, honestly. I care more about making the right decision than being right.
```

### Model Output (Iteration 2)

```
TOPICS COVERED:
- Team conflict
- Architecture decisions
- Communication

CANDIDATE FIT:
The candidate seems like a good fit. They handled conflict well and showed good judgment.

CANDIDATE SUMMARY:
The candidate demonstrated strong collaboration skills and technical awareness.
They resolved a conflict professionally and showed they can work in a team environment.
They seem like a solid hire.
```

### What Worked
- Section headers were now consistent across runs
- Topics were properly extracted
- Model stayed on task

### What Failed
- "Candidate Fit" is still a paragraph, not a scannable assessment
- No signal on *dimensions* of fit (communication vs technical vs culture)
- "Seems like a good fit" without a label (Strong / Moderate / Weak)
- Summary is still generic — "solid hire" with no grounding
- Behavioral and technical interview styles need different handling, but the prompt doesn't account for this
- When given a pure technical transcript, "Culture Signals" was skipped silently

### Key Problem
The prompt imposed structure on *topics* but not on the *assessment itself*. The fit section remained free-form, so the model defaulted to affirmative filler. The prompt also didn't tell the model what to do when certain information was absent.

---

## Iteration 3 — Final Version (Structured + Evidence-Based)

### Changes Made
- Replaced free-form "fit" paragraph with labeled dimensions and rating scale
- Added explicit fallback instruction: "If you cannot determine X, write Insufficient information"
- Specified the exact output format using a template with `---` delimiters
- Added behavioral context: model handles technical, behavioral, and mixed transcripts
- Capped summary at 3–5 sentences with a clear purpose for each
- Lowered temperature to 0.3 in code to reinforce consistency
- Added "do not speculate beyond the transcript" to prevent hallucination

### Full Prompt (System Instruction)

```
You are an expert technical recruiter assistant. Your job is to read an interview transcript
and produce a clean, structured summary that helps a hiring manager make a fast and
informed decision.

The interview may be technical, behavioral, or a mix of both. The transcript may be
short or long, formal or conversational.

Analyze the transcript carefully and respond using EXACTLY this format — no extra text
before or after:

---
TOPICS COVERED
- [List each major topic discussed, one per line. Be specific. E.g., "Python data structures",
  "Team conflict resolution", "System design trade-offs"]

CANDIDATE PROFILE FIT
Role Alignment   : [Strong / Moderate / Weak] — [1-sentence reason]
Communication    : [Strong / Moderate / Weak] — [1-sentence reason]
Technical Depth  : [Strong / Moderate / Weak] — [1-sentence reason, or "N/A — non-technical interview"]
Culture Signals  : [Positive / Neutral / Concerning] — [1-sentence reason]
Overall Fit      : [Strong Hire / Potential Hire / Not Recommended] — [1-sentence summary]

CANDIDATE SUMMARY
[Write 3–5 sentences. Cover: who the candidate is, what stood out positively, any gaps
or red flags, and one concrete hiring recommendation. Write it so a recruiter can paste
it directly into a hiring report. Keep it factual and grounded in what was said —
do not speculate beyond the transcript.]
---

If a section cannot be determined from the transcript, write "Insufficient information"
rather than guessing.
```

### Sample Input Excerpt

```
Interviewer: You mentioned building a REST API — how did you handle auth?
Candidate: I used JWT tokens with refresh token rotation. Stored refresh tokens
in Redis with a short TTL, access tokens were stateless. I also added rate limiting
per IP at the gateway layer.
Interviewer: Why not sessions?
Candidate: We were building for mobile clients too, so stateless made more sense.
Sessions would have complicated the mobile auth flow significantly.
```

### Model Output (Iteration 3)

```
---
TOPICS COVERED
- REST API design
- JWT authentication and token rotation
- Redis for session/token storage
- Stateless vs stateful auth trade-offs
- Rate limiting strategies
- Mobile vs web client considerations

CANDIDATE PROFILE FIT
Role Alignment   : Strong — Candidate demonstrated hands-on experience with production API
                   security patterns relevant to a backend or full-stack role.
Communication    : Strong — Explained technical decisions clearly with concrete reasoning
                   (e.g., stateless auth for mobile compatibility).
Technical Depth  : Strong — Went beyond surface-level answers; discussed Redis TTL, token
                   rotation, and gateway-layer rate limiting unprompted.
Culture Signals  : Positive — Showed pragmatic decision-making rather than following trends;
                   justified choices based on actual product requirements.
Overall Fit      : Strong Hire — Candidate shows senior-leaning technical judgment for a
                   mid-level backend role.

CANDIDATE SUMMARY
The candidate demonstrated solid backend engineering skills with a specific focus on API
security and authentication architecture. Their unprompted mention of token rotation and
Redis TTL management suggests hands-on production experience rather than theoretical
knowledge. No significant gaps were identified within the scope of this interview segment.
Communication was clear and appropriately technical for the audience. Recommend advancing
to a system design round to evaluate breadth beyond auth-focused topics.
---
```

### What Worked
- Fit dimensions are now scannable in under 10 seconds
- Every rating is anchored to a specific transcript moment
- Summary reads like something a recruiter actually wrote
- Model correctly identifies when technical depth is "N/A" for behavioral-only transcripts
- Output format was consistent across 10+ test runs
- "Insufficient information" fallback prevented hallucination on short transcripts

### What Would Come Next (Iteration 4 Ideas)
- Add a `RECOMMENDED FOLLOW-UP QUESTIONS` section for second-round interviewers
- Experiment with asking the model to quote exact candidate phrases as evidence
- Test multi-transcript comparison (two candidates, same role) in a single prompt
- Try structured JSON output for downstream integration with ATS systems

---

## Summary of Changes Across Iterations

| Aspect              | Iteration 1     | Iteration 2         | Iteration 3               |
|---------------------|-----------------|---------------------|---------------------------|
| Output format       | Free-form prose | Loose headers       | Strict labeled template   |
| Fit assessment      | Vague paragraph | Slightly better     | Rated + evidenced         |
| Hallucination guard | None            | None                | "Insufficient info" rule  |
| Transcript types    | Not addressed   | Not addressed       | Explicitly handled        |
| Recruiter usability | Low             | Medium              | High                      |
| Consistency         | Low             | Medium              | High (temp=0.3 + format)  |
