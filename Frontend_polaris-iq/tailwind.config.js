/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#070810',
        card: 'rgba(17, 18, 30, 0.65)',
        cardBorder: 'rgba(99, 102, 241, 0.2)',
        primary: {
          DEFAULT: '#6366f1',
          light: '#818cf8',
        },
        secondary: {
          DEFAULT: '#a855f7',
          light: '#c084fc',
        },
        accent: {
          DEFAULT: '#0ea5e9',
        }
      },
      boxShadow: {
        'neon': '0 0 10px rgba(99, 102, 241, 0.3), 0 0 20px rgba(168, 85, 247, 0.1)',
        'neon-strong': '0 0 15px rgba(99, 102, 241, 0.6), 0 0 30px rgba(168, 85, 247, 0.4)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass-gradient': 'linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
      }
    },
  },
  plugins: [require('@tailwindcss/typography')],
}

