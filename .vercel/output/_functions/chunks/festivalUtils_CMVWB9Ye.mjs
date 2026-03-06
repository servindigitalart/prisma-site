function getFestivalLogoUrl(logoPath) {
  if (!logoPath) return null;
  if (logoPath.startsWith("/logos/")) return logoPath;
  if (logoPath.startsWith("http")) return logoPath;
  return `https://image.tmdb.org/t/p/w92${logoPath}`;
}
function isFestivalLogoLocal(logoPath) {
  return !!logoPath && logoPath.startsWith("/logos/");
}
const STOP_WORDS = /* @__PURE__ */ new Set([
  "of",
  "the",
  "and",
  "de",
  "du",
  "di",
  "del",
  "la",
  "le",
  "les",
  "film",
  "festival",
  "awards",
  "award",
  "international",
  "prize",
  "cinema",
  "film",
  "a"
]);
function getFestivalMonogram(name) {
  const words = name.split(/[\s\-]+/).map((w) => w.replace(/[^A-Za-zÀ-ÿ]/g, "")).filter((w) => w.length > 0 && !STOP_WORDS.has(w.toLowerCase()));
  if (words.length === 0) return name[0]?.toUpperCase() ?? "?";
  if (words[0] === words[0].toUpperCase() && words[0].length >= 2) {
    return words[0].slice(0, 2).toUpperCase();
  }
  return words.slice(0, 2).map((w) => w[0].toUpperCase()).join("");
}

export { getFestivalMonogram as a, getFestivalLogoUrl as g, isFestivalLogoLocal as i };
