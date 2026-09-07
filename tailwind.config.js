/** @type {import('tailwindcss').Config} */
module.exports = {
  safelist: ['md:col-span-2', 'md:col-span-3', 'md:col-span-6'],
  content: [
    './templates/**/*.html',
    './core/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        'muko-black': '#000000',
        'muko-red': '#FF3131',
        'muko-white': '#FFFFFF',
      },
      fontFamily: {
        bebas: ['"Bebas Neue"', 'sans-serif'],
        script: ['"Dancing Script"', 'cursive'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
