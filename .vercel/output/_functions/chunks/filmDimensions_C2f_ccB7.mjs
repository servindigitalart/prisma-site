const RHYTHM_LABELS = {
  dinamico_frenetico: "Frenético",
  dinamico_energico: "Cinético",
  moderado_balanceado: "Narrativo",
  lento_contemplativo: "Contemplativo",
  estatico_ritualistico: "Ritual"
};
const TEMPERATURE_LABELS = {
  calido_apasionado: "Ardiente",
  calido_nostalgico: "Nostálgico",
  neutral_contemplativo: "Ecuánime",
  frio_melancolico: "Melancólico",
  frio_perturbador: "Perturbador",
  frio_alienado: "Alienante"
};
const ABSTRACTION_LABELS = {
  extremadamente_realista: "Documental",
  realista_con_estilizacion: "Realista",
  estilizado: "Estilizado",
  muy_estilizado: "Expresionista",
  extremadamente_abstracto: "Surrealista"
};
const RHYTHM_DESCRIPTIONS = {
  dinamico_frenetico: "Películas que no dan respiro. Edición hipnótica, energía caótica, cámara en movimiento constante.",
  dinamico_energico: "Movimiento con intención. Acción controlada, montaje preciso, ritmo que impulsa la narrativa.",
  moderado_balanceado: "El flujo clásico del cine. Ritmo al servicio de la historia, sin excesos en ninguna dirección.",
  lento_contemplativo: "El tiempo como material cinematográfico. Planos largos, silencios que pesan, belleza en la pausa.",
  estatico_ritualistico: "La cámara como testigo inmóvil. Encuadres fijos, movimiento mínimo, tiempo suspendido."
};
const TEMPERATURE_DESCRIPTIONS = {
  calido_apasionado: "Intensidad visceral. Películas que queman, que exigen, que no dejan indiferente a nadie.",
  calido_nostalgico: "La calidez del recuerdo. Dorado, tierno, agridulce. El cine que abraza mientras duele.",
  neutral_contemplativo: "La mirada sin juicio. Observacional, equilibrada, cine que confía en el espectador.",
  frio_melancolico: "Azul interior. Introspección, tristeza elegante, la belleza que solo existe en la pérdida.",
  frio_perturbador: "El frío que inquieta. Alienación, tensión subterránea, algo que no termina de estar bien.",
  frio_alienado: "La distancia como estética. Frialdad estructural, cine que observa desde lejos, la emoción reprimida como forma."
};
const ABSTRACTION_DESCRIPTIONS = {
  extremadamente_realista: "La cámara como documento. Sin filtros, sin estilización. La vida tal como es.",
  realista_con_estilizacion: "Anclado en lo real pero con mirada cinematográfica. El mundo, pero más.",
  estilizado: "Decisiones visuales conscientes. Un lenguaje propio que va más allá del realismo.",
  muy_estilizado: "La imagen como declaración. Expresionismo, teatralidad, la forma como contenido.",
  extremadamente_abstracto: "El cine que sueña despierto. Surrealismo, lógica onírica, imágenes que no se olvidan."
};
function rhythmSlug(id) {
  return id.replace(/_/g, "-");
}
function temperatureSlug(id) {
  return id.replace(/_/g, "-");
}
function abstractionSlug(id) {
  return id.replace(/_/g, "-");
}

export { ABSTRACTION_LABELS as A, RHYTHM_LABELS as R, TEMPERATURE_LABELS as T, ABSTRACTION_DESCRIPTIONS as a, RHYTHM_DESCRIPTIONS as b, TEMPERATURE_DESCRIPTIONS as c, abstractionSlug as d, rhythmSlug as r, temperatureSlug as t };
