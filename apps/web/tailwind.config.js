/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#14181F",
          surface: "#1B212B",
          raised: "#222A36",
          border: "#2E3745",
        },
        paper: {
          DEFAULT: "#EFEBE2",
          dim: "#E3DDCF",
        },
        gold: {
          DEFAULT: "#C9A227",
          bright: "#E0BC46",
          dim: "#8F7419",
        },
        sage: {
          DEFAULT: "#4F7A5A",
          bright: "#6B9C78",
          dim: "#365641",
        },
        rust: {
          DEFAULT: "#B5563A",
          bright: "#CE6B4D",
          dim: "#7E3B27",
        },
        mist: {
          DEFAULT: "#A9AFBD",
          dim: "#7B8291",
        },
      },
      fontFamily: {
        display: [
          '"Space Grotesk"',
          '"Avenir Next"',
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: [
          '"IBM Plex Mono"',
          "ui-monospace",
          "SFMono-Regular",
          '"SF Mono"',
          "Menlo",
          "monospace",
        ],
      },
      borderRadius: {
        card: "14px",
        pill: "999px",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(0,0,0,0.24), 0 8px 24px -8px rgba(0,0,0,0.35)",
        lift: "0 4px 10px rgba(0,0,0,0.28), 0 16px 40px -12px rgba(0,0,0,0.45)",
      },
      backgroundImage: {
        contour:
          "radial-gradient(circle at 20% 20%, rgba(201,162,39,0.06) 0, transparent 45%), radial-gradient(circle at 80% 60%, rgba(79,122,90,0.06) 0, transparent 40%)",
      },
    },
  },
  plugins: [],
};
