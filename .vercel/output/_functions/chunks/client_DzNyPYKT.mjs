import { createClient } from '@supabase/supabase-js';

const __vite_import_meta_env__ = {"ASSETS_PREFIX": undefined, "BASE_URL": "/", "DEV": false, "MODE": "production", "PROD": true, "PUBLIC_SITE_URL": "https://prisma.film", "PUBLIC_SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNDE2MzEsImV4cCI6MjA4NzYxNzYzMX0.q_fDlajLrMQ1Cbg7o_gwDGPhX8Mt7BwhgXapMkY9jN4", "PUBLIC_SUPABASE_URL": "https://porqyokkphflvqfclvkj.supabase.co", "SITE": "https://prisma.film", "SSR": true};
function getEnv(key) {
  const value = Object.assign(__vite_import_meta_env__, { SUPABASE_URL: "https://porqyokkphflvqfclvkj.supabase.co", SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjA0MTYzMSwiZXhwIjoyMDg3NjE3NjMxfQ.pEoWQcmDq-YfFJfF2maOjUF9cYulAfa_avOEeKVZVB0", _: process.env._ })[key];
  if (!value) {
    throw new Error(
      `Missing required environment variable: ${key}
Add it to .env.local (server-side: no PUBLIC_ prefix, build-time only)
or to .env.local with PUBLIC_ prefix for client-safe variables.`
    );
  }
  return value;
}
function getEnvOptional(key) {
  return Object.assign(__vite_import_meta_env__, { SUPABASE_URL: "https://porqyokkphflvqfclvkj.supabase.co", SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjA0MTYzMSwiZXhwIjoyMDg3NjE3NjMxfQ.pEoWQcmDq-YfFJfF2maOjUF9cYulAfa_avOEeKVZVB0", _: process.env._ })[key];
}
function createServiceClient() {
  const url = getEnv("PUBLIC_SUPABASE_URL");
  const serviceKey = getEnv("SUPABASE_SERVICE_KEY");
  return createClient(url, serviceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  });
}
function isSupabaseConfigured() {
  const url = getEnvOptional("PUBLIC_SUPABASE_URL");
  const key = getEnvOptional("PUBLIC_SUPABASE_ANON_KEY");
  return Boolean(url && key);
}

export { createServiceClient as c, isSupabaseConfigured as i };
