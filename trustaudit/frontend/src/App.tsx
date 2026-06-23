import { useState } from "react";
import { analyze } from "./api";
import type { AnalyzeResponse, Claim } from "./types";

const VERDICT_CONFIG = {
  supported: {
    label: "Supported",
    color: "text-verified",
    border: "border-verified/30",
    bg: "bg-verified/5",
    dot: "bg-verified",
    underline: "#4FD1C5",
    highlight: "rgba(79,209,197,0.12)",
  },
  unverifiable: {
    label: "Unverifiable",
    color: "text-flagged",
    border: "border-flagged/30",
    bg: "bg-flagged/5",
    dot: "bg-flagged",
    underline: "#F0A857",
    highlight: "rgba(240,168,87,0.12)",
  },
  unsupported: {
    label: "Unsupported",
    color: "text-critical",
    border: "border-critical/30",
    bg: "bg-critical/5",
    dot: "bg-critical",
    underline: "#E8675A",
    highlight: "rgba(232,103,90,0.12)",
  },
  contradicted: {
    label: "Contradicted",
    color: "text-critical",
    border: "border-critical/30",
    bg: "bg-critical/5",
    dot: "bg-critical",
    underline: "#E8675A",
    highlight: "rgba(232,103,90,0.12)",
  },
};

interface Segment {
  text: string;
  claim: Claim | null;
}

function buildSegments(responseText: string, claims: Claim[]): Segment[] {
  const located = claims
    .filter((c) => c.start_index !== null && c.end_index !== null)
    .sort((a, b) => (a.start_index ?? 0) - (b.start_index ?? 0));
  const segments: Segment[] = [];
  let cursor = 0;
  for (const claim of located) {
    const start = claim.start_index as number;
    const end = claim.end_index as number;
    if (start < cursor) continue;
    if (start > cursor) segments.push({ text: responseText.slice(cursor, start), claim: null });
    segments.push({ text: responseText.slice(start, end), claim });
    cursor = end;
  }
  if (cursor < responseText.length) segments.push({ text: responseText.slice(cursor), claim: null });
  return segments;
}

