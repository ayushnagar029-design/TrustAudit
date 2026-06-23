export type ClaimVerdict = "supported" | "unsupported" | "contradicted" | "unverifiable";

export interface Claim {
  text: string;
  verdict: ClaimVerdict;
  confidence: number;
  reasoning: string;
  start_index: number | null;
  end_index: number | null;
}

export interface AnalyzeResponse {
  response_text: string;
  mode: "grounded" | "self_consistency";
  claims: Claim[];
  trust_score: number;
  risk_level: "low" | "medium" | "high";
  summary: string;
}

export interface AnalyzeRequest {
  response_text: string;
  source_context?: string;
  prompt?: string;
}
