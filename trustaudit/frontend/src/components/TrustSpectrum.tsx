export default function TrustSpectrum({ score, risk }: { score: number; risk: "low" | "medium" | "high" }) {
  const riskColor = risk === "low" ? "text-verified" : risk === "medium" ? "text-flagged" : "text-critical";
  const riskLabel = risk === "low" ? "Grounded" : risk === "medium" ? "Mixed" : "Fabrication risk";

  return (
    <div className="w-full">
      <div className="flex items-baseline justify-between mb-2">
        <span className="font-display text-sm tracking-wide text-muted uppercase">Trust score</span>
        <span className={`font-display text-2xl font-semibold ${riskColor}`}>
          {score.toFixed(0)}
          <span className="text-muted text-base font-normal">/100</span>
        </span>
      </div>
      <div className="relative h-2 rounded-full bg-ink-line overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${score}%`,
            background: "linear-gradient(90deg, #E8675A 0%, #F0A857 50%, #4FD1C5 100%)",
          }}
        />
        <div
          className="absolute inset-y-0 w-0.5 bg-paper/80 transition-all duration-700 ease-out"
          style={{ left: `${score}%` }}
        />
      </div>
      <div className="flex justify-between mt-1.5 text-xs text-muted font-mono">
        <span>Fabricated</span>
        <span className={riskColor}>{riskLabel}</span>
        <span>Grounded</span>
      </div>
    </div>
  );
}
