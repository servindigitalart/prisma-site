/**
 * src/lib/db/client.ts
 * ─────────────────────
 * Supabase client factory for Astro.
 *
 * Two clients are exported:
 *
 * 1. `supabase` — anon/public client using PUBLIC_SUPABASE_ANON_KEY.
 *    Safe to instantiate on the client-side. Respects RLS policies.
 *    Use for: user-specific queries in React islands, client-side auth.
 *
 * 2. `createServiceClient()` — service role client using SUPABASE_SERVICE_KEY.
 *    Server-side ONLY. Bypasses RLS. Never expose this key to the browser.
 *    Use for: Astro build-time static path generation, server API routes.
 *
 * Note: Until you run `npx supabase gen types typescript`, import Database
 * from './database.types' (generated). Until then, types default to `unknown`.
 * The `any` casts in this file will be removed once types are generated.
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { Database } from "./database.types";

// ─── Environment variable helpers ────────────────────────────────────────────

function getEnv(key: string): string {
  const value = import.meta.env[key];
  if (!value) {
    throw new Error(
      `Missing required environment variable: ${key}\n` +
        `Add it to .env.local (server-side: no PUBLIC_ prefix, build-time only)\n` +
        `or to .env.local with PUBLIC_ prefix for client-safe variables.`
    );
  }
  return value as string;
}

function getEnvOptional(key: string): string | undefined {
  return import.meta.env[key] as string | undefined;
}

// ─── Public (anon) client ────────────────────────────────────────────────────
// Uses PUBLIC_SUPABASE_ANON_KEY — safe for client-side rendering.
// Will throw at runtime if PUBLIC_SUPABASE_URL is not set.

let _publicClient: SupabaseClient<Database> | null = null;

export function getPublicClient(): SupabaseClient<Database> {
  if (!_publicClient) {
    const url = getEnv("PUBLIC_SUPABASE_URL");
    const key = getEnv("PUBLIC_SUPABASE_ANON_KEY");
    _publicClient = createClient<Database>(url, key, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
      },
    });
  }
  return _publicClient;
}

// Convenience export for the most common use case
export const supabase = {
  get client() {
    return getPublicClient();
  },
};

// ─── Service role client (server-side ONLY) ───────────────────────────────────
// Uses SUPABASE_SERVICE_KEY — bypasses RLS, never expose to browser.
// Each call creates a new client instance (no session persistence needed).

export function createServiceClient(): SupabaseClient<Database> {
  const url = getEnv("PUBLIC_SUPABASE_URL");
  const serviceKey = getEnv("SUPABASE_SERVICE_KEY");

  return createClient<Database>(url, serviceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}

// ─── Connection check ─────────────────────────────────────────────────────────

/**
 * Returns true if Supabase is configured (env vars present).
 * Used by loaders to decide between Supabase and filesystem fallback.
 */
export function isSupabaseConfigured(): boolean {
  const url = getEnvOptional("PUBLIC_SUPABASE_URL");
  const key = getEnvOptional("PUBLIC_SUPABASE_ANON_KEY");
  return Boolean(url && key);
}
