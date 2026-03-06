/* empty css                                  */
import { f as createComponent, r as renderTemplate, k as renderComponent, m as maybeRenderHead } from '../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import { $ as $$BaseLayout } from '../chunks/BaseLayout_QHw3iGXw.mjs';
/* empty css                                  */
export { renderers } from '../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(raw || cooked.slice()) }));
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
        ? 'Runtime per episode <span class="req">*</span>'
        : 'Runtime in minutes <span class="req">*</span>';
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
      showError('Please accept both checkboxes under "Rights" before submitting.');
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
      showError('Please fill in all required fields.');
      return;
    }

    try {
      new URL(data.drive_link);
    } catch(_) {
      showError('Please enter a valid URL for the Google Drive link.');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting\u2026';

    try {
      var response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      var result = await response.json();

      if (response.ok && result.success) {
        formSuccess.innerHTML = '<span class="bullet">\u2726</span> Your submission has been received.<br>We\\'ll review your work and get back to you at <strong>' + escapeHtml(data.filmmaker_email) + '</strong> within 14 business days.';
        formSuccess.hidden = false;
        form.reset();
        synopsisCount.textContent = '0/500';
        bioCount.textContent = '0/300';
        if (episodesWrapper) episodesWrapper.hidden = true;
        formSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        showError(result.error || 'Something went wrong. Please try again.');
      }
    } catch(err) {
      showError('Network error. Please check your connection and try again.');
    }

    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit your work';
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
<\/script> `], ["", ` <script>
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
        ? 'Runtime per episode <span class="req">*</span>'
        : 'Runtime in minutes <span class="req">*</span>';
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
      showError('Please accept both checkboxes under "Rights" before submitting.');
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
      showError('Please fill in all required fields.');
      return;
    }

    try {
      new URL(data.drive_link);
    } catch(_) {
      showError('Please enter a valid URL for the Google Drive link.');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting\u2026';

    try {
      var response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      var result = await response.json();

      if (response.ok && result.success) {
        formSuccess.innerHTML = '<span class="bullet">\u2726</span> Your submission has been received.<br>We\\\\'ll review your work and get back to you at <strong>' + escapeHtml(data.filmmaker_email) + '</strong> within 14 business days.';
        formSuccess.hidden = false;
        form.reset();
        synopsisCount.textContent = '0/500';
        bioCount.textContent = '0/300';
        if (episodesWrapper) episodesWrapper.hidden = true;
        formSuccess.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        showError(result.error || 'Something went wrong. Please try again.');
      }
    } catch(err) {
      showError('Network error. Please check your connection and try again.');
    }

    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit your work';
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
<\/script> `])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Submit your work \u2014 PRISMA", "description": "Submit your independent film, short, music video or series to PRISMA's curated catalog.", "data-astro-cid-cfftgubm": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<main class="submit-page" data-astro-cid-cfftgubm> <!-- Value proposition --> <header class="submit-header" data-astro-cid-cfftgubm> <h1 data-astro-cid-cfftgubm>Submit your work to PRISMA</h1> <p class="submit-intro" data-astro-cid-cfftgubm>
PRISMA is a curated platform for independent cinema. We accept short films,
        feature films, music videos, and series from independent filmmakers worldwide.
</p> <div class="submit-benefits" data-astro-cid-cfftgubm> <h2 data-astro-cid-cfftgubm>What you get</h2> <ul data-astro-cid-cfftgubm> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Your work analyzed through PRISMA's color identity system — the same framework applied to Tarkovsky, Bergman, and <em data-astro-cid-cfftgubm>Parasite</em></li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> A permanent page on prisma.film with structured data, Google-indexed</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> Real streaming stats — plays, minutes watched, geographic reach (via Bunny Stream)</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> AES-128 encryption + signed URLs + domain lock — your work is protected</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> No download button. Watermark with your name during encoding</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> If you already have works in our catalog, your submission links to your existing author profile</li> <li data-astro-cid-cfftgubm><span class="bullet" data-astro-cid-cfftgubm>✦</span> A URL you can put on your CV: <code data-astro-cid-cfftgubm>prisma.film/films/your-title</code></li> </ul> </div> <p class="submit-terms" data-astro-cid-cfftgubm>
We review every submission personally. Response within 14 business days.<br data-astro-cid-cfftgubm>
No fees. You keep 100% of your rights.
</p> </header> <!-- Form --> <form class="submit-form" id="submit-form" novalidate data-astro-cid-cfftgubm> <!-- Your work --> <fieldset class="form-section" data-astro-cid-cfftgubm> <legend data-astro-cid-cfftgubm>Your work</legend> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-type" data-astro-cid-cfftgubm>Content type</label> <select id="f-type" name="type" required data-astro-cid-cfftgubm> <option value="" data-astro-cid-cfftgubm>Select…</option> <option value="short" data-astro-cid-cfftgubm>Short film</option> <option value="feature" data-astro-cid-cfftgubm>Feature film</option> <option value="music_video" data-astro-cid-cfftgubm>Music video</option> <option value="series" data-astro-cid-cfftgubm>Series</option> </select> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-title" data-astro-cid-cfftgubm>Title <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="text" id="f-title" name="title" required maxlength="200" data-astro-cid-cfftgubm> </div> <div class="form-field form-row" data-astro-cid-cfftgubm> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-year" data-astro-cid-cfftgubm>Year <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="number" id="f-year" name="year" required min="1900" max="2030" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-runtime" id="f-runtime-label" data-astro-cid-cfftgubm>Runtime in minutes <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="number" id="f-runtime" name="runtime_min" required min="1" max="600" data-astro-cid-cfftgubm> </div> </div> <div class="form-field" id="f-episodes-wrapper" hidden data-astro-cid-cfftgubm> <label for="f-episodes" data-astro-cid-cfftgubm>Episode count</label> <input type="number" id="f-episodes" name="episode_count" min="1" max="100" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-synopsis" data-astro-cid-cfftgubm>Synopsis <span class="req" data-astro-cid-cfftgubm>*</span></label> <textarea id="f-synopsis" name="synopsis" required maxlength="500" rows="4" placeholder="Brief synopsis of your work…" data-astro-cid-cfftgubm></textarea> <span class="char-count" id="f-synopsis-count" data-astro-cid-cfftgubm>0/500</span> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-drive" data-astro-cid-cfftgubm>Google Drive link <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="url" id="f-drive" name="drive_link" required placeholder="https://drive.google.com/…" data-astro-cid-cfftgubm> <span class="form-helper" data-astro-cid-cfftgubm>Make sure the link is accessible to anyone with the link</span> </div> </fieldset> <!-- About you --> <fieldset class="form-section" data-astro-cid-cfftgubm> <legend data-astro-cid-cfftgubm>About you</legend> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-name" data-astro-cid-cfftgubm>Your name <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="text" id="f-name" name="filmmaker_name" required maxlength="120" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-email" data-astro-cid-cfftgubm>Email <span class="req" data-astro-cid-cfftgubm>*</span></label> <input type="email" id="f-email" name="filmmaker_email" required maxlength="200" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-bio" data-astro-cid-cfftgubm>Short bio <span class="form-optional" data-astro-cid-cfftgubm>optional</span></label> <textarea id="f-bio" name="filmmaker_bio" maxlength="300" rows="3" placeholder="A few words about yourself…" data-astro-cid-cfftgubm></textarea> <span class="char-count" id="f-bio-count" data-astro-cid-cfftgubm>0/300</span> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-website" data-astro-cid-cfftgubm>Website <span class="form-optional" data-astro-cid-cfftgubm>optional</span></label> <input type="url" id="f-website" name="filmmaker_website" placeholder="https://…" data-astro-cid-cfftgubm> </div> <div class="form-field" data-astro-cid-cfftgubm> <label for="f-social" data-astro-cid-cfftgubm>Instagram or social link <span class="form-optional" data-astro-cid-cfftgubm>optional</span></label> <input type="url" id="f-social" name="filmmaker_social" placeholder="https://instagram.com/…" data-astro-cid-cfftgubm> </div> </fieldset> <!-- Rights --> <fieldset class="form-section" data-astro-cid-cfftgubm> <legend data-astro-cid-cfftgubm>Rights</legend> <div class="form-check" data-astro-cid-cfftgubm> <input type="checkbox" id="f-rights" name="rights_confirmed" required data-astro-cid-cfftgubm> <label for="f-rights" data-astro-cid-cfftgubm>I own all rights to this work and have the authority to grant PRISMA a non-exclusive streaming license</label> </div> <div class="form-check" data-astro-cid-cfftgubm> <input type="checkbox" id="f-rejection" name="rejection_understood" required data-astro-cid-cfftgubm> <label for="f-rejection" data-astro-cid-cfftgubm>I understand PRISMA may reject my submission without obligation to provide detailed feedback</label> </div> </fieldset> <div class="form-actions" data-astro-cid-cfftgubm> <button type="submit" class="submit-btn" id="submit-btn" data-astro-cid-cfftgubm>Submit your work</button> </div> <!-- Messages --> <div class="form-message form-message--error" id="form-error" hidden data-astro-cid-cfftgubm></div> <div class="form-message form-message--success" id="form-success" hidden data-astro-cid-cfftgubm></div> </form> </main> ` }));
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
