export const GENRE_MAP: Record<string, {
  name: string
  slug: string
  description: string
  emoji: string
}> = {
  'Drama': {
    name: 'Drama', slug: 'drama',
    description: 'El alma del cine de autor. Conflictos humanos, emociones en carne viva.',
    emoji: '🎭',
  },
  'Crime': {
    name: 'Crimen', slug: 'crimen',
    description: 'La moral en sus límites. Noir, policiales, el submundo.',
    emoji: '🔫',
  },
  'Thriller': {
    name: 'Thriller', slug: 'thriller',
    description: 'Tensión, paranoia, el suspenso como forma de arte.',
    emoji: '😰',
  },
  'Romance': {
    name: 'Romance', slug: 'romance',
    description: 'El amor como tema eterno. Desde Rohmer hasta Wong Kar-wai.',
    emoji: '❤️',
  },
  'Comedy': {
    name: 'Comedia', slug: 'comedia',
    description: 'La risa crítica. Desde Chaplin hasta la sátira contemporánea.',
    emoji: '😄',
  },
  'Horror': {
    name: 'Terror', slug: 'terror',
    description: 'El miedo como espejo. Horror artístico, pesadillas cinematográficas.',
    emoji: '👁️',
  },
  'Science Fiction': {
    name: 'Ciencia Ficción', slug: 'ciencia-ficcion',
    description: 'Futuros posibles. La tecnología, la humanidad, el tiempo.',
    emoji: '🚀',
  },
  'War': {
    name: 'Guerra', slug: 'guerra',
    description: 'El horror del conflicto. Desde Kubrick hasta Malick.',
    emoji: '⚔️',
  },
  'History': {
    name: 'Historia', slug: 'historia',
    description: 'El pasado como espejo del presente.',
    emoji: '📜',
  },
  'Adventure': {
    name: 'Aventura', slug: 'aventura',
    description: 'El viaje como metáfora. Exploraciones físicas y espirituales.',
    emoji: '🗺️',
  },
  'Animation': {
    name: 'Animación', slug: 'animacion',
    description: 'El dibujo como realidad. Miyazaki, el stop-motion, la forma pura.',
    emoji: '✏️',
  },
  'Documentary': {
    name: 'Documental', slug: 'documental',
    description: 'La realidad como material cinematográfico.',
    emoji: '📽️',
  },
  'Music': {
    name: 'Música', slug: 'musica',
    description: 'El ritmo, la actuación, el arte sonoro en imagen.',
    emoji: '🎵',
  },
  'Mystery': {
    name: 'Misterio', slug: 'misterio',
    description: 'Lo que no se ve. La ambigüedad como herramienta narrativa.',
    emoji: '🔍',
  },
  'Western': {
    name: 'Western', slug: 'western',
    description: 'El género americano por excelencia. Ford, Leone, Peckinpah.',
    emoji: '🤠',
  },
  'Fantasy': {
    name: 'Fantasía', slug: 'fantasia',
    description: 'Lo imposible hecho imagen. Mundos alternativos y oníricos.',
    emoji: '🌙',
  },
  'Family': {
    name: 'Familia', slug: 'familia',
    description: 'Historias universales contadas para todos.',
    emoji: '👨‍👩‍👧',
  },
  'Action': {
    name: 'Acción', slug: 'accion',
    description: 'El movimiento puro. Cuerpos, persecuciones, velocidad.',
    emoji: '💥',
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
    emoji: '🎬',
  }
}
