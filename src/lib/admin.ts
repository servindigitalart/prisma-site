import { createServiceClient } from './db/client'

export async function requireAdmin(locals: App.Locals): Promise<boolean> {
  if (!locals.user) return false
  const db = createServiceClient()
  const { data } = await db
    .from('user_profiles')
    .select('is_admin')
    .eq('id', locals.user.id)
    .maybeSingle()
  return data?.is_admin === true
}
