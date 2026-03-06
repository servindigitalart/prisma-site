import { c as createServiceClient } from '../../../chunks/client_DzNyPYKT.mjs';
export { renderers } from '../../../renderers.mjs';

const POST = async ({ request, redirect }) => {
  const db = createServiceClient();
  const formData = await request.formData();
  const articleId = formData.get("article_id");
  if (!articleId) {
    return new Response("Missing article_id", { status: 400 });
  }
  const id = parseInt(articleId.toString(), 10);
  if (isNaN(id)) {
    return new Response("Invalid article_id", { status: 400 });
  }
  try {
    const { error } = await db.from("generated_articles").update({
      is_published: false,
      reviewed_at: (/* @__PURE__ */ new Date()).toISOString()
    }).eq("id", id);
    if (error) {
      console.error("[reject-article] Error:", error);
      return new Response(`Error: ${error.message}`, { status: 500 });
    }
    return redirect("/admin/review", 303);
  } catch (err) {
    console.error("[reject-article] Exception:", err);
    return new Response("Internal server error", { status: 500 });
  }
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
