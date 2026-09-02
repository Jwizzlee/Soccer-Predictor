interface FormBadgesProps {
  values: number[];
  line: number;
  lastN: number;
}

export default function FormBadges({ values, line, lastN }: FormBadgesProps) {
  if (values.length === 0) return null;

  return (
    <div className="rounded-xl border border-white/5 bg-black/20 px-4 py-3">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Last {lastN} game form
      </p>
      <div className="flex flex-wrap gap-2">
        {values.map((value, index) => {
          const isOver = value > line;
          const isPush = value === line;

          return (
            <span
              key={index}
              className={`min-w-[2.25rem] rounded-full border px-3 py-1 text-center text-sm font-bold ${
                isOver
                  ? "border-accent-over/40 bg-accent-over/20 text-accent-over"
                  : isPush
                    ? "border-slate-500/40 bg-slate-600/30 text-slate-300"
                    : "border-white/10 bg-white/5 text-slate-500"
              }`}
            >
              {value}
            </span>
          );
        })}
      </div>
    </div>
  );
}
