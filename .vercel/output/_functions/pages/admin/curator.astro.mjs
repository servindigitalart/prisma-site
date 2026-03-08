/* empty css                                     */
import { f as createComponent, k as renderComponent, r as renderTemplate, m as maybeRenderHead, l as renderScript, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_CKaj1kxH.mjs';
import { P as PRISMA_PALETTE } from '../../chunks/colorPalette_MBD9-pHi.mjs';
export { renderers } from '../../renderers.mjs';

const $$Curator = createComponent(async ($$result, $$props, $$slots) => {
  const db = createServiceClient();
  const { data: assignments, error } = await db.from("color_assignments").select(`
    work_id,
    color_iconico,
    colores_secundarios,
    color_rank,
    review_status,
    editorial_override,
    updated_at,
    works!inner (
      title,
      year
    )
  `).order("updated_at", { ascending: false });
  if (error) {
    console.error("[admin/curator] Error fetching color assignments:", error);
  }
  const colorAssignments = assignments ?? [];
  const paletteArray = Object.values(PRISMA_PALETTE);
  return renderTemplate`${renderComponent($$result, "Layout", $$BaseLayout, { "title": "Color Curator \u2014 PRISMA Admin" }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="max-w-7xl mx-auto px-4 py-12"> <header class="mb-12"> <h1 class="text-4xl font-bold mb-4">Color Curator</h1> <p class="text-gray-400">
Editorial override interface for AI-assigned color identities.
        Changes made here take precedence over pipeline results.
</p> </header> ${colorAssignments.length === 0 ? renderTemplate`<div class="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-6"> <p class="text-yellow-200">
⚠️ No color assignments found. Run the pipeline first.
</p> </div>` : renderTemplate`<div class="space-y-4"> ${colorAssignments.map((assignment) => {
    const work = assignment.works;
    const currentColor = PRISMA_PALETTE[assignment.color_iconico];
    const hasOverride = assignment.editorial_override !== null;
    return renderTemplate`<article class="bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-6"${addAttribute(assignment.work_id, "data-work-id")}> <div class="flex items-start justify-between gap-6">  <div class="flex-1"> <h2 class="text-2xl font-semibold mb-2"> ${work.title} (${work.year})
</h2> <div class="flex items-center gap-4 text-sm text-gray-400"> <span class="capitalize bg-blue-900/30 text-blue-200 px-2 py-1 rounded"> ${assignment.review_status.replace(/_/g, " ")} </span> ${hasOverride && renderTemplate`<span class="bg-purple-900/30 text-purple-200 px-2 py-1 rounded">
✎ Editorial Override
</span>`} <span>
Confidence: ${assignment.color_rank ? (assignment.color_rank * 100).toFixed(0) : "0"}%
</span> <span class="text-xs text-gray-500">
Updated: ${assignment.updated_at ? new Date(assignment.updated_at).toLocaleDateString() : "N/A"} </span> </div> </div>  <div class="flex flex-col items-center gap-2"> <div class="w-20 h-20 rounded-lg border-2 border-white/20 shadow-lg"${addAttribute(`background-color: ${currentColor?.hex || "#4A4A4A"}`, "style")}></div> <span class="text-xs text-gray-400 text-center"> ${currentColor?.name || assignment.color_iconico} </span> </div> </div>  <details class="mt-6"> <summary class="cursor-pointer text-sm text-gray-400 hover:text-gray-200 transition-colors">
▸ Edit Color Assignment
</summary> <form class="mt-6 space-y-6 override-form"> <input type="hidden" name="work_id"${addAttribute(assignment.work_id, "value")}>  <div> <label class="block text-sm font-medium text-gray-300 mb-3">
Primary Color
</label> <div class="grid grid-cols-6 gap-3"> ${paletteArray.map((color) => renderTemplate`<label class="cursor-pointer group"> <input type="radio" name="color_iconico"${addAttribute(color.id, "value")}${addAttribute(color.id === assignment.color_iconico, "checked")} class="sr-only peer"> <div class="flex flex-col items-center gap-2"> <div class="w-12 h-12 rounded-lg border-2 transition-all
                                     peer-checked:border-white peer-checked:ring-2 peer-checked:ring-white/50
                                     group-hover:scale-110"${addAttribute(`background-color: ${color.hex}; border-color: ${color.id === assignment.color_iconico ? "white" : "rgba(255,255,255,0.2)"}`, "style")}></div> <span class="text-[10px] text-gray-500 text-center leading-tight max-w-[60px]"> ${color.name} </span> </div> </label>`)} </div> </div>  <div> <label class="block text-sm font-medium text-gray-300 mb-3">
Secondary Colors (max 2)
</label> <div class="grid grid-cols-6 gap-3"> ${paletteArray.map((color) => renderTemplate`<label class="cursor-pointer group"> <input type="checkbox" name="colores_secundarios"${addAttribute(color.id, "value")}${addAttribute(assignment.colores_secundarios?.includes(color.id), "checked")} class="sr-only peer secondary-checkbox"> <div class="flex flex-col items-center gap-2"> <div class="w-12 h-12 rounded-lg border-2 transition-all
                                     peer-checked:border-white peer-checked:ring-2 peer-checked:ring-white/50
                                     group-hover:scale-110"${addAttribute(`background-color: ${color.hex}; border-color: ${assignment.colores_secundarios?.includes(color.id) ? "white" : "rgba(255,255,255,0.2)"}`, "style")}></div> <span class="text-[10px] text-gray-500 text-center leading-tight max-w-[60px]"> ${color.name} </span> </div> </label>`)} </div> </div>  <div> <label class="block text-sm font-medium text-gray-300 mb-2">
Editorial Note (why this override?)
</label> <textarea name="editorial_note" rows="3" class="w-full bg-[var(--surface-elevated)] border border-[var(--surface-border)] 
                             rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:ring-2 
                             focus:ring-blue-500 resize-none" placeholder="e.g., 'Film is visually dominated by red cheongsams and amber lighting, not blue melancholy'">${assignment.editorial_override?.note || ""}</textarea> </div>  <div class="flex gap-3"> <button type="submit" class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded font-medium 
                             transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
✓ Save Override
</button> <button type="button" class="bg-gray-700 hover:bg-gray-600 text-gray-200 px-6 py-2 rounded font-medium 
                             transition-colors reset-form">
Reset
</button> </div> <div class="save-status hidden"></div> </form> </details> </article>`;
  })} </div>`} <div class="mt-12 bg-blue-900/20 border border-blue-700/50 rounded-lg p-6"> <h3 class="font-semibold mb-2 text-blue-200">Curator Guidelines</h3> <ul class="text-sm text-blue-100/80 space-y-1 list-disc list-inside"> <li>Override when AI assigns color based on emotional symbolism instead of visual dominance</li> <li>Example: "In the Mood for Love" (2000) should be red (cheongsams), not blue (melancholy)</li> <li>Always provide a clear editorial note explaining the visual evidence</li> <li>Secondary colors should support the primary (max 2 recommended)</li> <li>Overrides are permanent until manually changed — they persist across pipeline re-runs</li> </ul> </div> </main> ${renderScript($$result2, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/curator.astro?astro&type=script&index=0&lang.ts")} ` })}`;
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/curator.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/curator.astro";
const $$url = "/admin/curator";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Curator,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
