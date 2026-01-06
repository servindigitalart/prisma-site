import { deriveColorSemantics } from "./colorMath";

export function buildColorNarrative(summary: {
  L_mean: number;
  chroma_mean: number;
  L_std: number;
  chroma_std: number;
}) {
  const s = deriveColorSemantics(summary);

  // Curated editorial sentences (short, expandable later)
  if (s.lightness === "light" && s.chroma === "muted" && s.stability === "controlled") {
    return "Soft pastels and powdered light shape a delicate, ornamental visual world.";
  }

  if (s.lightness === "dark" && s.chroma === "vivid") {
    return "Rich, saturated colors emerge from darkness with emotional intensity.";
  }

  if (s.lightness === "balanced" && s.chroma === "balanced") {
    return "A restrained color palette that quietly supports the film’s emotional tone.";
  }

  // Fallback (never empty)
  return "A distinctive color language defines the film’s visual identity.";
}
