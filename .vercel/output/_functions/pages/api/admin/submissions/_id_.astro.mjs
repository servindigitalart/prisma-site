import { r as requireAdmin } from '../../../../chunks/admin_DmZOtt0Z.mjs';
import { c as createServiceClient } from '../../../../chunks/client_DzNyPYKT.mjs';
export { renderers } from '../../../../renderers.mjs';

const prerender = false;
const PATCH = async ({ params, request, locals }) => {
  const isAdmin = await requireAdmin(locals);
  if (!isAdmin) {
    return new Response(JSON.stringify({ error: "Forbidden" }), {
      status: 403,
      headers: { "Content-Type": "application/json" }
    });
  }
  const id = Number(params.id);
  if (!id || isNaN(id)) {
    return new Response(JSON.stringify({ error: "Invalid ID" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  try {
    const body = await request.clone().json();
    const { status, reviewer_notes, rejection_reason, mark_streamable, work_id } = body;
    const db = createServiceClient();
    if (mark_streamable && work_id) {
      const { error: streamErr } = await db.from("works").update({ is_streamable: true }).eq("id", work_id);
      if (streamErr) {
        console.error("[admin/submissions] mark_streamable error:", streamErr.message);
        return new Response(JSON.stringify({ error: streamErr.message }), {
          status: 500,
          headers: { "Content-Type": "application/json" }
        });
      }
      return new Response(JSON.stringify({ success: true, streamable: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }
    const updates = {};
    if (reviewer_notes !== void 0) {
      updates.reviewer_notes = reviewer_notes;
    }
    if (status) {
      if (status === "rejected" && !rejection_reason) {
        return new Response(JSON.stringify({ error: "Rejection reason is required." }), {
          status: 400,
          headers: { "Content-Type": "application/json" }
        });
      }
      updates.status = status;
      updates.reviewed_at = (/* @__PURE__ */ new Date()).toISOString();
      if (status === "rejected") {
        updates.rejection_reason = rejection_reason;
      }
      if (status === "approved") {
        updates.ficha_token = crypto.randomUUID();
        const expires = /* @__PURE__ */ new Date();
        expires.setDate(expires.getDate() + 30);
        updates.ficha_token_expires_at = expires.toISOString();
      }
    }
    const { error } = await db.from("film_submissions").update(updates).eq("id", id);
    if (error) {
      console.error("[admin/submissions] update error:", error.message);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    console.error("[admin/submissions] error:", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  PATCH,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
