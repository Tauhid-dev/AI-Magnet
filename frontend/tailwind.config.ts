import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        muted: "#657083",
        line: "#d7dde8",
        panel: "#ffffff",
        canvas: "#f6f8fb",
        accent: "#1f6feb",
        success: "#21834f",
        warning: "#c47a1c"
      }
    }
  },
  plugins: []
};

export default config;
