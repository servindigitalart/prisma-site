import { readFileSync } from 'fs';
import { resolve } from 'path';

let _doctrinCache = null;
function loadColorDoctrine() {
  if (_doctrinCache) return _doctrinCache;
  const doctrinePaths = [
    // Try current symlink first
    "pipeline/doctrine/current/color_doctrine.json",
    // Fallback to versioned file
    "pipeline/doctrine/v1.1/color_doctrine.json"
  ];
  for (const relativePath of doctrinePaths) {
    try {
      const fullPath = resolve(process.cwd(), relativePath);
      const raw = readFileSync(fullPath, "utf-8");
      _doctrinCache = JSON.parse(raw);
      return _doctrinCache;
    } catch {
    }
  }
  console.error("[colors] Could not load color doctrine from any known path.");
  return null;
}
function getColorProfile(colorId) {
  const doctrine = loadColorDoctrine();
  if (!doctrine) return null;
  return doctrine.colors.find((c) => c.id === colorId) ?? null;
}
function getAllColorProfiles() {
  const doctrine = loadColorDoctrine();
  return doctrine?.colors ?? [];
}

export { getAllColorProfiles as a, getColorProfile as g };
