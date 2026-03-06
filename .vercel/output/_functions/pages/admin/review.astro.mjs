/* empty css                                     */
import { f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_QHw3iGXw.mjs';
/* empty css                                     */
export { renderers } from '../../renderers.mjs';

const $$Review = createComponent(async ($$result, $$props, $$slots) => {
  const db = createServiceClient();
  const { data: articles, error } = await db.from("generated_articles").select("*").eq("is_published", false).order("generated_at", { ascending: false });
  if (error) {
    console.error("[admin/review] Error fetching articles:", error);
  }
  const pendingArticles = articles ?? [];
  return renderTemplate`${renderComponent($$result, "Layout", $$BaseLayout, { "title": "Review Queue \u2014 PRISMA Admin", "data-astro-cid-47e4x3dr": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="max-w-6xl mx-auto px-4 py-12" data-astro-cid-47e4x3dr> <header class="mb-12" data-astro-cid-47e4x3dr> <h1 class="text-4xl font-bold mb-4" data-astro-cid-47e4x3dr>pSEO Content Review Queue</h1> <p class="text-gray-600" data-astro-cid-47e4x3dr>
Articles awaiting editorial approval before publication.
</p> </header> ${pendingArticles.length === 0 ? renderTemplate`<div class="bg-green-50 border border-green-200 rounded-lg p-6" data-astro-cid-47e4x3dr> <p class="text-green-800" data-astro-cid-47e4x3dr>
✅ All clear! No articles pending review.
</p> </div>` : renderTemplate`<div class="space-y-6" data-astro-cid-47e4x3dr> ${pendingArticles.map((article) => renderTemplate`<article class="bg-white border border-gray-200 rounded-lg p-6" data-astro-cid-47e4x3dr> <div class="flex items-start justify-between mb-4" data-astro-cid-47e4x3dr> <div class="flex-1" data-astro-cid-47e4x3dr> <h2 class="text-2xl font-semibold mb-2" data-astro-cid-47e4x3dr>${article.title}</h2> <div class="flex items-center gap-4 text-sm text-gray-600" data-astro-cid-47e4x3dr> <span class="capitalize bg-blue-100 text-blue-800 px-2 py-1 rounded" data-astro-cid-47e4x3dr> ${article.template_type?.replace(/_/g, " ")} </span> <span data-astro-cid-47e4x3dr>${article.word_count} words</span> <span data-astro-cid-47e4x3dr>
Generated: ${article.generated_at ? new Date(article.generated_at).toLocaleDateString() : "Unknown"} </span> </div> </div> </div> ${article.excerpt && renderTemplate`<p class="text-gray-700 mb-4 line-clamp-3" data-astro-cid-47e4x3dr>${article.excerpt}</p>`} <div class="flex gap-3" data-astro-cid-47e4x3dr> <form action="/api/admin/approve-article" method="POST" data-astro-cid-47e4x3dr> <input type="hidden" name="article_id"${addAttribute(article.id, "value")} data-astro-cid-47e4x3dr> <button type="submit" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded font-medium transition-colors" data-astro-cid-47e4x3dr>
✓ Approve & Publish
</button> </form> <form action="/api/admin/reject-article" method="POST" data-astro-cid-47e4x3dr> <input type="hidden" name="article_id"${addAttribute(article.id, "value")} data-astro-cid-47e4x3dr> <button type="submit" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded font-medium transition-colors" data-astro-cid-47e4x3dr>
✗ Reject (back to draft)
</button> </form> <a${addAttribute(`/admin/review/${article.id}`, "href")} class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded font-medium transition-colors" data-astro-cid-47e4x3dr>
View Full Article
</a> </div> </article>`)} </div>`} <div class="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6" data-astro-cid-47e4x3dr> <h3 class="font-semibold mb-2" data-astro-cid-47e4x3dr>Review Guidelines</h3> <ul class="text-sm text-gray-700 space-y-1 list-disc list-inside" data-astro-cid-47e4x3dr> <li data-astro-cid-47e4x3dr>Minimum 800 words required for publication</li> <li data-astro-cid-47e4x3dr>Check for keyword stuffing or unnatural language</li> <li data-astro-cid-47e4x3dr>Verify all film/person/color links are correct</li> <li data-astro-cid-47e4x3dr>Ensure intro and closing paragraphs are editorial (not AI-generated)</li> <li data-astro-cid-47e4x3dr>Confirm no duplicate H1s across published articles</li> </ul> </div> </main> ` })} `;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/review.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/review.astro";
const $$url = "/admin/review";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Review,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
