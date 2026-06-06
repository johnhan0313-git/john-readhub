import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
        surface: {
          DEFAULT: "#ffffff",
          muted: "#f8fafc",
          border: "#e2e8f0",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(15,23,42,.06), 0 8px 24px rgba(14,165,233,.06)",
        "card-hover": "0 4px 12px rgba(15,23,42,.08), 0 16px 40px rgba(14,165,233,.1)",
      },
      backgroundImage: {
        "mesh-gradient":
          "radial-gradient(at 40% 20%, rgba(14,165,233,.1) 0, transparent 50%), radial-gradient(at 80% 0%, rgba(56,189,248,.08) 0, transparent 50%)",
      },
    },
  },
  plugins: [],
};

export default config;
