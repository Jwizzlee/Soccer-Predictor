/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        display: ["Outfit", "Inter", "sans-serif"],
      },
      colors: {
        surface: {
          DEFAULT: "#070b12",
          raised: "#0f1623",
          card: "#121c2e",
          border: "rgba(148, 163, 184, 0.18)",
        },
        accent: {
          over: "#34d399",
          under: "#f87171",
          primary: "#60a5fa",
          glow: "#818cf8",
        },
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0, 0, 0, 0.45)",
        glow: "0 0 40px rgba(96, 165, 250, 0.15)",
      },
      animation: {
        pulseSoft: "pulseSoft 2s ease-in-out infinite",
        shimmer: "shimmer 1.8s ease-in-out infinite",
      },
      keyframes: {
        pulseSoft: {
          "0%, 100%": { opacity: "0.45" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
    },
  },
  plugins: [],
};
