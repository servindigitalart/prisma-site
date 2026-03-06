import { c as createServiceClient } from '../../../chunks/client_DzNyPYKT.mjs';
import { a as getBunnyEmbedUrlSigned } from '../../../chunks/bunny_oG5cOVSx.mjs';
export { renderers } from '../../../renderers.mjs';

const prerender = false;
const GET = async ({ params }) => {
  const workId = params.work_id;
  if (!workId) {
    return json({ error: "Missing work_id" }, 400);
  }
  const db = createServiceClient();
  const { data: work } = await db.from("works").select("id, streaming_id, streaming_type, is_streamable").eq("id", workId).maybeSingle();
  if (!work) {
    return json({ error: "Work not found" }, 404);
  }
  if (!work.is_streamable || !work.streaming_id) {
    return json({ error: "This work is not available for streaming" }, 404);
  }
  if (work.streaming_type !== "bunny") {
    return json({ error: `Unsupported streaming provider: ${work.streaming_type}` }, 400);
  }
  const embedUrl = getBunnyEmbedUrlSigned(work.streaming_id);
  const expires = Math.floor(Date.now() / 1e3) + 14400;
  return json({ embedUrl, expires });
};
function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
