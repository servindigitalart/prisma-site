/**
 * src/lib/film/filmDimensions.ts
 * ────────────────────────────────
 * Film dimension types and display mappings for the three cultural axes:
 * - Visual Rhythm
 * - Emotional Temperature
 * - Visual Abstraction
 */

export type VisualRhythm =
  | 'dinamico_frenetico'
  | 'dinamico_energico'
  | 'moderado_balanceado'
  | 'lento_contemplativo'
  | 'estatico_ritualistico'

export type EmotionalTemperature =
  | 'calido_apasionado'
  | 'calido_nostalgico'
  | 'neutral_contemplativo'
  | 'frio_melancolico'
  | 'frio_perturbador'
  | 'frio_alienado'

export type VisualAbstraction =
  | 'extremadamente_realista'
  | 'realista_con_estilizacion'
  | 'estilizado'
  | 'muy_estilizado'
  | 'extremadamente_abstracto'

// ─── UX Display Names ────────────────────────────────────────────────────────

export const RHYTHM_LABELS: Record<VisualRhythm, string> = {
  dinamico_frenetico:    'Frenético',
  dinamico_energico:     'Cinético',
  moderado_balanceado:   'Narrativo',
  lento_contemplativo:   'Contemplativo',
  estatico_ritualistico: 'Ritual',
}

export const TEMPERATURE_LABELS: Record<EmotionalTemperature, string> = {
  calido_apasionado:     'Ardiente',
  calido_nostalgico:     'Nostálgico',
  neutral_contemplativo: 'Ecuánime',
  frio_melancolico:      'Melancólico',
  frio_perturbador:      'Perturbador',
  frio_alienado:         'Alienante',
}

export const ABSTRACTION_LABELS: Record<VisualAbstraction, string> = {
  extremadamente_realista:    'Documental',
  realista_con_estilizacion:  'Realista',
  estilizado:                 'Estilizado',
  muy_estilizado:             'Expresionista',
  extremadamente_abstracto:   'Surrealista',
}

// ─── Short descriptions for category pages ───────────────────────────────────

export const RHYTHM_DESCRIPTIONS: Record<VisualRhythm, string> = {
  dinamico_frenetico:    'Películas que no dan respiro. Edición hipnótica, energía caótica, cámara en movimiento constante.',
  dinamico_energico:     'Movimiento con intención. Acción controlada, montaje preciso, ritmo que impulsa la narrativa.',
  moderado_balanceado:   'El flujo clásico del cine. Ritmo al servicio de la historia, sin excesos en ninguna dirección.',
  lento_contemplativo:   'El tiempo como material cinematográfico. Planos largos, silencios que pesan, belleza en la pausa.',
  estatico_ritualistico: 'La cámara como testigo inmóvil. Encuadres fijos, movimiento mínimo, tiempo suspendido.',
}

export const TEMPERATURE_DESCRIPTIONS: Record<EmotionalTemperature, string> = {
  calido_apasionado:     'Intensidad visceral. Películas que queman, que exigen, que no dejan indiferente a nadie.',
  calido_nostalgico:     'La calidez del recuerdo. Dorado, tierno, agridulce. El cine que abraza mientras duele.',
  neutral_contemplativo: 'La mirada sin juicio. Observacional, equilibrada, cine que confía en el espectador.',
  frio_melancolico:      'Azul interior. Introspección, tristeza elegante, la belleza que solo existe en la pérdida.',
  frio_perturbador:      'El frío que inquieta. Alienación, tensión subterránea, algo que no termina de estar bien.',
  frio_alienado:         'La distancia como estética. Frialdad estructural, cine que observa desde lejos, la emoción reprimida como forma.',
}

export const ABSTRACTION_DESCRIPTIONS: Record<VisualAbstraction, string> = {
  extremadamente_realista:   'La cámara como documento. Sin filtros, sin estilización. La vida tal como es.',
  realista_con_estilizacion: 'Anclado en lo real pero con mirada cinematográfica. El mundo, pero más.',
  estilizado:                'Decisiones visuales conscientes. Un lenguaje propio que va más allá del realismo.',
  muy_estilizado:            'La imagen como declaración. Expresionismo, teatralidad, la forma como contenido.',
  extremadamente_abstracto:  'El cine que sueña despierto. Surrealismo, lógica onírica, imágenes que no se olvidan.',
}

// ─── URL slug helpers ─────────────────────────────────────────────────────────

export function rhythmSlug(id: VisualRhythm): string {
  return id.replace(/_/g, '-')
}

export function temperatureSlug(id: EmotionalTemperature): string {
  return id.replace(/_/g, '-')
}

export function abstractionSlug(id: VisualAbstraction): string {
  return id.replace(/_/g, '-')
}

// ─── Reverse lookup: slug → ID ────────────────────────────────────────────────

export function slugToRhythm(slug: string): VisualRhythm {
  return slug.replace(/-/g, '_') as VisualRhythm
}

export function slugToTemperature(slug: string): EmotionalTemperature {
  return slug.replace(/-/g, '_') as EmotionalTemperature
}

export function slugToAbstraction(slug: string): VisualAbstraction {
  return slug.replace(/-/g, '_') as VisualAbstraction
}
