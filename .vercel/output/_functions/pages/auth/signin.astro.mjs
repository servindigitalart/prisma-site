export { renderers } from '../../renderers.mjs';

const prerender = false;
const GET = async ({ redirect, url }) => {
  const supabaseUrl = "https://porqyokkphflvqfclvkj.supabase.co";
  const redirectTo = encodeURIComponent(`${url.origin}/auth/callback`);
  return redirect(
    `${supabaseUrl}/auth/v1/authorize?provider=google&redirect_to=${redirectTo}`,
    302
  );
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
