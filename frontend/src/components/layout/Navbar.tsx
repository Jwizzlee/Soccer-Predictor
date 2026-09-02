import { Link, NavLink } from "react-router-dom";
import {
  SignInButton,
  SignUpButton,
  UserButton,
  useAuth,
} from "@clerk/react-router";
import SubscriptionBadge from "../billing/SubscriptionBadge";
import { useSubscriptionStatus } from "../../hooks/useSubscription";

function navLinkClass({ isActive }: { isActive: boolean }) {
  return [
    "rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 ease-in-out",
    isActive
      ? "bg-accent-primary/15 text-accent-primary"
      : "text-slate-400 hover:bg-white/5 hover:text-white",
  ].join(" ");
}

export default function Navbar() {
  const { isLoaded, isSignedIn } = useAuth();
  const { data: subscription } = useSubscriptionStatus();

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-surface/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4 lg:px-10">
        <Link to="/" className="group min-w-0 shrink-0">
          <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-accent-primary">
            Prop Intelligence
          </p>
          <h1 className="font-display text-xl font-bold tracking-tight text-white transition-colors group-hover:text-accent-primary md:text-2xl">
            Sports Predictor
          </h1>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavLink to="/dashboard" className={navLinkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/profile" className={navLinkClass}>
            Profile
          </NavLink>
        </nav>

        <div className="flex items-center gap-2">
          {isLoaded && !isSignedIn && (
            <>
            <SignInButton mode="modal">
              <button
                type="button"
                className="hidden rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-300 transition-all duration-200 ease-in-out hover:border-white/20 hover:bg-white/10 hover:text-white sm:inline-flex"
              >
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button
                type="button"
                className="rounded-lg bg-gradient-to-r from-accent-primary to-accent-glow px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-accent-primary/20 transition-all duration-200 ease-in-out hover:scale-[1.02] hover:shadow-accent-primary/35"
              >
                Register
              </button>
            </SignUpButton>
            </>
          )}
          {isLoaded && isSignedIn && (
            <div className="flex items-center gap-2">
              {subscription?.active && (
                <SubscriptionBadge isAdmin={subscription.is_admin} />
              )}
              <div className="rounded-full border border-white/10 bg-white/5 p-1">
                <UserButton />
              </div>
            </div>
          )}
        </div>
      </div>

      <nav className="flex gap-1 border-t border-white/5 px-6 py-2 md:hidden lg:px-10">
        <NavLink to="/dashboard" className={navLinkClass}>
          Dashboard
        </NavLink>
        <NavLink to="/profile" className={navLinkClass}>
          Profile
        </NavLink>
      </nav>
    </header>
  );
}
