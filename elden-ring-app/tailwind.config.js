module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        elden: {
          dark: '#1a1306',
          medium: '#2d2411',
          light: '#e6d2a8',
          gold: '#ffd700',
          bronze: '#976f2d',
          accent: '#c7a767',
        },
      },
      fontFamily: {
        elden: ['Cinzel', 'serif'],
      },
    },
  },
  plugins: [],
}