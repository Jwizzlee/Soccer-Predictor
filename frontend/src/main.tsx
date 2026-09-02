import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ClerkProvider } from "@clerk/react-router";
import App from "./App";
import ClerkEnvFallback from "./components/ClerkEnvFallback";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
    },
  },
});

function resolveClerkPublishableKey(): string | undefined {
  const raw = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
  if (typeof raw !== "string") {
    return undefined;
  }
  const trimmed = raw.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

const clerkPublishableKey = resolveClerkPublishableKey();
const root = document.getElementById("root");

if (!root) {
  throw new Error("Root element #root not found");
}

if (!clerkPublishableKey) {
  if (import.meta.env.DEV) {
    console.warn(
      "[Clerk] VITE_CLERK_PUBLISHABLE_KEY is missing. Check frontend/.env and restart `npm run dev` from the frontend folder."
    );
  }
  createRoot(root).render(<ClerkEnvFallback />);
} else {
  createRoot(root).render(
    <StrictMode>
      <BrowserRouter>
        <ClerkProvider publishableKey={clerkPublishableKey}>
          <QueryClientProvider client={queryClient}>
            <App />
          </QueryClientProvider>
        </ClerkProvider>
      </BrowserRouter>
    </StrictMode>
  );
}
