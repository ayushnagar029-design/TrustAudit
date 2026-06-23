import type { Claim } from "../types";

const VERDICT_STYLE: Record<string, { underline: string; bg: string }> = {
  supported: { underline: "decoration-verified", bg: "hover:bg-verified/10" },
  unverifiable: { underline: "decoration-flagged", bg: "hover:bg-flagged/10" },
  unsupported: { underline: "decoration-critical", bg: "hover:bg-critical/10" },
  contradicted: { underline: "decoration-critical", bg: "hover:bg-critical/10" },
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
    if (start < cursor) continue; // overlapping claim, skip to keep text contiguous
    if (start > cursor) {
      segments.push({ text: responseText.slice(cursor, start), claim: null });
    }
    segments.push({ text: responseText.slice(start, end), claim });
    cursor = end;
  }

  if (cursor < responseText.length) {
    segments.push({ text: responseText.slice(cursor), claim: null });
  }

  return segments;
}

export default function AuditedText({
  responseText,
  claims,
  activeClaim,
  onHoverClaim,
}: {
  responseText: string;
  claims: Claim[];
  activeClaim: Claim | null;
  onHoverClaim: (claim: Claim | null) => void;
}) {
  const segments = buildSegments(responseText, claims);

  return (
    <p className="font-mono text-[15px] leading-8 text-paper whitespace-pre-wrap">
      {segments.map((seg, i) => {
        if (!seg.claim) return <span key={i}>{seg.text}</span>;
        const style = VERDICT_STYLE[seg.claim.verdict];
        const isActive = activeClaim === seg.claim;
        return (
          <span
            key={i}
            onMouseEnter={() => onHoverClaim(seg.claim)}
            onMouseLeave={() => onHoverClaim(null)}
            className={`underline decoration-2 underline-offset-4 cursor-help transition-colors rounded-sm px-0.5 ${style.underline} ${style.bg} ${
              isActive ? "bg-ink-line" : ""
            }`}
          >
            {seg.text}
          </span>
        );
      })}
    </p>
  );
}
