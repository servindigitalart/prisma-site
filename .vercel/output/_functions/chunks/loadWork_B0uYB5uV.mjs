import fs from 'fs';
import path from 'path';
import { i as isSupabaseConfigured, c as createServiceClient } from './client_DzNyPYKT.mjs';

const WORKS_DIR = path.resolve("pipeline/normalized/works");
function loadAllWorksFromFilesystem() {
  if (!fs.existsSync(WORKS_DIR)) {
    console.warn(`[loadWork] Works directory not found: ${WORKS_DIR}`);
    return [];
  }
  return fs.readdirSync(WORKS_DIR).filter((f) => f.endsWith(".json")).map((file) => {
    const raw = fs.readFileSync(path.join(WORKS_DIR, file), "utf-8");
    const data = JSON.parse(raw);
    return {
      ...data,
      slug: file.replace("work_", "").replace(".json", "")
    };
  });
}
function loadWorkBySlugFromFilesystem(slug) {
  const file = `work_${slug}.json`;
  const fullPath = path.join(WORKS_DIR, file);
  if (!fs.existsSync(fullPath)) return null;
  const data = JSON.parse(
    fs.readFileSync(fullPath, "utf-8")
  );
  return { ...data, slug };
}
async function loadWorkBySlugFromSupabase(slug) {
  try {
    const db = createServiceClient();
    const workId = `work_${slug}`;
    const { data, error } = await db.from("works").select(
      `
        *,
        color_assignments(*),
        work_people(role, billing_order, people(*)),
        work_studios(studios(*)),
        work_awards(*, awards(*, festivals(id, name, country, tier, logo_path)), people(id, name))
      `
    ).eq("id", workId).eq("is_published", true).single();
    if (error) {
      if (error.code !== "PGRST116") {
        console.error(
          `[loadWork] Supabase getWorkBySlug(${slug}) error:`,
          error.message
        );
      }
      return null;
    }
    return data;
  } catch (err) {
    console.error("[loadWork] Supabase connection failed:", err);
    return null;
  }
}
function loadAllWorks() {
  return loadAllWorksFromFilesystem();
}
async function loadWorkBySlugAsync(slug) {
  if (isSupabaseConfigured()) {
    const supabaseResult = await loadWorkBySlugFromSupabase(slug);
    if (supabaseResult) return supabaseResult;
  }
  return loadWorkBySlugFromFilesystem(slug);
}

export { loadWorkBySlugAsync as a, loadAllWorks as l };
