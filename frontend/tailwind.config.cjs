/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'beau-rivage': ['"Beau Rivage"', 'cursive'],
        'tangerine-regular': ["Tangerine", 'cursive'],
      }
    },
  },
  plugins: [],
}