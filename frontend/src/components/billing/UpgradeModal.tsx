import { useEffect, useState } from "react";
import { useAuth } from "@clerk/react-router";
import { createCheckoutSession } from "../../api/client";

interface UpgradeModalProps {
  open: boolean;
  onClose: () => void;
}

export default function UpgradeModal({ open, onClose }: UpgradeModalProps) {
  const { getToken } = useAuth();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setCheckoutError(null);
      setCheckoutLoading(false);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  const handleUpgrade = async () => {
    setCheckoutError(null);
    setCheckoutLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Please sign in again to continue.");
      }
      const { url } = await createCheckoutSession(token);
      window.location.href = url;
    } catch (err) {
      setCheckoutError(
        err instanceof Error ? err.message : "Unable to start checkout."
      );
      setCheckoutLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="upgrade-modal-title"
    >
      <button
        type="button"
        aria-label="Close upgrade modal"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      <div className="glass-panel relative z-10 w-full max-w-md border-white/15 p-8 shadow-glow">
        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl border border-accent-primary/30 bg-accent-primary/10">
          <svg
            viewBox="0 0 24 24"
            className="h-6 w-6 text-accent-glow"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.75"
            aria-hidden
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 3l2.2 6.8H21l-5.5 4 2.1 6.7L12 16.4 6.4 20.5l2.1-6.7L3 9.8h6.8L12 3z"
            />
          </svg>
        </div>

        <h2
          id="upgrade-modal-title"
          className="font-display text-2xl font-bold text-white"
        >
          Upgrade to Pro
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-slate-400">
          Player prop analysis requires an active subscription. Unlock unlimited
          AI-powered Over/Under insights across all supported leagues.
        </p>

        <ul className="mt-5 space-y-2 text-sm text-slate-300">
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-primary" />
            Unlimited prop analyses
          </li>
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-primary" />
            Live API-Football match logs
          </li>
          <li className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-primary" />
            GPT-4o-mini recommendations
          </li>
        </ul>

        {checkoutError && (
          <p className="mt-4 rounded-lg border border-accent-under/30 bg-accent-under/10 px-4 py-3 text-sm text-accent-under">
            {checkoutError}
          </p>
        )}

        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleUpgrade}
            disabled={checkoutLoading}
            className="flex-1 rounded-xl bg-gradient-to-r from-accent-primary to-accent-glow py-3.5 text-sm font-bold uppercase tracking-wider text-white shadow-lg shadow-accent-primary/25 transition-all duration-200 ease-in-out hover:scale-[1.01] hover:shadow-accent-primary/40 disabled:scale-100 disabled:opacity-50"
          >
            {checkoutLoading ? "Redirecting…" : "Upgrade to Pro"}
          </button>
          <button
            type="button"
            onClick={onClose}
            disabled={checkoutLoading}
            className="rounded-xl border border-white/10 bg-white/5 px-5 py-3.5 text-sm font-medium text-slate-300 transition-all duration-200 ease-in-out hover:border-white/20 hover:bg-white/10 hover:text-white disabled:opacity-50"
          >
            Not now
          </button>
        </div>
      </div>
    </div>
  );
}
