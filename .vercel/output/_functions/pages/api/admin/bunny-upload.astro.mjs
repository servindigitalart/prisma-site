import { r as requireAdmin } from '../../../chunks/admin_DmZOtt0Z.mjs';
import { c as createServiceClient } from '../../../chunks/client_DzNyPYKT.mjs';
import { g as getBunnyUploadUrl, c as createBunnyVideo } from '../../../chunks/bunny_oG5cOVSx.mjs';
export { renderers } from '../../../renderers.mjs';

const prerender = false;
const POST = async ({ request, locals }) => {
  const isAdmin = await requireAdmin(locals);
  if (!isAdmin) {
    return json({ error: "Forbidden" }, 403);
  }
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid JSON body" }, 400);
  }
  const { submission_id, title } = body;
  if (!submission_id || !title) {
    return json({ error: "Missing submission_id or title" }, 400);
  }
  const db = createServiceClient();
  const { data: sub } = await db.from("film_submissions").select("id, work_id, status").eq("id", Number(submission_id)).maybeSingle();
  if (!sub) {
    return json({ error: "Submission not found" }, 404);
  }
  if (!sub.work_id) {
    return json({ error: "Work has not been published yet. Publish first, then upload video." }, 400);
  }
  const { data: work } = await db.from("works").select("id, streaming_id, streaming_type").eq("id", sub.work_id).maybeSingle();
  if (work?.streaming_id) {
    return json({
      error: "Work already has a video linked.",
      videoId: work.streaming_id,
      uploadUrl: getBunnyUploadUrl(work.streaming_id),
      libraryId: ""
    }, 409);
  }
  try {
    const videoId = await createBunnyVideo(title);
    const uploadUrl = getBunnyUploadUrl(videoId);
    console.log(`[bunny-upload] Created video ${videoId} for work ${sub.work_id}`);
    const { error: updateErr } = await db.from("works").update({
      streaming_id: videoId,
      streaming_type: "bunny",
      streaming_url: `https://iframe.mediadelivery.net/embed/${""}/${videoId}`,
      is_streamable: false
      // Will be set to true after upload + encoding completes
    }).eq("id", sub.work_id);
    if (updateErr) {
      console.error("[bunny-upload] DB update error:", updateErr.message);
      return json({ error: `Video created in Bunny (${videoId}) but DB update failed: ${updateErr.message}` }, 500);
    }
    return json({
      success: true,
      videoId,
      uploadUrl,
      libraryId: ""
    });
  } catch (err) {
    console.error("[bunny-upload] Bunny API error:", err.message);
    return json({ error: err.message || "Failed to create Bunny video" }, 500);
  }
};
function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
