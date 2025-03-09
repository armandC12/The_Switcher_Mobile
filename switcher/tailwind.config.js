/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
	  './index.html', // Include index.html
	  './src/**/*.{js,jsx,ts,tsx}', // Include all JS/TS files inside the src folder
	],
	theme: {
	  extend: {
		// fontSize: {
		//   xs: '0.875rem', // Tailwind default: 0.75rem
		//   sm: '1rem',     // Tailwind default: 0.875rem
		//   base: '1.125rem', // Tailwind default: 1rem
		//   lg: '1.25rem',   // Tailwind default: 1.125rem
		//   xl: '1.5rem',    // Tailwind default: 1.25rem
		//   '2xl': '1.875rem', // Tailwind default: 1.5rem
		//   '3xl': '2.25rem', // Tailwind default: 1.875rem
		//   '4xl': '2.875rem', // Tailwind default: 2.25rem
		//   '5xl': '3.5rem',   // Tailwind default: 3rem
		//   '6xl': '4rem',    // Tailwind default: 3.75rem
		//   '7xl': '4.5rem',   // Tailwind default: 4.5rem
		//   '8xl': '5rem',    // Tailwind default: 6rem
		//   '9xl': '6rem',    // Tailwind default: 8rem
		// },
		borderRadius: {
		  lg: 'var(--radius)',
		  md: 'calc(var(--radius) - 2px)',
		  sm: 'calc(var(--radius) - 4px)'
		},
		colors: {
		  background: 'hsl(var(--background))',
		  foreground: 'hsl(var(--foreground))',
		  card: {
			DEFAULT: 'hsl(var(--card))',
			foreground: 'hsl(var(--card-foreground))'
		  },
		  popover: {
			DEFAULT: 'hsl(var(--popover))',
			foreground: 'hsl(var(--popover-foreground))'
		  },
		  primary: {
			DEFAULT: 'hsl(var(--primary))',
			foreground: 'hsl(var(--primary-foreground))'
		  },
		  secondary: {
			DEFAULT: 'hsl(var(--secondary))',
			foreground: 'hsl(var(--secondary-foreground))'
		  },
		  muted: {
			DEFAULT: 'hsl(var(--muted))',
			foreground: 'hsl(var(--muted-foreground))'
		  },
		  accent: {
			DEFAULT: 'hsl(var(--accent))',
			foreground: 'hsl(var(--accent-foreground))'
		  },
		  destructive: {
			DEFAULT: 'hsl(var(--destructive))',
			foreground: 'hsl(var(--destructive-foreground))'
		  },
		  border: 'hsl(var(--border))',
		  input: 'hsl(var(--input))',
		  ring: 'hsl(var(--ring))',
		  chart: {
			'1': 'hsl(var(--chart-1))',
			'2': 'hsl(var(--chart-2))',
			'3': 'hsl(var(--chart-3))',
			'4': 'hsl(var(--chart-4))',
			'5': 'hsl(var(--chart-5))'
		  }
		},
	  }
	},
	plugins: [require("tailwindcss-animate")],
  }
  