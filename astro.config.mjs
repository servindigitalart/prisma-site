// @ts-check
import { defineConfig } from "astro/config";
import vercel from "@astrojs/vercel";
import react from "@astrojs/react";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

// https://astro.build/config
export default defineConfig({
  // ─── Canonical site URL ──────────────────────────────────────────────────
  site: "https://prisma.film",

  // ─── Hybrid rendering ────────────────────────────────────────────────────
  // Astro v5 removed the "hybrid" output mode. Use "server" to enable SSR,
  // then opt individual pages into static prerendering:
  //   - Pages with getStaticPaths() are always prerendered automatically.
  //   - Add `export const prerender = true` to any other static page.
  //   - SSR-only pages (auth, dashboard, API routes) need nothing extra.
  // See: https://docs.astro.build/en/guides/on-demand-rendering/
  output: "server",
  adapter: vercel({
    // Enable Edge Middleware for faster auth checks globally
    edgeMiddleware: false,
    // Image optimization via Vercel's image CDN
    imageService: true,
    // ISR: stale-while-revalidate for SSR pages (seconds)
    // Film pages are static so this mainly applies to API routes
    isr: false,
  }),

  // ─── Integrations ────────────────────────────────────────────────────────
  integrations: [
    // React: for interactive islands (ratings, reviews, sharing cards)
    react(),

    // Tailwind: utility-first CSS, mobile-first
    tailwind({
      // Allow Tailwind classes alongside Astro component CSS
      applyBaseStyles: true,
    }),

    // Sitemap: auto-generated XML sitemap at /sitemap-index.xml
    sitemap({
      // Exclude admin, auth, and API routes from sitemap
      filter: (page) =>
        !page.includes("/admin/") &&
        !page.includes("/auth/") &&
        !page.includes("/api/"),
      // Custom change frequencies for different page types
      customPages: [],
    }),
  ],

  // ─── Image optimization ───────────────────────────────────────────────────
  image: {
    // Allow images from TMDB CDN and Supabase Storage
    domains: [
      "image.tmdb.org",
      // Supabase Storage domain (replaced by your project ID at setup)
      // e.g. "abcdefghijklmnop.supabase.co"
    ],
    // Vercel image optimization handles remote images via the adapter
    // Set fallback service for local dev
    service: {
      entrypoint: "astro/assets/services/sharp",
    },
  },

  // ─── Build configuration ─────────────────────────────────────────────────
  build: {
    // Split output into per-page chunks for better caching
    inlineStylesheets: "auto",
  },

  // ─── Development server ───────────────────────────────────────────────────
  server: {
    port: 4321,
    host: false, // localhost only
  },

  // ─── Vite configuration ──────────────────────────────────────────────────
  vite: {
    // Optimize Supabase for SSR (avoid Node.js-only imports in browser bundles)
    ssr: {
      noExternal: [],
    },
    // Suppress warnings from dependencies during dev
    build: {
      rollupOptions: {
        onwarn(warning, warn) {
          // Suppress "use client" directive warnings from React packages
          if (warning.code === "MODULE_LEVEL_DIRECTIVE") return;
          warn(warning);
        },
      },
    },
  },
});
