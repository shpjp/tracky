/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './tracker_app/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#2563eb',
        'primary-dark': '#1d4ed8'
      }
    },
  },
  plugins: [],
}