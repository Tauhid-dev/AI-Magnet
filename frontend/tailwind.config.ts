import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        muted: "#657083",
        line: "#d7e0ec",
        panel: "#ffffff",
        canvas: "#eef3f9",
        accent: "#1f6feb",
        success: "#21834f",
        warning: "#c47a1c"
      }
    }
  },
  plugins: []
};

export default config;
