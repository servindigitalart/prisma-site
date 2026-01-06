import fs from "fs";
import path from "path";

const WORKS_DIR = path.resolve("pipeline/normalized/works");

export function loadAllWorks() {
  return fs
    .readdirSync(WORKS_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((file) => {
      const raw = fs.readFileSync(path.join(WORKS_DIR, file), "utf-8");
      const data = JSON.parse(raw);
      return {
        ...data,
        slug: file.replace("work_", "").replace(".json", ""),
      };
    });
}

export function loadWorkBySlug(slug: string) {
  const file = `work_${slug}.json`;
  const fullPath = path.join(WORKS_DIR, file);

  if (!fs.existsSync(fullPath)) return null;

  return JSON.parse(fs.readFileSync(fullPath, "utf-8"));
}
