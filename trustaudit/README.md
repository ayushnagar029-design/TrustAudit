# TrustAudit

Claim-level hallucination detection for AI-generated text.

**Scope (v1):** hallucination detection only, one provider (OpenAI). Bias detection
and the authenticity/deepfake layer are deliberately out of scope for this version —
they're the next phase, after this one is real and tested.

## How it works

1. **Claim decomposition** — the response is broken into atomic, independently
   checkable factual claims (skipping opinions, hedges, greetings).
2. **Claim verification** — each claim is checked one of two ways:
   - **Grounded mode** (source context provided): each claim is checked against the
     source as supported / contradicted / unverifiable — an NLI-style grounding check.
   - **Self-consistency mode** (no source provided): each claim is risk-assessed on
     its own — specific, falsifiable claims (numbers, names, dates) stated with
     unwarranted confidence are flagged as higher-risk than general statements.
3. **Trust score** — an aggregate 0-100 score from the per-claim verdicts, with a
   low/medium/high risk label.

This mirrors the grounding-verification approach used in research tools like
SelfCheckGPT — hallucination is treated as a per-claim problem, not a single
yes/no label slapped on the whole response.

## Project structure

```
trustaudit/
├── backend/          FastAPI service — the detection engine
│   ├── main.py        API routes
│   ├── detector.py     core detection logic
│   ├── models.py        request/response schemas
│   └── requirements.txt
└── frontend/         React + TypeScript + Tailwind UI
    └── src/
```

## Running it locally

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and add your real OPENAI_API_KEY

uvicorn main:app --reload --port 8000
```

Backend will be live at `http://localhost:8000`. Check `http://localhost:8000/docs`
for the interactive API explorer.

### 2. Frontend

In a separate terminal:

```bash
cd frontend
npm install
cp .env.example .env    # only needed if your backend isn't on localhost:8000
npm run dev
```

Frontend will be live at `http://localhost:5173`.

### 3. Use it

1. Open `http://localhost:5173`
2. Paste an AI-generated response into the left panel
3. (Optional but recommended) paste the source document it should be checked
   against — without this, you only get self-consistency risk flags, not real
   verification
4. Click **Run audit**
5. The right panel shows the trust score, the response with claims
   underlined inline by verdict (teal = supported, amber = unverifiable,
   red = contradicted/unsupported), and the full claim-by-claim breakdown

## What's already verified working

- Backend imports and routes are wired correctly
- Trust score and risk-level math is unit-tested (`75% → low risk`,
  `0% → high risk`, etc.)
- Full request/response cycle tested end-to-end (claim decomposition →
  verification → scoring → character-offset location for frontend highlighting)
- Frontend type-checks clean (`tsc --noEmit`) and builds clean for production
  (`npm run build`)

**Not yet tested:** real OpenAI API calls — you'll need to add your own API
key and run it against real model outputs to validate detection accuracy on
real data. That's the next real step, not a "nice to have."

## Honest next steps, in order

1. Add your `OPENAI_API_KEY` and run this against 10-20 real LLM outputs
   you already have — see if the trust scores and verdicts actually match
   your own judgment of what's hallucinated
2. Fix whatever the real testing reveals (prompt tuning, edge cases in
   claim decomposition, etc.) — don't expect this to be perfect on the
   first real run
3. Only after that: consider bias detection or confidence-calibration as
   separate, additional modules — not before
