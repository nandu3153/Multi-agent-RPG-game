/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Cinzel Decorative"', "serif"],
        narrative: ['"Cormorant Garamond"', "Georgia", "serif"],
        ui: ['"DM Sans"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      colors: {
        void: {
          DEFAULT: "#0a0a12",
          50: "#12121c",
          100: "#1a1a28",
          200: "#252538",
        },
        moon: {
          DEFAULT: "#c8d4e8",
          dim: "#8b9cb8",
          glow: "#e8f0ff",
        },
        gold: {
          DEFAULT: "#d4a853",
          dim: "#a67c2e",
          bright: "#f0c96b",
        },
        mystic: {
          DEFAULT: "#7c5cbf",
          dim: "#4a3580",
          glow: "#a78bfa",
        },
        ember: {
          DEFAULT: "#c45c3e",
          dim: "#8b3a24",
        },
      },
      boxShadow: {
        glow: "0 0 40px rgba(124, 92, 191, 0.15)",
        "glow-gold": "0 0 30px rgba(212, 168, 83, 0.2)",
        panel: "0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.04)",
        card: "0 4px 24px rgba(0, 0, 0, 0.5)",
      },
      animation: {
        "fade-in": "fadeIn 0.6s ease-out forwards",
        "fade-in-up": "fadeInUp 0.5s ease-out forwards",
        "slide-in-right": "slideInRight 0.4s ease-out forwards",
        "pulse-soft": "pulseSoft 3s ease-in-out infinite",
        "float": "float 6s ease-in-out infinite",
        "shimmer": "shimmer 2.5s linear infinite",
        "dice-pop": "dicePop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards",
        "star-twinkle": "twinkle 4s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        dicePop: {
          "0%": { opacity: "0", transform: "scale(0.8) rotate(-5deg)" },
          "100%": { opacity: "1", transform: "scale(1) rotate(0)" },
        },
        twinkle: {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "1" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "mesh": "radial-gradient(at 20% 30%, rgba(124,92,191,0.12) 0%, transparent 50%), radial-gradient(at 80% 70%, rgba(212,168,83,0.08) 0%, transparent 50%), radial-gradient(at 50% 50%, rgba(200,212,232,0.04) 0%, transparent 70%)",
      },
    },
  },
  plugins: [],
};
