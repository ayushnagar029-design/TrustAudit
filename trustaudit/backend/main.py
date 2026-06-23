"""
TrustAudit API — hallucination detection for AI-generated text.

Run locally:
    uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse
import detector

app = FastAPI(
    title="TrustAudit API",
    description="Claim-level hallucination detection for AI-generated responses.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        return detector.analyze(req.response_text, req.source_context)
    except RuntimeError as e:
        # missing API key, etc.
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {e}")
