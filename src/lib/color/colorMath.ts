export type ColorSemantics = {
  lightness: "light" | "balanced" | "dark";
  chroma: "muted" | "balanced" | "vivid";
  stability: "controlled" | "balanced" | "chaotic";
};

export function deriveColorSemantics(summary: {
  L_mean: number;
  chroma_mean: number;
  L_std: number;
  chroma_std: number;
}): ColorSemantics {
  const lightness =
    summary.L_mean > 0.7 ? "light" :
    summary.L_mean < 0.45 ? "dark" : "balanced";

  const chroma =
    summary.chroma_mean < 0.04 ? "muted" :
    summary.chroma_mean > 0.09 ? "vivid" : "balanced";

  const stability =
    (summary.L_std + summary.chroma_std) < 0.12 ? "controlled" :
    (summary.L_std + summary.chroma_std) > 0.25 ? "chaotic" : "balanced";

  return { lightness, chroma, stability };
}
