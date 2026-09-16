/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f4f9f8",
          100: "#dbeeea",
          500: "#007f7a",
          700: "#075f5f",
          900: "#0c2f30"
        },
        accent: {
          500: "#ff6b35",
          700: "#d9480f"
        }
      },
      fontFamily: {
        primary: ["var(--font-primary)"],
        titles: ["var(--font-titles)"],
        labels: ["var(--font-labels)"],
        display: ["var(--font-titles)"],
        body: ["var(--font-primary)"],
        ui: ["var(--font-labels)"]
      },
      boxShadow: {
        glow: "0 10px 40px rgba(0, 127, 122, 0.25)"
      }
    },
  },
  plugins: [],
};
