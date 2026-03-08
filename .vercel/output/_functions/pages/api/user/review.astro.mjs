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
  const { work_id, review } = body;
  if (!work_id) {
    return new Response(JSON.stringify({ error: "Invalid request" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  if (review && review.length > 500) {
    return new Response(JSON.stringify({ error: "Review too long (max 500 characters)" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  const supabase = createSupabaseServerClient(cookies, request);
  const { data, error } = await supabase.from("user_ratings").upsert(
    {
      user_id: user.id,
      work_id,
      review: review.trim(),
      updated_at: (/* @__PURE__ */ new Date()).toISOString()
    },
    { onConflict: "user_id,work_id" }
  ).select().single();
  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
  return new Response(JSON.stringify({ success: true, data }), {
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
