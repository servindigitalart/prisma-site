import { c as createSupabaseServerClient } from '../../../chunks/server_Cbvb-X7K.mjs';
import { P as PRISMA_PALETTE } from '../../../chunks/colorPalette_MBD9-pHi.mjs';
export { renderers } from '../../../renderers.mjs';

const prerender = false;
const GET = async ({ url, cookies }) => {
  const workId = url.searchParams.get("work_id");
  const userId = url.searchParams.get("user_id");
  if (!workId) {
    return new Response(JSON.stringify({ error: "work_id required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  const supabase = createSupabaseServerClient(cookies);
  const { data: work } = await supabase.from("works").select(`
      title,
      year,
      color_assignments (
        color_id
      )
    `).eq("id", workId).single();
  if (!work) {
    return new Response(JSON.stringify({ error: "Work not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" }
    });
  }
  const colorId = work.color_assignments?.[0]?.color_id;
  const color = colorId ? PRISMA_PALETTE[colorId] : null;
  let rating = null;
  if (userId) {
    const { data: ratingData } = await supabase.from("user_ratings").select("rating").eq("user_id", userId).eq("work_id", workId).single();
    rating = ratingData?.rating || null;
  }
  const slug = workId.replace(/^work_/, "");
  return new Response(JSON.stringify({
    url: `/share/${slug}${userId ? `?user=${userId}` : ""}`,
    title: work.title,
    year: work.year,
    color: color?.name || "Unknown",
    hex: color?.hex || "#4A4A4A",
    rating
  }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
