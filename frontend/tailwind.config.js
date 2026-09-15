/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#faf5eb",
        accent: "#d97706", // matches the onion.cards orange from your mockup
      },
    },
  },
  plugins: [],
};
