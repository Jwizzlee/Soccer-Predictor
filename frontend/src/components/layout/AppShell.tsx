import type { ReactNode } from "react";
import Navbar from "./Navbar";

interface AppShellProps {
  children: ReactNode;
  /** Wider main area for dashboard-style pages */
  wide?: boolean;
}

export default function AppShell({ children, wide = false }: AppShellProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-surface">
      <div
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          backgroundImage: `
            linear-gradient(rgba(96, 165, 250, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(96, 165, 250, 0.04) 1px, transparent 1px)
          `,
          backgroundSize: "48px 48px",
        }}
      />
      <div className="pointer-events-none absolute -left-32 top-0 h-96 w-96 rounded-full bg-accent-primary/10 blur-3xl" />
      <div className="pointer-events-none absolute -right-32 bottom-0 h-96 w-96 rounded-full bg-accent-glow/10 blur-3xl" />

      <Navbar />
      <main
        className={`relative mx-auto px-6 py-10 lg:px-10 lg:py-14 ${
          wide ? "max-w-7xl" : "max-w-6xl"
        }`}
      >
        {children}
      </main>
      <footer className="relative border-t border-white/10 py-6 text-center text-xs text-slate-500">
        For research and entertainment only. Not financial or betting advice.
      </footer>
    </div>
  );
}