function ScoreRing({ score, risk }: { score: number; risk: string }) {
  const r = 54;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = risk === "low" ? "#4FD1C5" : risk === "medium" ? "#F0A857" : "#E8675A";
  const label = risk === "low" ? "Grounded" : risk === "medium" ? "Mixed" : "High Risk";

  return (
    <div className="flex items-center gap-6">
      <div className="relative w-32 h-32 shrink-0">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 128 128">
          <circle cx="64" cy="64" r={r} fill="none" stroke="#222D42" strokeWidth="10" />
          <circle
            cx="64" cy="64" r={r} fill="none"
            stroke={color} strokeWidth="10"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-3xl font-bold" style={{ color }}>{score.toFixed(0)}</span>
          <span className="text-muted text-xs font-mono">/100</span>
        </div>
      </div>
      <div>
        <div className="font-display text-xl font-semibold text-paper mb-1" style={{ color }}>{label}</div>
        <div className="text-sm text-muted font-mono">Trust Score</div>
        <div className="flex gap-3 mt-3">
          {[
            { v: "supported", label: "Grounded", color: "#4FD1C5" },
            { v: "unverifiable", label: "Uncertain", color: "#F0A857" },
            { v: "contradicted", label: "Flagged", color: "#E8675A" },
          ].map((item) => (
            <div key={item.v} className="flex items-center gap-1.5">
              <div className="h-2 w-2 rounded-full" style={{ background: item.color }} />
              <span className="text-xs text-muted font-mono">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [responseText, setResponseText] = useState("");
  const [sourceContext, setSourceContext] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [activeClaim, setActiveClaim] = useState<Claim | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAudit() {
    if (!responseText.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setActiveClaim(null);
    try {
      const res = await analyze({ response_text: responseText, source_context: sourceContext.trim() || undefined });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Audit failed.");
    } finally {
      setLoading(false);
    }
  }

  const segments = result ? buildSegments(result.response_text, result.claims) : [];

  const counts = result ? {
    supported: result.claims.filter(c => c.verdict === "supported").length,
    flagged: result.claims.filter(c => ["contradicted", "unsupported"].includes(c.verdict)).length,
    uncertain: result.claims.filter(c => c.verdict === "unverifiable").length,
  } : null;

  return (
    <div className="min-h-screen bg-ink font-body">
      {/* Header */}
      <header className="border-b border-ink-line px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-verified/15 border border-verified/20 flex items-center justify-center">
            <div className="h-2.5 w-2.5 rounded-full bg-verified" />
          </div>
          <div>
            <span className="font-display text-base font-semibold text-paper tracking-tight">TrustAudit</span>
            <span className="text-muted text-sm font-mono ml-2 opacity-60">v0.1</span>
          </div>
        </div>
        <div className="text-xs font-mono text-muted/50 hidden md:block">
          AI Hallucination Detection Engine
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

          {/* Left panel — Input */}
          <div className="lg:col-span-2 flex flex-col gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-mono text-muted uppercase tracking-widest">01</span>
                <label className="text-xs font-display font-medium text-paper uppercase tracking-wide">AI Response</label>
              </div>
              <textarea
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                placeholder="Paste the AI-generated text you want to audit..."
                rows={10}
                className="w-full bg-ink-surface border border-ink-line rounded-xl p-4 font-mono text-sm text-paper placeholder:text-muted/40 focus:border-verified/40 focus:bg-ink-surface outline-none resize-none transition-all"
              />
            </div>

            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-mono text-muted uppercase tracking-widest">02</span>
                <label className="text-xs font-display font-medium text-paper uppercase tracking-wide">Source Context</label>
                <span className="text-xs text-muted/50 font-mono normal-case ml-1">optional</span>
              </div>
              <textarea
                value={sourceContext}
                onChange={(e) => setSourceContext(e.target.value)}
                placeholder="Paste a reference document to enable grounded verification. Without this, risk-based assessment is used."
                rows={5}
                className="w-full bg-ink-surface border border-ink-line rounded-xl p-4 font-mono text-sm text-paper placeholder:text-muted/40 focus:border-verified/40 outline-none resize-none transition-all"
              />
            </div>

            <button
              onClick={handleAudit}
              disabled={loading || !responseText.trim()}
              className="w-full font-display font-semibold text-sm bg-verified text-ink py-3 rounded-xl hover:bg-verified/90 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="h-3.5 w-3.5 border-2 border-ink/30 border-t-ink rounded-full animate-spin" />
                  Analysing claims...
                </span>
              ) : "Run Audit"}
            </button>

            {error && (
              <div className="text-xs text-critical font-mono bg-critical/10 border border-critical/20 rounded-xl p-3 leading-relaxed">
                {error}
              </div>
            )}

            {/* Legend */}
            <div className="bg-ink-surface border border-ink-line rounded-xl p-4 mt-2">
              <div className="text-xs font-mono text-muted uppercase tracking-widest mb-3">Legend</div>
              <div className="flex flex-col gap-2">
                {[
                  { color: "#4FD1C5", label: "Supported", desc: "Claim verified as accurate" },
                  { color: "#F0A857", label: "Unverifiable", desc: "Cannot be confirmed without source" },
                  { color: "#E8675A", label: "Contradicted", desc: "Claim conflicts with known facts" },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-3">
                    <div className="h-1 w-6 rounded-full shrink-0" style={{ background: item.color }} />
                    <span className="text-xs font-mono" style={{ color: item.color }}>{item.label}</span>
                    <span className="text-xs text-muted/60">{item.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right panel — Results */}
          <div className="lg:col-span-3 flex flex-col gap-4">
            {!result && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-24 border border-ink-line rounded-xl border-dashed">
                <div className="h-12 w-12 rounded-full bg-ink-surface border border-ink-line flex items-center justify-center mb-4">
                  <div className="h-3 w-3 rounded-full bg-muted/30" />
                </div>
                <p className="text-muted text-sm font-mono">No audit run yet.</p>
                <p className="text-muted/50 text-xs font-mono mt-1">Paste a response and click Run Audit.</p>
              </div>
            )}

            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center py-24 border border-ink-line rounded-xl">
                <div className="h-8 w-8 border-2 border-ink-line border-t-verified rounded-full animate-spin mb-4" />
                <p className="text-muted text-sm font-mono animate-pulse">Decomposing claims...</p>
              </div>
            )}

            {result && (
              <>
                {/* Score card */}
                <div className="bg-ink-surface border border-ink-line rounded-xl p-6">
                  <ScoreRing score={result.trust_score} risk={result.risk_level} />

                  {/* Stat pills */}
                  {counts && (
                    <div className="flex gap-2 mt-5 pt-5 border-t border-ink-line">
                      <div className="flex-1 bg-verified/10 border border-verified/20 rounded-lg px-3 py-2 text-center">
                        <div className="font-display text-xl font-bold text-verified">{counts.supported}</div>
                        <div className="text-xs text-muted font-mono mt-0.5">Supported</div>
                      </div>
                      <div className="flex-1 bg-flagged/10 border border-flagged/20 rounded-lg px-3 py-2 text-center">
                        <div className="font-display text-xl font-bold text-flagged">{counts.uncertain}</div>
                        <div className="text-xs text-muted font-mono mt-0.5">Uncertain</div>
                      </div>
                      <div className="flex-1 bg-critical/10 border border-critical/20 rounded-lg px-3 py-2 text-center">
                        <div className="font-display text-xl font-bold text-critical">{counts.flagged}</div>
                        <div className="text-xs text-muted font-mono mt-0.5">Flagged</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Annotated text */}
                <div className="bg-ink-surface border border-ink-line rounded-xl p-5">
                  <div className="text-xs font-mono text-muted uppercase tracking-widest mb-3">Annotated Response</div>
                  <p className="font-mono text-sm text-paper/90 leading-8 whitespace-pre-wrap">
                    {segments.map((seg, i) => {
                      if (!seg.claim) return <span key={i}>{seg.text}</span>;
                      const cfg = VERDICT_CONFIG[seg.claim.verdict];
                      const isActive = activeClaim === seg.claim;
                      return (
                        <span
                          key={i}
                          onMouseEnter={() => setActiveClaim(seg.claim)}
                          onMouseLeave={() => setActiveClaim(null)}
                          style={{
                            borderBottom: `2px solid ${cfg.underline}`,
                            backgroundColor: isActive ? cfg.highlight : "transparent",
                            paddingBottom: "1px",
                            borderRadius: "2px",
                            cursor: "help",
                            transition: "background-color 0.15s ease",
                          }}
                        >
                          {seg.text}
                        </span>
                      );
                    })}
                  </p>
                </div>

                {/* Claim breakdown */}
                {result.claims.length > 0 && (
                  <div className="bg-ink-surface border border-ink-line rounded-xl p-5">
                    <div className="text-xs font-mono text-muted uppercase tracking-widest mb-3">
                      Claim Breakdown <span className="text-muted/50">({result.claims.length})</span>
                    </div>
                    <div className="flex flex-col gap-2">
                      {result.claims.map((claim, i) => {
                        const cfg = VERDICT_CONFIG[claim.verdict];
                        const isActive = activeClaim === claim;
                        return (
                          <div
                            key={i}
                            onMouseEnter={() => setActiveClaim(claim)}
                            onMouseLeave={() => setActiveClaim(null)}
                            className={`rounded-lg border p-3.5 transition-all cursor-default ${cfg.border} ${isActive ? cfg.bg : "border-transparent hover:" + cfg.bg}`}
                          >
                            <div className="flex items-center justify-between mb-1.5">
                              <div className="flex items-center gap-2">
                                <div className={`h-1.5 w-1.5 rounded-full shrink-0 ${cfg.dot}`} />
                                <span className={`text-xs font-display font-semibold uppercase tracking-wider ${cfg.color}`}>
                                  {cfg.label}
                                </span>
                              </div>
                              <span className="text-xs font-mono text-muted/60">
                                {(claim.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                            <p className="font-mono text-sm text-paper/90 mb-1.5 leading-relaxed">{claim.text}</p>
                            <p className="text-xs text-muted leading-relaxed">{claim.reasoning}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}