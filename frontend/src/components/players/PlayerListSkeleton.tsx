export default function PlayerListSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="grid gap-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="glass-panel flex items-center gap-4 p-4">
          <div className="skeleton-pulse h-14 w-14 shrink-0 rounded-2xl" />
          <div className="flex-1 space-y-2">
            <div className="skeleton-pulse h-4 w-2/5 rounded" />
            <div className="skeleton-pulse h-3 w-3/5 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}
