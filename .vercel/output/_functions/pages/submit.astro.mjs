/* empty css                                  */
import { f as createComponent, r as renderTemplate, k as renderComponent, m as maybeRenderHead } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_CKaj1kxH.mjs';
/* empty css                                  */
export { renderers } from '../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const prerender = false;
const $$Submit = createComponent(async ($$result, $$props, $$slots) => {
  return renderTemplate(_a || (_a = __template(["", ` <script>
(function() {
  var form = document.getElementById('submit-form');
  var typeSelect = document.getElementById('f-type');
  var runtimeLabel = document.getElementById('f-runtime-label');
  var episodesWrapper = document.getElementById('f-episodes-wrapper');
  var synopsisField = document.getElementById('f-synopsis');
  var synopsisCount = document.getElementById('f-synopsis-count');
  var bioField = document.getElementById('f-bio');
  var bioCount = document.getElementById('f-bio-count');
  var submitBtn = document.getElementById('submit-btn');
  var formError = document.getElementById('form-error');
  var formSuccess = document.getElementById('form-success');

  if (!form || !typeSelect) return;

  // Dynamic fields based on content type
  typeSelect.addEventListener('change', function() {
    var isSeries = typeSelect.value === 'series';
    if (runtimeLabel) {
      runtimeLabel.innerHTML = isSeries
        ? 'Duraci\xF3n por episodio <span class="req">*</span>'
        : 'Duraci\xF3n en minutos <span class="req">*</span>';
    }
    if (episodesWrapper) {
      episodesWrapper.hidden = !isSeries;
    }
  });

  // Character counters
  if (synopsisField && synopsisCount) {
    synopsisField.addEventListener('input', function() {
      synopsisCount.textContent = synopsisField.value.length + '/500';
    });
  }
  if (bioField && bioCount) {
    bioField.addEventListener('input', function() {
      bioCount.textContent = bioField.value.length + '/300';
    });
  }

  // Submit
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    formError.hidden = true;
    formSuccess.hidden = true;

    var rights = document.getElementById('f-rights');
    var rejection = document.getElementById('f-rejection');

    if (!rights.checked || !rejection.checked) {
      showError('Por favor acepta ambas casillas en "Derechos" antes de enviar.');
      return;
    }

    var data = {
      type: typeSelect.value,
      title: document.getElementById('f-title').value.trim(),
      year: Number(document.getElementById('f-year').value),
      runtime_min: Number(document.getElementById('f-runtime').value),
      synopsis: synopsisField.value.trim(),
      drive_link: document.getElementById('f-drive').value.trim(),
      filmmaker_name: document.getElementById('f-name').value.trim(),
      filmmaker_email: document.getElementById('f-email').value.trim(),
      filmmaker_bio: (bioField ? bioField.value.trim() : '') || null,
      filmmaker_website: document.getElementById('f-website').value.trim() || null,
      filmmaker_social: document.getElementById('f-social').value.trim() || null,
      episode_count: document.getElementById('f-episodes').value ? Number(document.getElementById('f-episodes').value) : null,
      rights_confirmed: rights.checked,
      rejection_understood: rejection.checked,
    };

    if (!data.title || !data.year || !data.runtime_min || !data.synopsis || !data.drive_link || !data.filmmaker_name || !data.filmmaker_email) {
      showError('Por favor completa todos los campos obligatorios.');
      return;
    }

    try {
      new URL(data.drive_link);
    } catch(_) {
      showError('Por favor ingresa una URL v\xE1lida para el enlace de Google Drive.');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando\u2026';

    try {
      var response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      var result = await response.json();

      if (response.ok && result.success) {
        formSuccess.innerHTML = '<span class="bullet">\u2726</span> Tu env\xEDo ha sido recibido.<br>Revisaremos tu obra y te responderemos a <strong>' + escapeHtml(data.filmmaker_email) + '</strong> en un plazo de 14 d\xEDas h\xE1biles.';
        formSuccess.hidden = false;
        form.reset();
        synopsisCount.textContent = '0/500';
        bioCount.textContent = '0/300';
        if (episodesWrapper) episodesWrapper.hidden = true;
        formSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        showError(result.error || 'Algo sali\xF3 mal. Por favor intenta de nuevo.');
      }
    } catch(err) {
      showError('Error de red. Por favor verifica tu conexi\xF3n e intenta de nuevo.');
    }

    submitBtn.disabled = false;
    submitBtn.textContent = 'Enviar tu obra';
  });

  function showError(msg) {
    formError.textContent = msg;
    formError.hidden = false;
    formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
})();
<\/script> `])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Env\xEDa tu obra \u2014 PRISMA", "description": "Env\xEDa tu pel\xEDcula independiente, corto, video musical o serie al cat\xE1logo curado de PRISMA.", "data-astro-cid-cfftgubm": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="submit-page" data-astro-cid-cfftgubm> <!-- Value proposition --> <header class="submit-header" data-astro-cid-cfftgubm> <h1 data-astro-cid-cfftgubm>Envía tu obra a PRISMA</h1> <p class="submit-intro" data-astro-cid-cfftgubm>
PRISMA es una plataforma curada de cine independiente. Aceptamos cortometrajes,
        largometrajes, videos musicales y series de cineastas independientes de todo el mundo.
</p> <div class="submit-benefits" data-astro-cid-cfftgubm> <h2 data-astro-cid-cfftgubm>Qué obtienes</h2> <ul data-astro-cid-cfftgubm> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Tu obra analizada con el sistema de identidad cromática de PRISMA — el mismo que se aplica a Tarkovsky, Bergman y <em data-astro-cid-cfftgubm>Parasite</em></li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Una página permanente en prisma.film con datos estructurados, indexada en Google</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Estadísticas reales de streaming — reproducciones, minutos vistos, alcance geográfico (vía Bunny Stream)</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Encriptación AES-128 + URLs firmadas + bloqueo de dominio — tu obra está protegida</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Sin botón de descarga. Marca de agua con tu nombre durante la codificación</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Si ya tienes obras en nuestro catálogo, tu envío se vincula a tu perfil de autor existente</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Una URL para poner en tu CV: <code data-astro-cid-cfftgubm>prisma.film/films/tu-titulo</code></li> </ul> </div> <p class="submit-terms" data-astro-cid-cfftgubm>
Revisamos cada envío personalmente. Respuesta en 14 días hábiles.<br data-astro-cid-cfftgubm>
Sin costo. Conservas el 100% de tus derechos.
</p> </header> <!-- Form --> <form class="submit-form" id="submit-form" novalidate data-astro-cid-cfftgubm> <!-- Your work --> <fieldset class="form-section" data-astro-cid-cfftgubm> <legend data-astro-cid-cfftgubm>Tu obra</legend> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-type" data-astro-cid-cfftgubm>Tipo de contenido</label> <select id="f-type" name="type" required data-astro-cid-cfftgubm> <option value="" data-astro-cid-cfftgubm>Seleccionar…</option> <option value="short" data-astro-cid-cfftgubm>Cortometraje</option> <option value="feature" data-astro-cid-cfftgubm>Largometraje</option> <option value="music_video" data-astro-cid-cfftgubm>Video musical</option> <option value="series" data-astro-cid-cfftgubm>Serie</option> </select> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-title" data-astro-cid-cfftgubm>Título <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="text" id="f-title" name="title" required maxlength="200" data-astro-cid-cfftgubm> </div> <div class="form-field form-row" data-astro-cid-cfftgubm> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-year" data-astro-cid-cfftgubm>Año <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="number" id="f-year" name="year" required min="1900" max="2030" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-runtime" id="f-runtime-label" data-astro-cid-cfftgubm>Duración en minutos <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="number" id="f-runtime" name="runtime_min" required min="1" max="600" data-astro-cid-cfftgubm> </div> </div> <div class="form-field" id="f-episodes-wrapper" hidden data-astro-cid-cfftgubm> <label for="f-episodes" data-astro-cid-cfftgubm>Número de episodios</label> <input type="number" id="f-episodes" name="episode_count" min="1" max="100" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-synopsis" data-astro-cid-cfftgubm>Sinopsis <span class="req" data-astro-cid-cfftgubm>*</span></label> <textarea id="f-synopsis" name="synopsis" required maxlength="500" rows="4" placeholder="Sinopsis breve de tu obra…" data-astro-cid-cfftgubm></textarea> <span class="char-count" id="f-synopsis-count" data-astro-cid-cfftgubm>0/500</span> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-drive" data-astro-cid-cfftgubm>Enlace de Google Drive <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="url" id="f-drive" name="drive_link" required placeholder="https://drive.google.com/…" data-astro-cid-cfftgubm> <span class="form-helper" data-astro-cid-cfftgubm>Asegúrate de que el enlace sea accesible para cualquier persona</span> </div> </fieldset> <!-- About you --> <fieldset class="form-section" data-astro-cid-cfftgubm> <legend data-astro-cid-cfftgubm>Sobre ti</legend> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-name" data-astro-cid-cfftgubm>Tu nombre <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="text" id="f-name" name="filmmaker_name" required maxlength="120" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-email" data-astro-cid-cfftgubm>Correo electrónico <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="email" id="f-email" name="filmmaker_email" required maxlength="200" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-bio" data-astro-cid-cfftgubm>Biografía breve <span class="form-optional" data-astro-cid-cfftgubm>opcional</span></label> <textarea id="f-bio" name="filmmaker_bio" maxlength="300" rows="3" placeholder="Unas palabras sobre ti…" data-astro-cid-cfftgubm></textarea> <span class="char-count" id="f-bio-count" data-astro-cid-cfftgubm>0/300</span> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-website" data-astro-cid-cfftgubm>Sitio web <span class="form-optional" data-astro-cid-cfftgubm>opcional</span></label> <input type="url" id="f-website" name="filmmaker_website" placeholder="https://…" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-social" data-astro-cid-cfftgubm>Instagram o enlace social <span class="form-optional" data-astro-cid-cfftgubm>opcional</span></label> <input type="url" id="f-social" name="filmmaker_social" placeholder="https://instagram.com/…" data-astro-cid-cfftgubm> </div> </fieldset> <!-- Rights --> <fieldset class="form-section" data-astro-cid-cfftgubm> <legend data-astro-cid-cfftgubm>Derechos</legend> <div class="form-check" data-astro-cid-cfftgubm> <input type="checkbox" id="f-rights" name="rights_confirmed" required data-astro-cid-cfftgubm> <label for="f-rights" data-astro-cid-cfftgubm>Poseo todos los derechos de esta obra y tengo la autoridad para otorgar a PRISMA una licencia de streaming no exclusiva</label> </div> <div class="form-check" data-astro-cid-cfftgubm> <input type="checkbox" id="f-rejection" name="rejection_understood" required data-astro-cid-cfftgubm> <label for="f-rejection" data-astro-cid-cfftgubm>Entiendo que PRISMA puede rechazar mi envío sin obligación de dar retroalimentación detallada</label> </div> </fieldset> <div class="form-actions" data-astro-cid-cfftgubm> <button type="submit" class="submit-btn" id="submit-btn" data-astro-cid-cfftgubm>Enviar tu obra</button> </div> <!-- Messages --> <div class="form-message form-message--error" id="form-error" hidden data-astro-cid-cfftgubm></div> <div class="form-message form-message--success" id="form-success" hidden data-astro-cid-cfftgubm></div> </form> </main> ` }));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/submit.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/submit.astro";
const $$url = "/submit";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Submit,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
