import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        cream: '#F4EDE0',
        'cream-deep': '#ECE2CE',
        'cream-light': '#FAF6EE',
        olive: '#5C5A3F',
        'olive-soft': '#8A8868',
        earth: '#8B6F4E',
        'earth-light': '#C9B391',
        wine: '#6B2D2D',
        ink: '#2B2620',
        'ink-soft': '#6C645A',
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', '"Times New Roman"', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'display': ['clamp(56px, 9vw, 144px)', { lineHeight: '0.95' }],
        'heading': ['clamp(40px, 5.5vw, 78px)', { lineHeight: '1.02' }],
        'subheading': ['clamp(26px, 2.4vw, 36px)', { lineHeight: '1.1' }],
        'lead': ['clamp(20px, 1.8vw, 26px)', { lineHeight: '1.5' }],
      },
      letterSpacing: {
        'eyebrow': '0.32em',
        'nav': '0.12em',
        'cta': '0.18em',
      },
      borderRadius: {
        'pill': '999px',
      },
      maxWidth: {
        'wrap': '1320px',
      },
      animation: {
        'marquee': 'marquee 38s linear infinite',
        'marquee-reverse': 'marquee 38s linear infinite reverse',
        'scroll-line': 'scrollLine 2.2s ease-in-out infinite',
        'pulse-wa': 'pulseWa 2.4s ease-in-out infinite',
      },
      keyframes: {
        marquee: {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        },
        scrollLine: {
          '0%, 100%': { transform: 'scaleY(0.4)', transformOrigin: 'top' },
          '50%': { transform: 'scaleY(1)' },
        },
        pulseWa: {
          '0%, 100%': {
            boxShadow: '0 10px 30px rgba(37,211,102,0.45), 0 0 0 0 rgba(37,211,102,0.5)',
          },
          '50%': {
            boxShadow: '0 10px 30px rgba(37,211,102,0.45), 0 0 0 14px rgba(37,211,102,0)',
          },
        },
      },
    },
  },
  plugins: [],
}

export default config
