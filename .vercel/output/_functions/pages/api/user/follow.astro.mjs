import { c as createSupabaseServerClient } from '../../../chunks/server_Cbvb-X7K.mjs';
export { renderers } from '../../../renderers.mjs';

const prerender = false;
const POST = async ({ request, cookies, locals }) => {
  const user = locals.user;
  if (!user) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" }
    });
  }
  const body = await request.clone().json();
  const { following_id } = body;
  if (!following_id) {
    return new Response(JSON.stringify({ error: "Invalid request" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  if (following_id === user.id) {
    return new Response(JSON.stringify({ error: "Cannot follow yourself" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  const supabase = createSupabaseServerClient(cookies, request);
  const { data: existing } = await supabase.from("follows").select("*").eq("follower_id", user.id).eq("following_id", following_id).maybeSingle();
  let following = false;
  if (existing) {
    const { error } = await supabase.from("follows").delete().eq("follower_id", user.id).eq("following_id", following_id);
    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  } else {
    const { error } = await supabase.from("follows").insert({
      follower_id: user.id,
      following_id,
      created_at: (/* @__PURE__ */ new Date()).toISOString()
    });
    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
    following = true;
  }
  return new Response(JSON.stringify({ success: true, following }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
