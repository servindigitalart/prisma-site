import { c as createServiceClient } from '../../../chunks/client_DzNyPYKT.mjs';
export { renderers } from '../../../renderers.mjs';

const prerender = false;
const POST = async ({ params, request }) => {
  const { token } = params;
  if (!token) {
    return json({ error: "Missing token" }, 400);
  }
  const db = createServiceClient();
  const { data: sub, error: fetchErr } = await db.from("film_submissions").select("*").eq("ficha_token", token).maybeSingle();
  if (fetchErr || !sub) {
    return json({ error: "Invalid or expired token" }, 404);
  }
  if (sub.status === "published") {
    return json({ error: "This work has already been published." }, 400);
  }
  if (sub.status === "ficha_received") {
    return json({ error: "Ficha already submitted." }, 400);
  }
  const isExpired = sub.ficha_token_expires_at && new Date(sub.ficha_token_expires_at) < /* @__PURE__ */ new Date();
  if (isExpired) {
    return json({ error: "This link has expired. Contact the PRISMA team for a new one." }, 400);
  }
  let formData;
  try {
    formData = await request.formData();
  } catch {
    return json({ error: "Invalid form data" }, 400);
  }
  const credits = parseCredits(formData);
  const submissionId = String(sub.id);
  const bucket = "filmmaker-assets";
  let filmmakerPhotoUrl = null;
  const filmmakerPhoto = formData.get("filmmaker_photo");
  if (filmmakerPhoto && filmmakerPhoto instanceof File && filmmakerPhoto.size > 0) {
    filmmakerPhotoUrl = await uploadFile(db, bucket, `submissions/${submissionId}/filmmaker`, filmmakerPhoto);
  }
  for (const role of Object.keys(credits)) {
    for (const entry of credits[role]) {
      if (entry._photoFile && entry._photoFile instanceof File && entry._photoFile.size > 0) {
        const slug = slugify(entry.name || "unknown");
        const path = `submissions/${submissionId}/credits/${role}/${slug}`;
        entry.photo_url = await uploadFile(db, bucket, path, entry._photoFile);
      }
      delete entry._photoFile;
    }
  }
  const bioFull = formStr(formData, "bio_full");
  const filmmakerWebsite = formStr(formData, "filmmaker_website");
  const filmmakerInstagram = formStr(formData, "filmmaker_instagram");
  const countries = formStr(formData, "countries");
  const languages = formStr(formData, "languages");
  const genres = formStr(formData, "genres");
  const synopsisFull = formStr(formData, "synopsis_full");
  const { error: updateErr } = await db.from("film_submissions").update({
    status: "ficha_received",
    ficha_submitted_at: (/* @__PURE__ */ new Date()).toISOString(),
    ficha_credits: credits,
    ficha_bio_full: bioFull || null,
    ficha_filmmaker_photo: filmmakerPhotoUrl || null,
    ficha_filmmaker_website: filmmakerWebsite || null,
    ficha_filmmaker_instagram: filmmakerInstagram || null,
    ficha_countries: countries ? splitComma(countries) : null,
    ficha_languages: languages ? splitComma(languages) : null,
    ficha_genres: genres ? splitComma(genres) : null,
    ficha_synopsis_full: synopsisFull || null
  }).eq("id", sub.id);
  if (updateErr) {
    console.error("[ficha] update error:", updateErr.message);
    return json({ error: "Error saving ficha. Please try again." }, 500);
  }
  return json({ success: true });
};
function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}
function formStr(formData, key) {
  const val = formData.get(key);
  return typeof val === "string" ? val.trim() : "";
}
function splitComma(str) {
  return str.split(",").map((s) => s.trim()).filter(Boolean);
}
function slugify(str) {
  return str.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60);
}
function parseCredits(formData) {
  const credits = {};
  const creditRegex = /^credits\[(\w+)\]\[(\d+)\]\[(\w+)\](?:\[(\w+)\])?$/;
  for (const [key, value] of formData.entries()) {
    const match = key.match(creditRegex);
    if (!match) continue;
    const [, role, idxStr, field, subField] = match;
    const idx = parseInt(idxStr, 10);
    if (!credits[role]) credits[role] = {};
    if (!credits[role][idx]) credits[role][idx] = { name: "", bio: "", also: [], photo_url: null };
    if (field === "also" && subField) {
      if (value === "on") {
        credits[role][idx].also.push(subField);
      }
    } else if (field === "photo") {
      if (value instanceof File && value.size > 0) {
        credits[role][idx]._photoFile = value;
      }
    } else if (field === "name") {
      credits[role][idx].name = typeof value === "string" ? value.trim() : "";
    } else if (field === "bio") {
      credits[role][idx].bio = typeof value === "string" ? value.trim() : "";
    }
  }
  const result = {};
  for (const role of Object.keys(credits)) {
    const entries = Object.values(credits[role]).filter((e) => e.name);
    if (entries.length > 0) {
      result[role] = entries;
    }
  }
  return result;
}
async function uploadFile(db, bucket, pathPrefix, file) {
  try {
    const ext = file.name.split(".").pop()?.toLowerCase() || "jpg";
    const filePath = `${pathPrefix}.${ext}`;
    const { error } = await db.storage.from(bucket).upload(filePath, file, {
      contentType: file.type || "image/jpeg",
      upsert: true
    });
    if (error) {
      console.error(`[ficha] upload error for ${filePath}:`, error.message);
      return null;
    }
    const { data: urlData } = db.storage.from(bucket).getPublicUrl(filePath);
    return urlData?.publicUrl || null;
  } catch (err) {
    console.error(`[ficha] upload exception:`, err);
    return null;
  }
}

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
