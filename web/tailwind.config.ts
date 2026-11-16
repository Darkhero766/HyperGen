import type { Config } from "tailwindcss";
export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: { colors: { ink: "#070910", violet: "#a69aff", mint: "#a6ffe2" }, fontFamily: { sans: ["Inter", "Arial", "sans-serif"] } } },
  plugins: [],
} satisfies Config;
