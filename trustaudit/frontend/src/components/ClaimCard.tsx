import type { Claim } from "../types";

const VERDICT_META: Record<string, { label: string; dot: string; text: string }> = {
  supported: { label: "Supported", dot: "bg-verified", text: "text-verified" },
  unverifiable: { label: "Unverifiable", dot: "bg-flagged", text: "text-flagged" },
  unsupported: { label: "Unsupported", dot: "bg-critical", text: "text-critical" },
  contradicted: { label: "Contradicted", dot: "bg-critical", text: "text-critical" },
};

export default function ClaimCard({ claim, isActive }: { claim: Claim; isActive: boolean }) {
  const meta = VERDICT_META[claim.verdict];

  return (
    <div
      className={`rounded-lg border p-3.5 transition-colors ${
        isActive ? "border-ink-line bg-ink-surface" : "border-transparent"
      }`}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
        <span className={`font-display text-xs font-medium uppercase tracking-wide ${meta.text}`}>
          {meta.label}
        </span>
        <span className="ml-auto text-xs font-mono text-muted">
          {(claim.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>
      <p className="font-mono text-sm text-paper/90 mb-1.5 leading-relaxed">{claim.text}</p>
      <p className="text-sm text-muted leading-relaxed">{claim.reasoning}</p>
    </div>
  );
}
