export const GENRE_MAP: Record<string, {
  name: string
  slug: string
  description: string
  svg: string
}> = {
  'Drama': {
    name: 'Drama', slug: 'drama',
    description: 'El alma del cine de autor. Conflictos humanos, emociones en carne viva.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 9c0-1.1.9-2 2-2h3l2-3h6l2 3h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9Z"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><circle cx="9" cy="11.5" r=".5" fill="currentColor"/><circle cx="15" cy="11.5" r=".5" fill="currentColor"/></svg>`,
  },
  'Crime': {
    name: 'Crimen', slug: 'crimen',
    description: 'La moral en sus límites. Noir, policiales, el submundo.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="10" width="7" height="4" rx="2"/><rect x="14" y="10" width="7" height="4" rx="2"/><path d="M10 12h4"/><path d="M6 10V8a2 2 0 0 1 4 0v2"/><path d="M14 10V8a2 2 0 0 1 4 0v2"/></svg>`,
  },
  'Thriller': {
    name: 'Thriller', slug: 'thriller',
    description: 'Tensión, paranoia, el suspenso como forma de arte.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8Z"/></svg>`,
  },
  'Romance': {
    name: 'Romance', slug: 'romance',
    description: 'El amor como tema eterno. Desde Rohmer hasta Wong Kar-wai.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z"/></svg>`,
  },
  'Comedy': {
    name: 'Comedia', slug: 'comedia',
    description: 'La risa crítica. Desde Chaplin hasta la sátira contemporánea.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><circle cx="9" cy="10" r=".5" fill="currentColor"/><circle cx="15" cy="10" r=".5" fill="currentColor"/></svg>`,
  },
  'Horror': {
    name: 'Terror', slug: 'terror',
    description: 'El miedo como espejo. Horror artístico, pesadillas cinematográficas.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="12" rx="9" ry="6"/><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r=".75" fill="currentColor"/></svg>`,
  },
  'Science Fiction': {
    name: 'Ciencia Ficción', slug: 'ciencia-ficcion',
    description: 'Futuros posibles. La tecnología, la humanidad, el tiempo.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><ellipse cx="12" cy="12" rx="11" ry="4.5" transform="rotate(-15 12 12)"/></svg>`,
  },
  'War': {
    name: 'Guerra', slug: 'guerra',
    description: 'El horror del conflicto. Desde Kubrick hasta Malick.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m14 6-8.5 8.5a2.12 2.12 0 0 0 3 3L17 9"/><path d="m17 9 1.5-1.5a2.12 2.12 0 0 0-3-3L14 6"/><path d="m5 19 2-2M19 5l-2 2"/></svg>`,
  },
  'History': {
    name: 'Historia', slug: 'historia',
    description: 'El pasado como espejo del presente.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21V6"/><path d="M19 21V6"/><path d="M5 6c1-2 2.5-3 7-3s6 1 7 3"/><path d="M5 11h14"/><path d="M5 16h14"/><path d="M3 21h18"/></svg>`,
  },
  'Adventure': {
    name: 'Aventura', slug: 'aventura',
    description: 'El viaje como metáfora. Exploraciones físicas y espirituales.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12Z"/></svg>`,
  },
  'Animation': {
    name: 'Animación', slug: 'animacion',
    description: 'El dibujo como realidad. Miyazaki, el stop-motion, la forma pura.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>`,
  },
  'Documentary': {
    name: 'Documental', slug: 'documental',
    description: 'La realidad como material cinematográfico.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3L14.5 4Z"/><circle cx="12" cy="13" r="3"/></svg>`,
  },
  'Music': {
    name: 'Música', slug: 'musica',
    description: 'El ritmo, la actuación, el arte sonoro en imagen.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`,
  },
  'Mystery': {
    name: 'Misterio', slug: 'misterio',
    description: 'Lo que no se ve. La ambigüedad como herramienta narrativa.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/></svg>`,
  },
  'Western': {
    name: 'Western', slug: 'western',
    description: 'El género americano por excelencia. Ford, Leone, Peckinpah.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 22v-4M7 6c0 3 1 4 5 6-4 2-5 3-5 6M17 6c0 3-1 4-5 6 4 2 5 3 5 6"/><path d="M5 12h2M17 12h2"/></svg>`,
  },
  'Fantasy': {
    name: 'Fantasía', slug: 'fantasia',
    description: 'Lo imposible hecho imagen. Mundos alternativos y oníricos.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/><path d="M19 3v4M21 5h-4"/></svg>`,
  },
  'Family': {
    name: 'Familia', slug: 'familia',
    description: 'Historias universales contadas para todos.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="5" r="2"/><circle cx="17" cy="4" r="2.5"/><circle cx="12" cy="4" r="1.5"/><path d="M4 20v-5a3 3 0 0 1 6 0v5M14 20v-4a3 3 0 0 1 6 0v4"/><path d="M9.5 20v-3.5a2.5 2.5 0 0 1 5 0V20"/></svg>`,
  },
  'Action': {
    name: 'Acción', slug: 'accion',
    description: 'El movimiento puro. Cuerpos, persecuciones, velocidad.',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5Z"/></svg>`,
  },
}

/** Reverse map: slug → TMDB genre name */
export const SLUG_TO_GENRE: Record<string, string> = Object.fromEntries(
  Object.entries(GENRE_MAP).map(([tmdb, info]) => [info.slug, tmdb])
)

export function getGenreInfo(tmdbGenre: string) {
  return GENRE_MAP[tmdbGenre] ?? {
    name: tmdbGenre,
    slug: tmdbGenre.toLowerCase().replace(/ /g, '-'),
    description: '',
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>`,
  }
}
