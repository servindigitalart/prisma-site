type OKLabColor = {
  L: number;
  a: number;
  b: number;
  hex: string;
  weight: number;
};

export function extractTopColors(
  palette: OKLabColor[],
  limit = 3
) {
  return [...palette]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, limit)
    .map(c => ({
      hex: c.hex,
      lightness: c.L,
      weight: c.weight
    }));
}

export function buildDominanceNarrative(colors: {
  hex: string;
  lightness: number;
}[]) {
  if (!colors.length) {
    return "A restrained chromatic balance shapes the film’s visual atmosphere.";
  }

  if (colors[0].lightness > 0.7) {
    return "Pale, luminous tones dominate the film’s visual composition.";
  }

  if (colors[0].lightness < 0.4) {
    return "Deep, shadowed hues dominate the film’s visual composition.";
  }

  return "Balanced mid-tones dominate the film’s visual composition.";
}
