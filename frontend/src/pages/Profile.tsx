import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth, useUser } from "@clerk/react-router";
import AppShell from "../components/layout/AppShell";
import SubscriptionBadge from "../components/billing/SubscriptionBadge";
import {
  createCheckoutSession,
  createCustomerPortalSession,
} from "../api/client";
import { useSubscriptionStatus } from "../hooks/useSubscription";

function planLabel(status: string | undefined, active: boolean | undefined) {
  if (!active) return "Free";
  if (status === "admin") return "Admin";
  if (status === "active") return "Pro Analyst";
  return status ?? "Unknown";
}

export default function Profile() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const { user } = useUser();
  const { data: subscription, isLoading: subscriptionLoading } =
    useSubscriptionStatus();
  const [billingLoading, setBillingLoading] = useState(false);
  const [billingError, setBillingError] = useState<string | null>(null);

  if (!isLoaded) {
    return null;
  }

  if (!isSignedIn) {
    return <Navigate to="/" replace />;
  }

  const displayName =
    user?.fullName ||
    [user?.firstName, user?.lastName].filter(Boolean).join(" ") ||
    "Sports Predictor user";
  const email =
    user?.primaryEmailAddress?.emailAddress ?? "No email on file";
  const avatarUrl = user?.imageUrl;

  const handleManageBilling = async () => {
    setBillingError(null);
    setBillingLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Please sign in again to continue.");
      }
      const { url } = await createCustomerPortalSession(token);
      window.location.href = url;
    } catch (err) {
      setBillingError(
        err instanceof Error ? err.message : "Unable to open billing portal."
      );
      setBillingLoading(false);
    }
  };

  const handleUpgrade = async () => {
    setBillingError(null);
    setBillingLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error("Please sign in again to continue.");
      }
      const { url } = await createCheckoutSession(token);
      window.location.href = url;
    } catch (err) {
      setBillingError(
        err instanceof Error ? err.message : "Unable to start checkout."
      );
      setBillingLoading(false);
    }
  };

  const showManageBilling =
    subscription?.active && !subscription.is_admin;
  const showUpgrade = !subscription?.active && !subscription?.is_admin;

  return (
    <AppShell>
      <div className="mb-10">
        <h1 className="section-title">Account settings</h1>
        <p className="section-subtitle mt-2">
          Manage your profile, subscription, and billing
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <aside className="glass-panel h-fit p-6 lg:col-span-1">
          <div className="flex items-center gap-4">
            {avatarUrl ? (
              <img
                src={avatarUrl}
                alt=""
                className="h-16 w-16 rounded-2xl border border-white/10 object-cover"
              />
            ) : (
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-gradient-to-br from-accent-primary/30 to-accent-glow/20 font-display text-2xl font-bold text-white">
                {displayName.charAt(0).toUpperCase()}
              </div>
            )}
            <div className="min-w-0">
              <p className="truncate font-display font-semibold text-white">
                {displayName}
              </p>
              <p className="truncate text-sm text-slate-400">{email}</p>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-white/10 bg-black/20 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Plan
            </p>
            <div className="mt-2 flex items-center gap-2">
              {subscriptionLoading ? (
                <p className="text-sm text-slate-400">Loading…</p>
              ) : (
                <>
                  <p className="font-medium text-white">
                    {planLabel(subscription?.status, subscription?.active)}
                  </p>
                  {subscription?.active && (
                    <SubscriptionBadge isAdmin={subscription.is_admin} />
                  )}
                </>
              )}
            </div>
          </div>
        </aside>

        <div className="space-y-6 lg:col-span-2">
          <section className="glass-panel p-6 md:p-8">
            <h2 className="font-display text-lg font-semibold text-white">
              Profile details
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Managed through your Clerk account
            </p>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Display name
                </p>
                <p className="glass-input cursor-default opacity-90">
                  {displayName}
                </p>
              </div>
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Email address
                </p>
                <p className="glass-input cursor-default opacity-90">{email}</p>
              </div>
            </div>
          </section>

          <section className="glass-panel p-6 md:p-8">
            <h2 className="font-display text-lg font-semibold text-white">
              Subscription
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              {subscription?.is_admin
                ? "Your admin account has full access without a paid subscription."
                : subscription?.active
                  ? "You have an active Pro subscription with unlimited prop analysis."
                  : "Upgrade to unlock unlimited AI prop analysis across all leagues."}
            </p>

            <div className="mt-6 rounded-xl border border-white/10 bg-black/20 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Current status
              </p>
              <p className="mt-2 text-sm text-slate-300">
                {subscriptionLoading
                  ? "Checking subscription…"
                  : subscription?.active
                    ? subscription.is_admin
                      ? "Admin access enabled"
                      : "Pro subscription active"
                    : "No active subscription"}
              </p>
            </div>

            {billingError && (
              <p className="mt-4 rounded-lg border border-accent-under/30 bg-accent-under/10 px-4 py-3 text-sm text-accent-under">
                {billingError}
              </p>
            )}

            <div className="mt-6 flex flex-wrap gap-3">
              {showManageBilling && (
                <button
                  type="button"
                  onClick={handleManageBilling}
                  disabled={billingLoading}
                  className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition-all duration-200 ease-in-out hover:border-white/20 hover:bg-white/10 disabled:opacity-50"
                >
                  {billingLoading
                    ? "Opening portal…"
                    : "Manage billing / Cancel subscription"}
                </button>
              )}

              {showUpgrade && (
                <button
                  type="button"
                  onClick={handleUpgrade}
                  disabled={billingLoading}
                  className="rounded-xl bg-gradient-to-r from-accent-primary to-accent-glow px-5 py-3 text-sm font-bold uppercase tracking-wider text-white shadow-lg shadow-accent-primary/25 transition-all duration-200 ease-in-out hover:scale-[1.01] hover:shadow-accent-primary/40 disabled:scale-100 disabled:opacity-50"
                >
                  {billingLoading ? "Redirecting…" : "Upgrade to Pro"}
                </button>
              )}
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
