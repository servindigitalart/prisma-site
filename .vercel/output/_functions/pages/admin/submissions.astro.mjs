/* empty css                                     */
import { e as createAstro, f as createComponent, r as renderTemplate, k as renderComponent, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_CKaj1kxH.mjs';
import { r as requireAdmin } from '../../chunks/admin_DmZOtt0Z.mjs';
import { c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
/* empty css                                          */
export { renderers } from '../../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$Submissions = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$Submissions;
  const isAdmin = await requireAdmin(Astro2.locals);
  if (!isAdmin) return Astro2.redirect("/");
  const db = createServiceClient();
  const { data: submissions } = await db.from("film_submissions").select("*").order("submitted_at", { ascending: false });
  const allSubs = submissions || [];
  const statusCounts = {};
  allSubs.forEach((s) => {
    statusCounts[s.status] = (statusCounts[s.status] || 0) + 1;
  });
  const statuses = ["pending", "under_review", "approved", "awaiting_ficha", "ficha_received", "published", "rejected"];
  const statusLabels = {
    pending: "Pending",
    under_review: "Under Review",
    approved: "Approved",
    awaiting_ficha: "Awaiting Ficha",
    ficha_received: "Ficha Received",
    published: "Published",
    rejected: "Rejected"
  };
  const statusColors = {
    pending: "#C98A2E",
    under_review: "#4A90D9",
    approved: "#3dba6f",
    awaiting_ficha: "#D4C9A8",
    ficha_received: "#7BC96F",
    published: "#1F7A5C",
    rejected: "#8E1B1B"
  };
  const typeBadges = {
    short: "SHORT",
    feature: "FILM",
    series: "SERIES",
    music_video: "MUSIC VIDEO"
  };
  return renderTemplate(_a || (_a = __template(["", " <script>\n(function() {\n  // Filter tabs\n  var tabs = document.querySelectorAll('.filter-tab');\n  var cards = document.querySelectorAll('.sub-card');\n  tabs.forEach(function(tab) {\n    tab.addEventListener('click', function() {\n      tabs.forEach(function(t) { t.classList.remove('is-active'); });\n      tab.classList.add('is-active');\n      var filter = tab.dataset.filter;\n      cards.forEach(function(card) {\n        card.style.display = (filter === 'all' || card.dataset.status === filter) ? '' : 'none';\n      });\n    });\n  });\n\n  // Auto-save notes on blur\n  document.querySelectorAll('.notes-textarea').forEach(function(ta) {\n    ta.addEventListener('blur', async function() {\n      var id = ta.dataset.subId;\n      await fetch('/api/admin/submissions/' + id, {\n        method: 'PATCH',\n        headers: { 'Content-Type': 'application/json' },\n        body: JSON.stringify({ reviewer_notes: ta.value })\n      });\n    });\n  });\n\n  // Action buttons\n  document.addEventListener('click', async function(e) {\n    var btn = e.target.closest('[data-action]');\n    if (!btn) return;\n    var action = btn.dataset.action;\n    var id = btn.dataset.subId;\n\n    if (action === 'reject') {\n      var rejectForm = document.getElementById('reject-' + id);\n      if (rejectForm) rejectForm.hidden = false;\n      return;\n    }\n\n    if (action === 'confirm_reject') {\n      var form = document.getElementById('reject-' + id);\n      var reason = form.querySelector('.reject-reason').value.trim();\n      if (!reason) { alert('Please provide a rejection reason.'); return; }\n      btn.disabled = true;\n      var res = await fetch('/api/admin/submissions/' + id, {\n        method: 'PATCH',\n        headers: { 'Content-Type': 'application/json' },\n        body: JSON.stringify({ status: 'rejected', rejection_reason: reason })\n      });\n      if (res.ok) location.reload();\n      else alert('Error: ' + (await res.json()).error);\n      btn.disabled = false;\n      return;\n    }\n\n    if (action === 'send_ficha') {\n      btn.disabled = true;\n      btn.textContent = 'Sending\u2026';\n      var res = await fetch('/api/admin/send-ficha', {\n        method: 'POST',\n        headers: { 'Content-Type': 'application/json' },\n        body: JSON.stringify({ submission_id: Number(id) })\n      });\n      if (res.ok) location.reload();\n      else alert('Error: ' + (await res.json()).error);\n      btn.disabled = false;\n      return;\n    }\n\n    // Status change (under_review, approved)\n    btn.disabled = true;\n    var res = await fetch('/api/admin/submissions/' + id, {\n      method: 'PATCH',\n      headers: { 'Content-Type': 'application/json' },\n      body: JSON.stringify({ status: action })\n    });\n    if (res.ok) location.reload();\n    else alert('Error: ' + (await res.json()).error);\n    btn.disabled = false;\n  });\n})();\n<\/script> "])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Submissions \u2014 PRISMA Admin", "data-astro-cid-cv3lzbmb": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="admin-page" data-astro-cid-cv3lzbmb> <header class="admin-header" data-astro-cid-cv3lzbmb> <h1 data-astro-cid-cv3lzbmb>Submissions</h1> <div class="status-counts" data-astro-cid-cv3lzbmb> ${statuses.map((s) => renderTemplate`<span class="status-count"${addAttribute(`--sc: ${statusColors[s]}`, "style")} data-astro-cid-cv3lzbmb> ${statusLabels[s]}: ${statusCounts[s] || 0} </span>`)} </div> </header> <div class="filter-tabs" id="filter-tabs" data-astro-cid-cv3lzbmb> <button class="filter-tab is-active" data-filter="all" data-astro-cid-cv3lzbmb>All (${allSubs.length})</button> ${statuses.map((s) => renderTemplate`<button class="filter-tab"${addAttribute(s, "data-filter")} data-astro-cid-cv3lzbmb> ${statusLabels[s]} (${statusCounts[s] || 0})
</button>`)} </div> <div class="submissions-list" id="submissions-list" data-astro-cid-cv3lzbmb> ${allSubs.length === 0 && renderTemplate`<p class="empty" data-astro-cid-cv3lzbmb>No submissions yet.</p>`} ${allSubs.map((sub) => {
    const driveLink = sub.storage_path || "";
    const metaLines = (sub.reviewer_notes || "").split("\n");
    const contentType = metaLines.find((l) => l.startsWith("Content type:"))?.replace("Content type: ", "") || "";
    const typeBadge = typeBadges[contentType] || contentType.toUpperCase() || "\u2014";
    const submitted = sub.submitted_at ? new Date(sub.submitted_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }) : "\u2014";
    return renderTemplate`<div class="sub-card"${addAttribute(sub.status, "data-status")}${addAttribute(sub.id, "data-id")} data-astro-cid-cv3lzbmb> <div class="sub-card__header" data-astro-cid-cv3lzbmb> <div class="sub-card__title-row" data-astro-cid-cv3lzbmb> <span class="type-badge" data-astro-cid-cv3lzbmb>${typeBadge}</span> <h3 class="sub-card__title" data-astro-cid-cv3lzbmb>${sub.title}</h3> <span class="sub-card__year" data-astro-cid-cv3lzbmb>${sub.year || "\u2014"}</span> </div> <span class="status-badge"${addAttribute(`--sb: ${statusColors[sub.status]}`, "style")} data-astro-cid-cv3lzbmb> ${statusLabels[sub.status]} </span> </div> <div class="sub-card__meta" data-astro-cid-cv3lzbmb> <span data-astro-cid-cv3lzbmb>${sub.filmmaker_name} · ${sub.filmmaker_email}</span> <span data-astro-cid-cv3lzbmb>Submitted ${submitted}</span> ${sub.runtime_min && renderTemplate`<span data-astro-cid-cv3lzbmb>${sub.runtime_min} min</span>`} </div> <details class="sub-card__synopsis" data-astro-cid-cv3lzbmb> <summary data-astro-cid-cv3lzbmb>Synopsis</summary> <p data-astro-cid-cv3lzbmb>${sub.synopsis || "No synopsis provided."}</p> </details> ${driveLink && renderTemplate`<a${addAttribute(driveLink, "href")} target="_blank" rel="noopener" class="drive-link" data-astro-cid-cv3lzbmb>
Open Drive link ↗
</a>`} <div class="sub-card__notes" data-astro-cid-cv3lzbmb> <label${addAttribute(`notes-${sub.id}`, "for")} data-astro-cid-cv3lzbmb>Reviewer notes</label> <textarea${addAttribute(`notes-${sub.id}`, "id")} class="notes-textarea"${addAttribute(sub.id, "data-sub-id")}${addAttribute(2, "rows")} data-astro-cid-cv3lzbmb>${sub.reviewer_notes || ""}</textarea> </div> <div class="sub-card__actions" data-astro-cid-cv3lzbmb> ${sub.status === "pending" && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-cv3lzbmb": true }, { "default": async ($$result3) => renderTemplate` <button class="action-btn action-btn--primary" data-action="under_review"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Mark as Under Review</button> <button class="action-btn action-btn--danger" data-action="reject"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Reject</button> ` })}`} ${sub.status === "under_review" && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-cv3lzbmb": true }, { "default": async ($$result3) => renderTemplate` <button class="action-btn action-btn--primary" data-action="approved"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Approve</button> <button class="action-btn action-btn--danger" data-action="reject"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Reject</button> ` })}`} ${sub.status === "approved" && renderTemplate`<button class="action-btn action-btn--accent" data-action="send_ficha"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Send Ficha Request</button>`} ${sub.status === "awaiting_ficha" && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-cv3lzbmb": true }, { "default": async ($$result3) => renderTemplate` <span class="ficha-note" data-astro-cid-cv3lzbmb>Ficha requested</span> <button class="action-btn action-btn--accent" data-action="send_ficha"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Resend</button> ` })}`} ${sub.status === "ficha_received" && renderTemplate`<a${addAttribute(`/admin/ficha/${sub.id}`, "href")} class="action-btn action-btn--primary" data-astro-cid-cv3lzbmb>Review Ficha</a>`} ${sub.status === "published" && sub.work_id && renderTemplate`<a${addAttribute(`/films/${sub.work_id.replace(/^work_/, "")}`, "href")} class="action-btn action-btn--subtle" data-astro-cid-cv3lzbmb>View on site ↗</a>`} </div> <div class="reject-form"${addAttribute(`reject-${sub.id}`, "id")} hidden data-astro-cid-cv3lzbmb> <textarea class="reject-reason" placeholder="Reason for rejection…"${addAttribute(2, "rows")} data-astro-cid-cv3lzbmb></textarea> <button class="action-btn action-btn--danger" data-action="confirm_reject"${addAttribute(sub.id, "data-sub-id")} data-astro-cid-cv3lzbmb>Confirm Rejection</button> </div> </div>`;
  })} </div> </main> ` }));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/submissions.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/submissions.astro";
const $$url = "/admin/submissions";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Submissions,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
