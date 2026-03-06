/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        serif: ['DM Serif Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        // Prisma palette
        prisma: {
          'rojo-pasional':       '#8E1B1B',
          'naranja-apocaliptico':'#C4471D',
          'ambar-desertico':     '#C98A2E',
          'amarillo-ludico':     '#F2C94C',
          'verde-lima':          '#7BC96F',
          'verde-esmeralda':     '#1F7A5C',
          'verde-distopico':     '#2F4F3E',
          'cian-melancolico':    '#4A7C8C',
          'azul-nocturno':       '#1B2A41',
          'violeta-cinetico':    '#5B3FA4',
          'purpura-onirico':     '#7A3E6D',
          'magenta-pop':         '#D63384',
          'blanco-polar':        '#E8EEF2',
          'negro-abismo':        '#0A0A0F',
          'titanio-mecanico':    '#8A9199',
        },
        // Site surfaces
        surface: {
          bg:       '#0D0D0F',
          elevated: '#141418',
          card:     '#1A1A20',
        },
      },
      maxWidth: {
        site: '1280px',
        content: '860px',
      },
    },
  },
  plugins: [],
}
