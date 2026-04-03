/* empty css                                     */
import { e as createAstro, f as createComponent, r as renderTemplate, k as renderComponent, m as maybeRenderHead, o as Fragment, h as addAttribute } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../../chunks/BaseLayout_BW8MRUf7.mjs';
import { c as createServiceClient } from '../../chunks/client_DzNyPYKT.mjs';
/* empty css                                      */
export { renderers } from '../../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro = createAstro("https://prisma.film");
const prerender = false;
const $$token = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$token;
  const { token } = Astro2.params;
  if (!token) return Astro2.redirect("/404");
  const db = createServiceClient();
  const { data: submission } = await db.from("film_submissions").select("*").eq("ficha_token", token).maybeSingle();
  if (!submission) return Astro2.redirect("/404");
  const isExpired = submission.ficha_token_expires_at && new Date(submission.ficha_token_expires_at) < /* @__PURE__ */ new Date();
  const isPublished = submission.status === "published";
  const isAlreadySubmitted = submission.status === "ficha_received";
  const typeBadges = {
    short: "Cortometraje",
    feature: "Largometraje",
    series: "Serie",
    music_video: "Video musical"
  };
  const metaLines = (submission.reviewer_notes || "").split("\n");
  const contentType = metaLines.find((l) => l.startsWith("Content type:"))?.replace("Content type: ", "") || "";
  const typeLabel = typeBadges[contentType] || contentType || "\u2014";
  const roles = ["director", "writer", "cinematographer", "editor", "music", "cast"];
  const roleLabels = {
    director: "Director",
    writer: "Guionista",
    cinematographer: "Director de fotograf\xEDa",
    editor: "Editor",
    music: "M\xFAsica",
    cast: "Elenco"
  };
  return renderTemplate(_a || (_a = __template(["", ` <script>
(function() {
  var form = document.getElementById('ficha-form');
  if (!form) return;

  var submitBtn = document.getElementById('ficha-submit-btn');
  var errorEl = document.getElementById('ficha-error');
  var successEl = document.getElementById('ficha-success');

  // Character counters
  function bindCounter(fieldId, countId, max) {
    var field = document.getElementById(fieldId);
    var counter = document.getElementById(countId);
    if (field && counter) {
      field.addEventListener('input', function() {
        counter.textContent = field.value.length + '/' + max;
      });
    }
  }
  bindCounter('f-bio-full', 'bio-full-count', 800);
  bindCounter('f-synopsis-full', 'synopsis-full-count', 1000);

  // Add credit entry
  var creditIndex = {};
  document.querySelectorAll('.add-credit').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var role = btn.dataset.role;
      if (!creditIndex[role]) creditIndex[role] = 1;
      else creditIndex[role]++;
      var idx = creditIndex[role];
      var container = document.getElementById('credits-' + role);
      if (!container) return;

      var entry = document.createElement('div');
      entry.className = 'credit-entry';
      entry.innerHTML =
        '<div class="form-field"><label>Nombre completo</label><input type="text" name="credits[' + role + '][' + idx + '][name]" placeholder="Nombre completo" /></div>' +
        '<div class="form-field"><label>Foto</label><input type="file" name="credits[' + role + '][' + idx + '][photo]" accept="image/*" /></div>' +
        '<div class="form-field"><label>Biograf\xEDa breve <span class="form-optional">opcional</span></label><textarea name="credits[' + role + '][' + idx + '][bio]" placeholder="Biograf\xEDa breve (opcional)" maxlength="500" rows="2"></textarea></div>' +
        '<button type="button" class="remove-credit">\u2715 Quitar</button>';
      container.appendChild(entry);

      entry.querySelector('.remove-credit').addEventListener('click', function() {
        entry.remove();
      });
    });
  });

  // Submit
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    errorEl.hidden = true;
    successEl.hidden = true;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando\u2026';

    try {
      var formData = new FormData(form);
      var token = window.location.pathname.split('/').pop();

      var res = await fetch('/api/ficha/' + token, {
        method: 'POST',
        body: formData,
      });

      var result = await res.json();

      if (res.ok && result.success) {
        successEl.innerHTML = '<span style="color:#3dba6f">\u2726</span> Ficha recibida.<br>El equipo de PRISMA revisar\xE1 tu informaci\xF3n y te avisaremos cuando tu obra est\xE9 publicada en el cat\xE1logo.';
        successEl.hidden = false;
        form.style.display = 'none';
        successEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        errorEl.textContent = result.error || 'Error al enviar. Intenta de nuevo.';
        errorEl.hidden = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar ficha t\xE9cnica';
      }
    } catch (err) {
      errorEl.textContent = 'Error de red. Verifica tu conexi\xF3n.';
      errorEl.hidden = false;
      submitBtn.disabled = false;
      submitBtn.textContent = 'Enviar ficha t\xE9cnica';
    }
  });
})();
<\/script> `])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": `Ficha t\xE9cnica \u2014 ${submission.title}`, "description": "Completa la ficha t\xE9cnica de tu obra para PRISMA.", "data-astro-cid-mubuge4t": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="ficha-page" data-astro-cid-mubuge4t> ${isExpired ? renderTemplate`<div class="ficha-notice" data-astro-cid-mubuge4t> <h1 data-astro-cid-mubuge4t>Enlace expirado</h1> <p data-astro-cid-mubuge4t>Este enlace ha expirado. Contacta al equipo de PRISMA para solicitar uno nuevo.</p> </div>` : isPublished ? renderTemplate`<div class="ficha-notice" data-astro-cid-mubuge4t> <h1 data-astro-cid-mubuge4t>Obra ya publicada</h1> <p data-astro-cid-mubuge4t>Tu obra ya fue publicada en el catálogo de PRISMA.</p> </div>` : isAlreadySubmitted ? renderTemplate`<div class="ficha-notice" data-astro-cid-mubuge4t> <h1 data-astro-cid-mubuge4t>Ficha ya recibida</h1> <p data-astro-cid-mubuge4t>Ya recibimos tu ficha técnica. El equipo de PRISMA está revisando tu información.</p> </div>` : renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-mubuge4t": true }, { "default": async ($$result3) => renderTemplate` <header class="ficha-header" data-astro-cid-mubuge4t> <h1 data-astro-cid-mubuge4t>Ficha técnica</h1> <p class="ficha-intro" data-astro-cid-mubuge4t>
Completa la información de tu obra para publicarla en el catálogo de PRISMA.
</p> </header> <form class="ficha-form" id="ficha-form" enctype="multipart/form-data" data-astro-cid-mubuge4t> <!-- Section 1: Tu obra (read-only) --> <fieldset class="form-section" data-astro-cid-mubuge4t> <legend data-astro-cid-mubuge4t>Tu obra</legend> <div class="confirmation-grid" data-astro-cid-mubuge4t> <div class="confirm-item" data-astro-cid-mubuge4t> <span class="confirm-label" data-astro-cid-mubuge4t>Título</span> <span class="confirm-value" data-astro-cid-mubuge4t>${submission.title}</span> </div> <div class="confirm-item" data-astro-cid-mubuge4t> <span class="confirm-label" data-astro-cid-mubuge4t>Tipo</span> <span class="confirm-value" data-astro-cid-mubuge4t>${typeLabel}</span> </div> <div class="confirm-item" data-astro-cid-mubuge4t> <span class="confirm-label" data-astro-cid-mubuge4t>Año</span> <span class="confirm-value" data-astro-cid-mubuge4t>${submission.year || "\u2014"}</span> </div> <div class="confirm-item" data-astro-cid-mubuge4t> <span class="confirm-label" data-astro-cid-mubuge4t>Duración</span> <span class="confirm-value" data-astro-cid-mubuge4t>${submission.runtime_min ? `${submission.runtime_min} min` : "\u2014"}</span> </div> </div> </fieldset> <!-- Section 2: Créditos --> <fieldset class="form-section" data-astro-cid-mubuge4t> <legend data-astro-cid-mubuge4t>Créditos</legend> <p class="section-helper" data-astro-cid-mubuge4t>Agrega las personas que participaron en tu obra. Puedes indicar si una persona tuvo más de un rol.</p> ${roles.map((role) => renderTemplate`<div class="credit-role" data-astro-cid-mubuge4t> <h4 data-astro-cid-mubuge4t>${roleLabels[role]}</h4> <div class="credit-entries"${addAttribute(`credits-${role}`, "id")} data-astro-cid-mubuge4t> <div class="credit-entry" data-astro-cid-mubuge4t> <div class="form-field" data-astro-cid-mubuge4t> <label data-astro-cid-mubuge4t>Nombre completo</label> <input type="text"${addAttribute(`credits[${role}][0][name]`, "name")} placeholder="Nombre completo" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label data-astro-cid-mubuge4t>Foto</label> <input type="file"${addAttribute(`credits[${role}][0][photo]`, "name")} accept="image/*" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label data-astro-cid-mubuge4t>Biografía breve <span class="form-optional" data-astro-cid-mubuge4t>opcional</span></label> <textarea${addAttribute(`credits[${role}][0][bio]`, "name")} placeholder="Biografía breve (opcional)" maxlength="500"${addAttribute(2, "rows")} data-astro-cid-mubuge4t></textarea> </div> ${role !== "cast" && renderTemplate`<div class="also-roles" data-astro-cid-mubuge4t> <label class="also-label" data-astro-cid-mubuge4t>También acreditado como:</label> <div class="also-checks" data-astro-cid-mubuge4t> ${roles.filter((r) => r !== role && r !== "cast").map((r) => renderTemplate`<label class="also-check" data-astro-cid-mubuge4t> <input type="checkbox"${addAttribute(`credits[${role}][0][also][${r}]`, "name")} data-astro-cid-mubuge4t> ${roleLabels[r]} </label>`)} </div> </div>`} </div> </div> <button type="button" class="add-credit"${addAttribute(role, "data-role")} data-astro-cid-mubuge4t>+ Agregar otro ${roleLabels[role].toLowerCase()}</button> </div>`)} </fieldset> <!-- Section 3: Sobre ti --> <fieldset class="form-section" data-astro-cid-mubuge4t> <legend data-astro-cid-mubuge4t>Sobre ti</legend> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-bio-full" data-astro-cid-mubuge4t>Biografía completa</label> <textarea id="f-bio-full" name="bio_full" maxlength="800"${addAttribute(4, "rows")} placeholder="Tu biografía completa…" data-astro-cid-mubuge4t></textarea> <span class="char-count" id="bio-full-count" data-astro-cid-mubuge4t>0/800</span> </div> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-filmmaker-photo" data-astro-cid-mubuge4t>Foto de perfil</label> <input type="file" id="f-filmmaker-photo" name="filmmaker_photo" accept="image/*" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-website" data-astro-cid-mubuge4t>Sitio web <span class="form-optional" data-astro-cid-mubuge4t>opcional</span></label> <input type="url" id="f-website" name="filmmaker_website" placeholder="https://…" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-instagram" data-astro-cid-mubuge4t>Instagram <span class="form-optional" data-astro-cid-mubuge4t>opcional</span></label> <input type="url" id="f-instagram" name="filmmaker_instagram" placeholder="https://instagram.com/…" data-astro-cid-mubuge4t> </div> </fieldset> <!-- Section 4: Tu obra en detalle --> <fieldset class="form-section" data-astro-cid-mubuge4t> <legend data-astro-cid-mubuge4t>Tu obra en detalle</legend> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-countries" data-astro-cid-mubuge4t>Países <span class="form-helper-inline" data-astro-cid-mubuge4t>separados por coma</span></label> <input type="text" id="f-countries" name="countries" placeholder="México, España, Francia…" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-languages" data-astro-cid-mubuge4t>Idiomas <span class="form-helper-inline" data-astro-cid-mubuge4t>separados por coma</span></label> <input type="text" id="f-languages" name="languages" placeholder="Español, Inglés…" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-genres" data-astro-cid-mubuge4t>Géneros <span class="form-helper-inline" data-astro-cid-mubuge4t>separados por coma</span></label> <input type="text" id="f-genres" name="genres" placeholder="Drama, Experimental…" data-astro-cid-mubuge4t> </div> <div class="form-field" data-astro-cid-mubuge4t> <label for="f-synopsis-full" data-astro-cid-mubuge4t>Sinopsis completa</label> <textarea id="f-synopsis-full" name="synopsis_full" maxlength="1000"${addAttribute(5, "rows")} placeholder="Sinopsis detallada…" data-astro-cid-mubuge4t></textarea> <span class="char-count" id="synopsis-full-count" data-astro-cid-mubuge4t>0/1000</span> </div> </fieldset> <div class="form-actions" data-astro-cid-mubuge4t> <button type="submit" class="submit-btn" id="ficha-submit-btn" data-astro-cid-mubuge4t>Enviar ficha técnica</button> </div> <div class="form-message form-message--error" id="ficha-error" hidden data-astro-cid-mubuge4t></div> <div class="form-message form-message--success" id="ficha-success" hidden data-astro-cid-mubuge4t></div> </form> ` })}`} </main> ` }));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/ficha/[token].astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/ficha/[token].astro";
const $$url = "/ficha/[token]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$token,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
