"""
Pydantic schemas for TrustAudit's hallucination detection API.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    response_text: str = Field(..., min_length=1, description="The AI-generated response to audit")
    source_context: Optional[str] = Field(
        None, description="Ground-truth source text to verify claims against. If omitted, self-consistency mode is used."
    )
    prompt: Optional[str] = Field(None, description="The original prompt that produced the response, for context only")


ClaimVerdict = Literal["supported", "unsupported", "contradicted", "unverifiable"]


class Claim(BaseModel):
    text: str
    verdict: ClaimVerdict
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model's confidence in this verdict")
    reasoning: str
    start_index: Optional[int] = Field(None, description="Character offset of claim in response_text, for highlighting")
    end_index: Optional[int] = None


class AnalyzeResponse(BaseModel):
    response_text: str
    mode: Literal["grounded", "self_consistency"]
    claims: List[Claim]
    trust_score: float = Field(..., ge=0.0, le=100.0, description="0 = fully fabricated, 100 = fully grounded")
    risk_level: Literal["low", "medium", "high"]
    summary: str
