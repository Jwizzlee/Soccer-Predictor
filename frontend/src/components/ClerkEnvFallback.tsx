export default function ClerkEnvFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#070b12] px-6 text-slate-200">
      <div className="max-w-lg rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-xl">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">
          Configuration required
        </p>
        <h1 className="mt-3 font-display text-2xl font-bold text-white">
          Clerk publishable key not loaded
        </h1>
        <p className="mt-4 text-sm leading-relaxed text-slate-400">
          Add{" "}
          <code className="rounded bg-black/40 px-1.5 py-0.5 text-blue-300">
            VITE_CLERK_PUBLISHABLE_KEY
          </code>{" "}
          to <code className="rounded bg-black/40 px-1.5 py-0.5">frontend/.env</code>,
          then restart the Vite dev server from the{" "}
          <code className="rounded bg-black/40 px-1.5 py-0.5">frontend</code> directory.
        </p>
      </div>
    </div>
  );
}
