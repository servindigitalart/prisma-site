/* empty css                                        */
import { e as createAstro, f as createComponent, r as renderTemplate, n as defineScriptVars, k as renderComponent, m as maybeRenderHead, h as addAttribute, o as Fragment } from '../../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../../chunks/BaseLayout_QHw3iGXw.mjs';
import { r as requireAdmin } from '../../../chunks/admin_DmZOtt0Z.mjs';
import { c as createServiceClient } from '../../../chunks/client_DzNyPYKT.mjs';
/* empty css                                      */
export { renderers } from '../../../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$id = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$id;
  const isAdmin = await requireAdmin(Astro2.locals);
  if (!isAdmin) return Astro2.redirect("/");
  const { id } = Astro2.params;
  if (!id) return Astro2.redirect("/admin/submissions");
  const db = createServiceClient();
  const { data: sub } = await db.from("film_submissions").select("*").eq("id", Number(id)).maybeSingle();
  if (!sub) return Astro2.redirect("/admin/submissions");
  const credits = sub.ficha_credits || {};
  const bioFull = sub.ficha_bio_full || "";
  const filmmakerPhoto = sub.ficha_filmmaker_photo || "";
  const filmmakerWebsite = sub.ficha_filmmaker_website || "";
  const filmmakerInstagram = sub.ficha_filmmaker_instagram || "";
  const fichaCountries = sub.ficha_countries || [];
  const fichaLanguages = sub.ficha_languages || [];
  const fichaGenres = sub.ficha_genres || [];
  const synopsisFull = sub.ficha_synopsis_full || "";
  const fichaSubmittedAt = sub.ficha_submitted_at || "";
  const metaLines = (sub.reviewer_notes || "").split("\n");
  const contentType = metaLines.find((l) => l.startsWith("Content type:"))?.replace("Content type: ", "") || "";
  const roleLabels = {
    director: "Director",
    writer: "Writer",
    cinematographer: "Cinematographer",
    editor: "Editor",
    music: "Music / Composer",
    cast: "Cast"
  };
  const roleToDbRole = {
    director: "director",
    writer: "writer",
    cinematographer: "cinematography",
    editor: "editor",
    music: "composer",
    cast: "actor"
  };
  const typeMapping = {
    short: "short",
    feature: "film",
    series: "series",
    music_video: "music_video"
  };
  const workType = typeMapping[contentType] || "film";
  const suggestedSlug = sub.title.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  const hasFichaData = Object.keys(credits).length > 0 || bioFull || synopsisFull;
  let workRecord = null;
  if (sub.work_id) {
    const { data } = await db.from("works").select("id, streaming_id, streaming_type, is_streamable").eq("id", sub.work_id).maybeSingle();
    workRecord = data;
  }
  return renderTemplate(_a || (_a = __template(["", " <script>(function(){", `
(function() {
  var form = document.getElementById('publish-form');
  if (!form) return;

  var publishBtn = document.getElementById('publish-btn');
  var errorEl = document.getElementById('publish-error');
  var successEl = document.getElementById('publish-success');

  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    errorEl.hidden = true;
    successEl.hidden = true;

    if (!confirm('Are you sure you want to publish this work to the catalog? This will create database records.')) {
      return;
    }

    publishBtn.disabled = true;
    publishBtn.textContent = 'Publishing\u2026';

    try {
      var fd = new FormData(form);
      var slug = fd.get('slug');
      var workType = fd.get('work_type');

      // Collect people data from the form
      var personEntries = document.querySelectorAll('.person-entry');
      var people = [];
      personEntries.forEach(function(el) {
        var role = el.dataset.role;
        var alsoRoles = JSON.parse(el.dataset.alsoRoles || '[]');
        var idInput = el.querySelector('.person-id-input');
        var nameInput = el.querySelectorAll('input')[1];
        people.push({
          person_id: idInput.value.trim(),
          name: nameInput.value.trim(),
          role: role,
          also_roles: alsoRoles
        });
      });

      var res = await fetch('/api/admin/publish/' + submissionId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug: slug, work_type: workType, people: people })
      });

      var result = await res.json();

      if (res.ok && result.success) {
        successEl.innerHTML = '\u2726 Published! <a href="/films/' + slug + '">View on site \u2192</a>';
        successEl.hidden = false;
        publishBtn.textContent = 'Published';
        form.querySelectorAll('input, select, button').forEach(function(el) { el.disabled = true; });
      } else {
        errorEl.textContent = result.error || 'Error publishing. Check console.';
        errorEl.hidden = false;
        publishBtn.disabled = false;
        publishBtn.textContent = 'Publish to Catalog';
      }
    } catch (err) {
      errorEl.textContent = 'Network error. Check connection.';
      errorEl.hidden = false;
      publishBtn.disabled = false;
      publishBtn.textContent = 'Publish to Catalog';
    }
  });
})();

// \u2500\u2500 Bunny Stream \u2500\u2500
(function() {
  // Create video slot
  var createBtn = document.getElementById('btn-create-bunny');
  if (createBtn) {
    createBtn.addEventListener('click', async function() {
      createBtn.disabled = true;
      createBtn.textContent = 'Creating\u2026';
      try {
        var res = await fetch('/api/admin/bunny-upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            submission_id: Number(createBtn.dataset.submissionId),
            title: createBtn.dataset.title
          })
        });
        var data = await res.json();
        if (data.videoId) {
          document.getElementById('bunny-video-id-display').textContent = data.videoId;
          document.getElementById('bunny-result').hidden = false;
          createBtn.textContent = '\u2713 Slot created';
        } else {
          alert('Error: ' + (data.error || 'Unknown error'));
          createBtn.disabled = false;
          createBtn.textContent = 'Create Bunny Video Slot';
        }
      } catch (err) {
        alert('Network error');
        createBtn.disabled = false;
        createBtn.textContent = 'Create Bunny Video Slot';
      }
    });
  }

  // Mark as streamable
  var streamBtn = document.getElementById('btn-mark-streamable');
  if (streamBtn) {
    streamBtn.addEventListener('click', async function() {
      if (!confirm('Mark this work as streamable? The player will appear on the film page.')) return;
      streamBtn.disabled = true;
      streamBtn.textContent = 'Updating\u2026';
      try {
        var res = await fetch('/api/admin/submissions/' + submissionId, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mark_streamable: true, work_id: streamBtn.dataset.workId })
        });
        if (res.ok) {
          location.reload();
        } else {
          var data = await res.json();
          alert('Error: ' + (data.error || 'Unknown error'));
          streamBtn.disabled = false;
          streamBtn.textContent = 'Mark as Streamable';
        }
      } catch (err) {
        alert('Network error');
        streamBtn.disabled = false;
        streamBtn.textContent = 'Mark as Streamable';
      }
    });
  }
})();
})();<\/script> `])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": `Review Ficha \u2014 ${sub.title}`, "data-astro-cid-5ui57533": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="admin-ficha" data-astro-cid-5ui57533> <a href="/admin/submissions" class="back-link" data-astro-cid-5ui57533>← Back to submissions</a> <header class="ficha-header" data-astro-cid-5ui57533> <h1 data-astro-cid-5ui57533>${sub.title}</h1> <div class="ficha-meta" data-astro-cid-5ui57533> <span class="meta-item" data-astro-cid-5ui57533>${sub.filmmaker_name}</span> <span class="meta-item" data-astro-cid-5ui57533>${sub.year || "\u2014"}</span> ${sub.runtime_min && renderTemplate`<span class="meta-item" data-astro-cid-5ui57533>${sub.runtime_min} min</span>`} <span class="status-badge"${addAttribute(sub.status, "data-status")} data-astro-cid-5ui57533>${sub.status.replace("_", " ")}</span> </div> ${fichaSubmittedAt && renderTemplate`<p class="ficha-date" data-astro-cid-5ui57533>Ficha submitted ${new Date(fichaSubmittedAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" })}</p>`} </header> ${!hasFichaData ? renderTemplate`<div class="empty-state" data-astro-cid-5ui57533> <p data-astro-cid-5ui57533>No ficha data has been submitted yet for this work.</p> <p data-astro-cid-5ui57533>Current status: <strong data-astro-cid-5ui57533>${sub.status}</strong></p> </div>` : renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-5ui57533": true }, { "default": async ($$result3) => renderTemplate`<section class="review-section" data-astro-cid-5ui57533> <h2 data-astro-cid-5ui57533>Filmmaker</h2> <div class="filmmaker-card" data-astro-cid-5ui57533> ${filmmakerPhoto && renderTemplate`<img${addAttribute(filmmakerPhoto, "src")}${addAttribute(sub.filmmaker_name, "alt")} class="filmmaker-photo" data-astro-cid-5ui57533>`} <div class="filmmaker-details" data-astro-cid-5ui57533> <h3 data-astro-cid-5ui57533>${sub.filmmaker_name}</h3> <p class="filmmaker-email" data-astro-cid-5ui57533>${sub.filmmaker_email}</p> ${filmmakerWebsite && renderTemplate`<a${addAttribute(filmmakerWebsite, "href")} target="_blank" rel="noopener" class="filmmaker-link" data-astro-cid-5ui57533>${filmmakerWebsite}</a>`} ${filmmakerInstagram && renderTemplate`<a${addAttribute(filmmakerInstagram, "href")} target="_blank" rel="noopener" class="filmmaker-link" data-astro-cid-5ui57533>${filmmakerInstagram}</a>`} </div> </div> ${bioFull && renderTemplate`<div class="bio-block" data-astro-cid-5ui57533> <h4 data-astro-cid-5ui57533>Biography</h4> <p data-astro-cid-5ui57533>${bioFull}</p> </div>`} </section> <section class="review-section" data-astro-cid-5ui57533> <h2 data-astro-cid-5ui57533>Credits</h2> ${Object.keys(credits).length === 0 ? renderTemplate`<p class="empty-note" data-astro-cid-5ui57533>No credits submitted.</p>` : Object.entries(credits).map(([role, entries]) => renderTemplate`<div class="credit-group" data-astro-cid-5ui57533> <h3 data-astro-cid-5ui57533>${roleLabels[role] || role} <span class="db-role" data-astro-cid-5ui57533>→ ${roleToDbRole[role] || role}</span></h3> <div class="credit-list" data-astro-cid-5ui57533> ${entries.map((entry, i) => renderTemplate`<div class="credit-card" data-astro-cid-5ui57533> ${entry.photo_url && renderTemplate`<img${addAttribute(entry.photo_url, "src")}${addAttribute(entry.name, "alt")} class="credit-photo" data-astro-cid-5ui57533>`} <div class="credit-info" data-astro-cid-5ui57533> <span class="credit-name" data-astro-cid-5ui57533>${entry.name}</span> ${entry.bio && renderTemplate`<p class="credit-bio" data-astro-cid-5ui57533>${entry.bio}</p>`} ${entry.also && entry.also.length > 0 && renderTemplate`<span class="credit-also" data-astro-cid-5ui57533>Also: ${entry.also.map((r) => roleLabels[r] || r).join(", ")}</span>`} </div> </div>`)} </div> </div>`)} </section> <section class="review-section" data-astro-cid-5ui57533> <h2 data-astro-cid-5ui57533>Work Details</h2> <div class="detail-grid" data-astro-cid-5ui57533> <div class="detail-item" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Countries</span> <span class="detail-value" data-astro-cid-5ui57533>${fichaCountries.length > 0 ? fichaCountries.join(", ") : "\u2014"}</span> </div> <div class="detail-item" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Languages</span> <span class="detail-value" data-astro-cid-5ui57533>${fichaLanguages.length > 0 ? fichaLanguages.join(", ") : "\u2014"}</span> </div> <div class="detail-item" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Genres</span> <span class="detail-value" data-astro-cid-5ui57533>${fichaGenres.length > 0 ? fichaGenres.join(", ") : "\u2014"}</span> </div> <div class="detail-item detail-item--full" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Full Synopsis</span> <p class="detail-value" data-astro-cid-5ui57533>${synopsisFull || "\u2014"}</p> </div> </div> </section> <section class="review-section publish-section" data-astro-cid-5ui57533> <h2 data-astro-cid-5ui57533>Publish to Catalog</h2> <p class="publish-help" data-astro-cid-5ui57533>
Review all data above. Publishing will create a <code data-astro-cid-5ui57533>work</code> record, <code data-astro-cid-5ui57533>people</code> records (if they don't exist), and <code data-astro-cid-5ui57533>work_people</code> entries. The submission status will change to <strong data-astro-cid-5ui57533>published</strong>.
</p> <form id="publish-form" class="publish-form" data-astro-cid-5ui57533> <div class="form-field" data-astro-cid-5ui57533> <label for="p-slug" data-astro-cid-5ui57533>Work slug</label> <div class="slug-preview" data-astro-cid-5ui57533> <span class="slug-prefix" data-astro-cid-5ui57533>work_</span> <input type="text" id="p-slug" name="slug"${addAttribute(suggestedSlug, "value")} required data-astro-cid-5ui57533> </div> <span class="form-hint" data-astro-cid-5ui57533>URL will be: /films/${suggestedSlug}</span> </div> <div class="form-field" data-astro-cid-5ui57533> <label for="p-work-type" data-astro-cid-5ui57533>Type</label> <select id="p-work-type" name="work_type" data-astro-cid-5ui57533> <option value="film"${addAttribute(workType === "film", "selected")} data-astro-cid-5ui57533>Film</option> <option value="short"${addAttribute(workType === "short", "selected")} data-astro-cid-5ui57533>Short</option> <option value="series"${addAttribute(workType === "series", "selected")} data-astro-cid-5ui57533>Series</option> <option value="music_video"${addAttribute(workType === "music_video", "selected")} data-astro-cid-5ui57533>Music Video</option> </select> </div> <h3 class="subsection-title" data-astro-cid-5ui57533>People Linking</h3> <p class="publish-help" data-astro-cid-5ui57533>
For each person, you can link to an existing person record or create a new one.
              Leave the ID field blank to auto-generate from their name.
</p> <div id="people-entries" data-astro-cid-5ui57533> ${Object.entries(credits).flatMap(
    ([role, entries]) => entries.map((entry, i) => {
      const personSlug = entry.name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
      const suggestedId = `person_${personSlug}`;
      const dbRole = roleToDbRole[role] || role;
      const alsoRoles = (entry.also || []).map((r) => roleToDbRole[r] || r);
      return renderTemplate`<div class="person-entry"${addAttribute(dbRole, "data-role")}${addAttribute(JSON.stringify(alsoRoles), "data-also-roles")} data-astro-cid-5ui57533> <div class="person-entry__header" data-astro-cid-5ui57533> <strong data-astro-cid-5ui57533>${entry.name}</strong> <span class="person-role-tag" data-astro-cid-5ui57533>${roleLabels[role] || role}</span> ${alsoRoles.length > 0 && renderTemplate`<span class="person-also-tag" data-astro-cid-5ui57533>+ ${alsoRoles.join(", ")}</span>`} </div> <div class="person-entry__fields" data-astro-cid-5ui57533> <div class="form-field form-field--inline" data-astro-cid-5ui57533> <label data-astro-cid-5ui57533>Person ID</label> <input type="text"${addAttribute(`person_id_${role}_${i}`, "name")}${addAttribute(suggestedId, "value")} class="person-id-input" data-astro-cid-5ui57533> </div> <div class="form-field form-field--inline" data-astro-cid-5ui57533> <label data-astro-cid-5ui57533>Name (as stored)</label> <input type="text"${addAttribute(`person_name_${role}_${i}`, "name")}${addAttribute(entry.name, "value")} data-astro-cid-5ui57533> </div> </div> </div>`;
    })
  )} </div> <div class="publish-actions" data-astro-cid-5ui57533> <button type="submit" class="publish-btn" id="publish-btn" data-astro-cid-5ui57533>
Publish to Catalog
</button> </div> </form> <div class="form-message form-message--error" id="publish-error" hidden data-astro-cid-5ui57533></div> <div class="form-message form-message--success" id="publish-success" hidden data-astro-cid-5ui57533></div> </section> ` })}`}  ${sub.work_id && renderTemplate`<section class="review-section bunny-section" data-astro-cid-5ui57533> <h2 data-astro-cid-5ui57533>Upload to Bunny Stream</h2> ${workRecord?.streaming_id ? renderTemplate`<div class="bunny-status" data-astro-cid-5ui57533> <p class="bunny-linked" data-astro-cid-5ui57533>✓ Video linked</p> <div class="detail-grid" data-astro-cid-5ui57533> <div class="detail-item" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Video ID</span> <code class="detail-value" data-astro-cid-5ui57533>${workRecord.streaming_id}</code> </div> <div class="detail-item" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Streamable</span> <span class="detail-value" data-astro-cid-5ui57533>${workRecord.is_streamable ? "\u2713 Yes" : "\u2717 Not yet (upload or encoding pending)"}</span> </div> </div> <div class="bunny-actions" data-astro-cid-5ui57533> <a href="https://dash.bunny.net/stream" target="_blank" rel="noopener" class="action-btn action-btn--subtle" data-astro-cid-5ui57533>
Open Bunny Dashboard ↗
</a> ${!workRecord.is_streamable && renderTemplate`<button class="action-btn action-btn--primary" id="btn-mark-streamable"${addAttribute(sub.work_id, "data-work-id")} data-astro-cid-5ui57533>
Mark as Streamable
</button>`} </div> </div>` : renderTemplate`<div class="bunny-create" data-astro-cid-5ui57533> <p class="publish-help" data-astro-cid-5ui57533>
Create a video slot in Bunny Stream, then upload the file via the Bunny dashboard.
              Once uploaded and encoded, mark the work as streamable to enable the player on the film page.
</p> <button class="action-btn action-btn--accent" id="btn-create-bunny"${addAttribute(sub.id, "data-submission-id")}${addAttribute(sub.title, "data-title")} data-astro-cid-5ui57533>
Create Bunny Video Slot
</button> <div id="bunny-result" hidden data-astro-cid-5ui57533> <div class="detail-grid" style="margin-top: 0.75rem;" data-astro-cid-5ui57533> <div class="detail-item detail-item--full" data-astro-cid-5ui57533> <span class="detail-label" data-astro-cid-5ui57533>Video ID</span> <code class="detail-value" id="bunny-video-id-display" data-astro-cid-5ui57533></code> </div> </div> <p class="publish-help" style="margin-top: 0.75rem;" data-astro-cid-5ui57533>
Video slot created. Upload the file in the Bunny dashboard, then return here to mark it as streamable.
</p> <a href="https://dash.bunny.net/stream" target="_blank" rel="noopener" class="action-btn action-btn--primary" data-astro-cid-5ui57533>
Open Bunny Dashboard to Upload ↗
</a> </div> </div>`} </section>`} </main> ` }), defineScriptVars({ submissionId: sub.id }));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/ficha/[id].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/admin/ficha/[id].astro";
const $$url = "/admin/ficha/[id]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$id,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
