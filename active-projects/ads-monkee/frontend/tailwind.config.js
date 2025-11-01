/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ads-blue': '#2E86AB',
        'ads-purple': '#A23B72',
        'ads-orange': '#F18F01',
        'ads-green': '#C73E1D'
      }
    },
  },
  plugins: [],
}
