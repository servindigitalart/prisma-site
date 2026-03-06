import { r as requireAdmin } from '../../../chunks/admin_DmZOtt0Z.mjs';
import { c as createServiceClient } from '../../../chunks/client_DzNyPYKT.mjs';
export { renderers } from '../../../renderers.mjs';

const prerender = false;
const SITE_URL = "https://prisma.film";
const POST = async ({ request, locals }) => {
  const isAdmin = await requireAdmin(locals);
  if (!isAdmin) {
    return new Response(JSON.stringify({ error: "Forbidden" }), {
      status: 403,
      headers: { "Content-Type": "application/json" }
    });
  }
  try {
    const body = await request.clone().json();
    const { submission_id } = body;
    if (!submission_id) {
      return new Response(JSON.stringify({ error: "Missing submission_id" }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    const db = createServiceClient();
    const { data: sub, error: fetchError } = await db.from("film_submissions").select("*").eq("id", submission_id).single();
    if (fetchError || !sub) {
      return new Response(JSON.stringify({ error: "Submission not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" }
      });
    }
    if (!["approved", "awaiting_ficha"].includes(sub.status)) {
      return new Response(JSON.stringify({ error: `Cannot send ficha for status "${sub.status}"` }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    let token = sub.ficha_token;
    if (!token) {
      token = crypto.randomUUID();
      const expires = /* @__PURE__ */ new Date();
      expires.setDate(expires.getDate() + 30);
      await db.from("film_submissions").update({ ficha_token: token, ficha_token_expires_at: expires.toISOString() }).eq("id", submission_id);
    }
    const fichaUrl = `${SITE_URL}/ficha/${token}`;
    const emailHtml = `
      <div style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; color: #333;">
        <h1 style="font-size: 1.5rem; font-weight: normal; color: #111;">
          Tu trabajo fue seleccionado para PRISMA
        </h1>
        <p>Hola ${sub.filmmaker_name},</p>
        <p>
          Hemos revisado <strong>${sub.title}</strong> y queremos incluirlo en el catálogo de PRISMA.
        </p>
        <p>
          Para publicar tu obra necesitamos que completes una <strong>ficha técnica</strong> con los
          créditos, tu biografía y algunos detalles adicionales.
        </p>
        <p style="margin: 2rem 0;">
          <a href="${fichaUrl}"
             style="display: inline-block; padding: 0.75rem 2rem; background: #F0EEE8; color: #111;
                    text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 0.9rem;">
            Completar ficha técnica
          </a>
        </p>
        <p style="font-size: 0.85rem; color: #888;">
          Este enlace expira en 30 días. Si tienes preguntas, responde directamente a este email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 2rem 0;" />
        <p style="font-size: 0.8rem; color: #999;">
          <strong>¿Qué sigue?</strong><br />
          Una vez que recibamos tu ficha, revisaremos la información y publicaremos tu obra en
          <a href="${SITE_URL}" style="color: #999;">prisma.film</a>.
          Recibirás una notificación cuando tu página esté activa.
        </p>
      </div>
    `;
    const resendKey = "";
    if (resendKey) ; else {
      console.log("[send-ficha] RESEND_API_KEY not set. Ficha URL:");
      console.log(fichaUrl);
      console.log("Email would go to:", sub.filmmaker_email);
    }
    await db.from("film_submissions").update({ status: "awaiting_ficha" }).eq("id", submission_id);
    return new Response(JSON.stringify({ success: true, ficha_url: fichaUrl }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    console.error("[send-ficha] error:", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
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
