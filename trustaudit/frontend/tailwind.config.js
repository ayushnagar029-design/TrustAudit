/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0B1220",
          surface: "#131B2C",
          line: "#222D42",
        },
        verified: "#4FD1C5",
        flagged: "#F0A857",
        critical: "#E8675A",
        muted: "#8B95AC",
        paper: "#E8ECF4",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
