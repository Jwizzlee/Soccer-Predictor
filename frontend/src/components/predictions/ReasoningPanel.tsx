interface ReasoningPanelProps {
  reasoning: string;
  keyFactors: string[];
  riskFlags: string[];
}

export default function ReasoningPanel({
  reasoning,
  keyFactors,
  riskFlags,
}: ReasoningPanelProps) {
  return (
    <div className="space-y-5 text-sm">
      <p className="text-base leading-relaxed text-slate-200">{reasoning}</p>

      {keyFactors.length > 0 && (
        <div>
          <h4 className="mb-3 text-xs font-bold uppercase tracking-widest text-accent-primary">
            Key factors
          </h4>
          <ul className="space-y-2">
            {keyFactors.map((f, i) => (
              <li
                key={i}
                className="flex gap-3 rounded-lg border border-white/5 bg-white/5 px-3 py-2.5 text-slate-200"
              >
                <span className="mt-0.5 font-bold text-accent-primary">▸</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {riskFlags.length > 0 && (
        <div>
          <h4 className="mb-3 text-xs font-bold uppercase tracking-widest text-amber-400">
            Risk flags
          </h4>
          <ul className="space-y-2">
            {riskFlags.map((f, i) => (
              <li
                key={i}
                className="flex gap-3 rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2.5 text-amber-100/90"
              >
                <span className="text-amber-400">⚠</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
