/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          100: '#2d2d2d',
          200: '#1f1f1f',
          300: '#121212',
          400: '#0d0d0d',
          500: '#000000',
        },
        gray: {
          light: '#f7fafc',
          medium: '#a0aec0',
          dark: '#2d3748',
        },
        primary: {
          DEFAULT: '#4299e1',
        },
      },
    },
  },
  plugins: [],
}