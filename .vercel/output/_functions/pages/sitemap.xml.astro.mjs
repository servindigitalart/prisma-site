import { i as isSupabaseConfigured, c as createServiceClient } from '../chunks/client_DzNyPYKT.mjs';
export { renderers } from '../renderers.mjs';

const prerender = false;
const SITE = "https://prisma.film";
const GET = async () => {
  if (!isSupabaseConfigured()) {
    return new Response("<!-- Supabase not configured -->", {
      status: 503,
      headers: { "Content-Type": "application/xml" }
    });
  }
  const db = createServiceClient();
  const [worksRes, peopleRes, festivalsRes] = await Promise.all([
    db.from("works").select("id, updated_at").order("updated_at", { ascending: false }),
    db.from("people").select("id, updated_at").order("updated_at", { ascending: false }),
    db.from("festivals").select("id").order("name", { ascending: true })
  ]);
  const staticPages = [
    { loc: "/", priority: "1.0", changefreq: "daily" },
    { loc: "/rankings/films", priority: "0.9", changefreq: "daily" },
    { loc: "/colors", priority: "0.8", changefreq: "weekly" },
    { loc: "/people", priority: "0.8", changefreq: "weekly" },
    { loc: "/festivals", priority: "0.8", changefreq: "weekly" },
    { loc: "/countries", priority: "0.7", changefreq: "weekly" },
    { loc: "/submit", priority: "0.4", changefreq: "monthly" }
  ];
  const decades = ["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"];
  const urls = [];
  for (const page of staticPages) {
    urls.push(
      `  <url>
    <loc>${SITE}${page.loc}</loc>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`
    );
  }
  for (const decade of decades) {
    urls.push(
      `  <url>
    <loc>${SITE}/decades/${decade}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>`
    );
  }
  for (const work of worksRes.data ?? []) {
    const slug = work.id.replace(/^work_/, "");
    const lastmod = work.updated_at ? new Date(work.updated_at).toISOString().split("T")[0] : "";
    urls.push(
      `  <url>
    <loc>${SITE}/films/${slug}</loc>${lastmod ? `
    <lastmod>${lastmod}</lastmod>` : ""}
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`
    );
  }
  for (const person of peopleRes.data ?? []) {
    const slug = person.id.replace(/^person_/, "");
    const lastmod = person.updated_at ? new Date(person.updated_at).toISOString().split("T")[0] : "";
    urls.push(
      `  <url>
    <loc>${SITE}/people/${slug}</loc>${lastmod ? `
    <lastmod>${lastmod}</lastmod>` : ""}
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`
    );
  }
  for (const fest of festivalsRes.data ?? []) {
    const slug = fest.id.replace(/^festival_/, "");
    urls.push(
      `  <url>
    <loc>${SITE}/festivals/${slug}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>`
    );
  }
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.join("\n")}
</urlset>`;
  return new Response(xml, {
    status: 200,
    headers: {
      "Content-Type": "application/xml",
      "Cache-Control": "public, max-age=3600, s-maxage=3600"
    }
  });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
