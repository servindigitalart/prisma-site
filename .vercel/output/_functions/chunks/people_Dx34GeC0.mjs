import { c as createServiceClient } from './client_DzNyPYKT.mjs';

async function getPersonBySlug(slug) {
  const db = createServiceClient();
  const personId = `person_${slug}`;
  const { data: personData, error: personError } = await db.from("people").select("*").eq("id", personId).single();
  if (personError) {
    if (personError.code !== "PGRST116") {
      console.error(`[people] getPersonBySlug(${slug}) error:`, personError.message);
    }
    return null;
  }
  const { data: profileData } = await db.from("person_color_profiles").select("*").eq("person_id", personId);
  const { data: filmographyData, error: filmError } = await db.from("work_people").select(
    `
      role,
      works!inner(
        id, title, year, tmdb_poster_path, is_published,
        color_assignments(color_iconico, tier)
      )
    `
  ).eq("person_id", personId).eq("works.is_published", true);
  if (filmError) {
    console.error(`[people] filmography query error for ${slug}:`, filmError.message);
  }
  const profiles = profileData ?? [];
  const directorProfile = profiles.find((p) => p.role_context === "director") || profiles.find((p) => p.role_context === "cinematography") || profiles[0] || null;
  const filmography = (filmographyData ?? []).map((row) => {
    const r = row;
    const ca = r.works.color_assignments?.[0] ?? null;
    return {
      work: {
        id: r.works.id,
        title: r.works.title,
        year: r.works.year,
        tmdb_poster_path: r.works.tmdb_poster_path
      },
      role: r.role,
      color: ca ? { color_iconico: ca.color_iconico, tier: ca.tier } : null
    };
  });
  return {
    ...personData,
    color_profile: directorProfile,
    filmography
  };
}

export { getPersonBySlug };
