import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "PingFang SC", "Microsoft YaHei", "system-ui", "sans-serif"],
      },
      colors: {
        panel: "rgba(10, 17, 32, 0.78)",
        line: "rgba(94, 234, 212, 0.22)",
        cyan: "#5eead4",
        violet: "#a78bfa",
      },
      boxShadow: {
        glow: "0 0 34px rgba(94, 234, 212, 0.18)",
        violet: "0 0 28px rgba(167, 139, 250, 0.2)",
      },
    },
  },
  plugins: [],
} satisfies Config;
