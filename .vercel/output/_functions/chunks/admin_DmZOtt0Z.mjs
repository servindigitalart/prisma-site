import { c as createServiceClient } from './client_DzNyPYKT.mjs';

async function requireAdmin(locals) {
  if (!locals.user) return false;
  const db = createServiceClient();
  const { data } = await db.from("user_profiles").select("is_admin").eq("id", locals.user.id).maybeSingle();
  return data?.is_admin === true;
}

export { requireAdmin as r };
