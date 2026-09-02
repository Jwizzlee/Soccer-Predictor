interface SubscriptionBadgeProps {
  isAdmin?: boolean;
}

export default function SubscriptionBadge({ isAdmin = false }: SubscriptionBadgeProps) {
  return (
    <span
      className={[
        "hidden items-center rounded-full border px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] shadow-glass backdrop-blur-xl sm:inline-flex",
        isAdmin
          ? "border-amber-400/30 bg-amber-500/10 text-amber-200"
          : "border-accent-primary/30 bg-accent-primary/10 text-accent-glow",
      ].join(" ")}
    >
      {isAdmin ? "Admin" : "Pro"}
    </span>
  );
}
