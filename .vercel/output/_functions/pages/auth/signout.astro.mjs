import { c as createSupabaseServerClient } from '../../chunks/server_DDrZ4Pp_.mjs';
export { renderers } from '../../renderers.mjs';

const prerender = false;
const POST = async ({ cookies, redirect }) => {
  const supabase = createSupabaseServerClient(cookies);
  await supabase.auth.signOut();
  return redirect("/", 302);
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
