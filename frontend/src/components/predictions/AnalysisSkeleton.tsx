export default function AnalysisSkeleton() {
  return (
    <article className="glass-panel mt-6 overflow-hidden p-6">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div className="flex-1 space-y-3">
          <div className="skeleton-pulse h-6 w-48 rounded-lg" />
          <div className="skeleton-pulse h-4 w-32 rounded" />
        </div>
        <div className="skeleton-pulse h-14 w-24 rounded-xl" />
      </div>

      <div className="skeleton-pulse mb-6 h-4 w-40 rounded" />

      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-white/5 bg-black/20 p-4">
            <div className="skeleton-pulse mx-auto mb-2 h-3 w-12 rounded" />
            <div className="skeleton-pulse mx-auto h-7 w-16 rounded" />
          </div>
        ))}
      </div>

      <div className="space-y-3 border-t border-white/10 pt-5">
        <div className="skeleton-pulse h-4 w-full rounded" />
        <div className="skeleton-pulse h-4 w-11/12 rounded" />
        <div className="skeleton-pulse h-4 w-4/5 rounded" />
      </div>

      <p className="mt-5 text-center text-xs font-medium text-slate-500 animate-pulseSoft">
        Fetching match logs & running AI analysis…
      </p>
    </article>
  );
}
