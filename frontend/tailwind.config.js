/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: "#0f766e",
        accent: "#fb923c",
        ink: "#111827",
        paper: "#f8fafc"
      },
      fontFamily: {
        heading: ["Poppins", "sans-serif"],
        body: ["Manrope", "sans-serif"]
      }
    }
  },
  plugins: []
};
