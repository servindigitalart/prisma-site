import { c as createSupabaseServerClient } from '../../chunks/server_Cbvb-X7K.mjs';
export { renderers } from '../../renderers.mjs';

const prerender = false;
const POST = async ({ request, cookies }) => {
  try {
    const body = await request.clone().json();
    const {
      type,
      title,
      year,
      runtime_min,
      synopsis,
      drive_link,
      filmmaker_name,
      filmmaker_email,
      filmmaker_bio,
      filmmaker_website,
      filmmaker_social,
      episode_count,
      rights_confirmed,
      rejection_understood
    } = body;
    if (!title || !year || !runtime_min || !synopsis || !drive_link || !filmmaker_name || !filmmaker_email) {
      return new Response(JSON.stringify({ error: "Please fill in all required fields." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    try {
      new URL(drive_link);
    } catch {
      return new Response(JSON.stringify({ error: "Please provide a valid Google Drive link." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(filmmaker_email)) {
      return new Response(JSON.stringify({ error: "Please provide a valid email address." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    if (!rights_confirmed || !rejection_understood) {
      return new Response(JSON.stringify({ error: "Please accept both checkboxes under Rights." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    if (synopsis.length > 500) {
      return new Response(JSON.stringify({ error: "Synopsis must be 500 characters or less." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    const supabase = createSupabaseServerClient(cookies, request);
    const extraMeta = [];
    if (type) extraMeta.push(`Content type: ${type}`);
    if (drive_link) extraMeta.push(`Google Drive: ${drive_link}`);
    if (filmmaker_social) extraMeta.push(`Social: ${filmmaker_social}`);
    if (episode_count) extraMeta.push(`Episodes: ${episode_count}`);
    const { error } = await supabase.from("film_submissions").insert({
      title,
      year: Number(year),
      runtime_min: Number(runtime_min),
      synopsis,
      filmmaker_name,
      filmmaker_email,
      filmmaker_bio: filmmaker_bio || null,
      filmmaker_website: filmmaker_website || null,
      storage_path: drive_link,
      copyright_attested: true,
      reviewer_notes: extraMeta.join("\n")
    });
    if (error) {
      console.error("[submit] insert error:", error.message);
      return new Response(JSON.stringify({ error: "Failed to save submission. Please try again." }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    console.error("[submit] unexpected error:", err);
    return new Response(JSON.stringify({ error: "Internal server error. Please try again." }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
