import { useState } from "react";
import { Link } from "react-router-dom";
import { SignInButton, useAuth } from "@clerk/react-router";
import AppShell from "../components/layout/AppShell";
import { createCheckoutSession } from "../api/client";

const FEATURES = [
  {
    title: "Live match logs",
    desc: "Pull real per-game stats from API-Football across top global leagues.",
  },
  {
    title: "AI prop engine",
    desc: "GPT-4o-mini synthesizes hit rates, trends, and risk flags into clear picks.",
  },
  {
    title: "Multi-league coverage",
    desc: "Premier League, La Liga, Serie A, UCL, and World Cup — one dashboard.",
  },
];

const PLAN_FEATURES = [
  "Unlimited prop analyses",
  "5 global soccer competitions",
  "GPT-4o-mini Over/Under insights",
  "Last-N game stat windows",
  "Priority API rate pacing",
];

export default function Landing() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  const handleSubscribe = async () => {
    setCheckoutError(null);
    setCheckoutLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Unable to authenticate. Please sign in again.");
      }
      const { url } = await createCheckoutSession(token);
      window.location.href = url;
    } catch (err) {
      setCheckoutError(
        err instanceof Error ? err.message : "Checkout failed. Try again."
      );
      setCheckoutLoading(false);
    }
  };

  return (
    <AppShell>
      <section className="mb-16 text-center">
        <span className="inline-block rounded-full border border-accent-primary/30 bg-accent-primary/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-accent-primary">
          Soccer prop intelligence platform
        </span>
        <h1 className="mt-6 font-display text-4xl font-extrabold leading-tight tracking-tight text-white md:text-6xl">
          Research player props
          <br />
          <span className="bg-gradient-to-r from-accent-primary to-accent-glow bg-clip-text text-transparent">
            like a pro
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          Sports Predictor combines live API-Football data with AI analysis to
          help you evaluate Over/Under lines before you place a pick.
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/dashboard"
            className="rounded-xl bg-gradient-to-r from-accent-primary to-accent-glow px-8 py-3.5 text-sm font-bold uppercase tracking-wider text-white shadow-lg shadow-accent-primary/25 transition-all duration-200 ease-in-out hover:scale-[1.02]"
          >
            Open dashboard
          </Link>
          <a
            href="#pricing"
            className="rounded-xl border border-white/10 bg-white/5 px-8 py-3.5 text-sm font-semibold text-slate-300 transition-all duration-200 ease-in-out hover:border-white/20 hover:bg-white/10 hover:text-white"
          >
            View pricing
          </a>
        </div>
      </section>

      <section className="mb-20 grid gap-6 md:grid-cols-3">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="glass-panel p-6 transition-all duration-200 ease-in-out hover:scale-[1.02]"
          >
            <h3 className="font-display text-lg font-semibold text-white">
              {f.title}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              {f.desc}
            </p>
          </div>
        ))}
      </section>

      <section id="pricing" className="mx-auto max-w-lg">
        <div className="mb-8 text-center">
          <h2 className="section-title">Simple pricing</h2>
          <p className="section-subtitle mt-2">
            One tier to get started — scale as we add NBA & NFL
          </p>
        </div>

        <article className="glass-panel relative overflow-hidden border-accent-primary/30 p-8 shadow-glow">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-transparent via-accent-primary to-transparent" />
          <span className="rounded-full border border-accent-primary/40 bg-accent-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-accent-primary">
            Most popular
          </span>
          <h3 className="mt-4 font-display text-2xl font-bold text-white">
            Pro Analyst
          </h3>
          <div className="mt-4 flex items-baseline gap-1">
            <span className="font-display text-5xl font-extrabold text-white">
              $15
            </span>
            <span className="text-slate-400">/ month</span>
          </div>
          <p className="mt-3 text-sm text-slate-400">
            Full access to live soccer prop analysis across all supported
            competitions.
          </p>

          <ul className="mt-8 space-y-3">
            {PLAN_FEATURES.map((item) => (
              <li
                key={item}
                className="flex items-center gap-3 text-sm text-slate-300"
              >
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent-over/20 text-xs text-accent-over">
                  ✓
                </span>
                {item}
              </li>
            ))}
          </ul>

          {isLoaded && isSignedIn ? (
            <button
              type="button"
              onClick={handleSubscribe}
              disabled={checkoutLoading}
              className="mt-8 w-full rounded-xl bg-gradient-to-r from-accent-primary to-accent-glow py-3.5 text-sm font-bold uppercase tracking-wider text-white shadow-lg shadow-accent-primary/25 transition-all duration-200 ease-in-out hover:scale-[1.01] disabled:scale-100 disabled:opacity-60"
            >
              {checkoutLoading ? "Redirecting to Stripe…" : "Subscribe now"}
            </button>
          ) : (
            <SignInButton mode="modal">
              <button
                type="button"
                className="mt-8 w-full rounded-xl bg-gradient-to-r from-accent-primary to-accent-glow py-3.5 text-sm font-bold uppercase tracking-wider text-white shadow-lg shadow-accent-primary/25 transition-all duration-200 ease-in-out hover:scale-[1.01]"
              >
                Sign in to subscribe
              </button>
            </SignInButton>
          )}

          {checkoutError && (
            <p className="mt-4 rounded-lg border border-accent-under/30 bg-accent-under/10 px-4 py-3 text-center text-sm text-accent-under">
              {checkoutError}
            </p>
          )}

          <p className="mt-4 text-center text-xs text-slate-500">
            Secure Stripe checkout · Cancel anytime
          </p>
        </article>
      </section>
    </AppShell>
  );
}
