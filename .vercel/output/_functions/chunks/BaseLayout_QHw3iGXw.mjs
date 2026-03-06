import { f as createComponent, r as renderTemplate, m as maybeRenderHead, e as createAstro, al as renderSlot, k as renderComponent, h as addAttribute, p as renderHead, u as unescapeHTML } from './astro/server_DZETslqp.mjs';
import 'piccolore';
/* empty css                          */
import 'clsx';

var __freeze$1 = Object.freeze;
var __defProp$1 = Object.defineProperty;
var __template$1 = (cooked, raw) => __freeze$1(__defProp$1(cooked, "raw", { value: __freeze$1(raw || cooked.slice()) }));
var _a$1;
const $$AuthModal = createComponent(async ($$result, $$props, $$slots) => {
  return renderTemplate(_a$1 || (_a$1 = __template$1(["", `<div id="auth-modal" class="auth-modal" hidden aria-modal="true" role="dialog" aria-labelledby="auth-modal-heading" data-astro-cid-crprt5hz> <div class="auth-modal__overlay" data-astro-cid-crprt5hz></div> <div class="auth-modal__card" data-astro-cid-crprt5hz> <button class="auth-modal__close" aria-label="Close" id="auth-modal-close" data-astro-cid-crprt5hz>\u2715</button> <div class="auth-modal__logo" aria-hidden="true" data-astro-cid-crprt5hz>PRISMA</div> <h2 class="auth-modal__heading" id="auth-modal-heading" data-astro-cid-crprt5hz>Join PRISMA</h2> <p class="auth-modal__sub" data-astro-cid-crprt5hz>Track films, rate, and discover your cinematic identity.</p> <div class="auth-modal__actions" data-astro-cid-crprt5hz> <!-- Google OAuth --> <button class="auth-btn auth-btn--google" id="btn-google-signin" type="button" data-astro-cid-crprt5hz> <svg class="auth-btn__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" data-astro-cid-crprt5hz> <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" data-astro-cid-crprt5hz></path> <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" data-astro-cid-crprt5hz></path> <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" data-astro-cid-crprt5hz></path> <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" data-astro-cid-crprt5hz></path> </svg>
Continue with Google
</button> <div class="auth-modal__separator" data-astro-cid-crprt5hz> <span data-astro-cid-crprt5hz>or</span> </div> <!-- Magic link / email --> <div class="auth-email-form" id="auth-email-form" hidden data-astro-cid-crprt5hz> <input type="email" id="auth-email-input" class="auth-email-input" placeholder="your@email.com" autocomplete="email" data-astro-cid-crprt5hz> <button class="auth-btn auth-btn--email-submit" id="btn-email-submit" type="button" data-astro-cid-crprt5hz>
Send magic link
</button> <p class="auth-email-hint" id="auth-email-hint" hidden data-astro-cid-crprt5hz></p> </div> <button class="auth-btn auth-btn--email" id="btn-email-toggle" type="button" data-astro-cid-crprt5hz>
Continue with email
</button> </div> <p class="auth-modal__terms" data-astro-cid-crprt5hz>
By joining you agree to our <a href="/terms" data-astro-cid-crprt5hz>terms</a> and <a href="/privacy" data-astro-cid-crprt5hz>privacy policy</a>.
</p> </div> </div> <script>
  console.log('[AuthModal] Script loaded');

  const modal    = document.getElementById('auth-modal')
  const overlay  = modal.querySelector('.auth-modal__overlay')
  const closeBtn = document.getElementById('auth-modal-close')

  // \u2500\u2500 Show / hide \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  function showModal() { 
    console.log('[AuthModal] Showing modal');
    modal.removeAttribute('hidden') 
  }
  function hideModal() { 
    console.log('[AuthModal] Hiding modal');
    modal.setAttribute('hidden', '') 
  }

  // Expose globally so any page/component can call window.showAuthModal()
  window.showAuthModal = showModal
  window.hideAuthModal = hideModal
  
  console.log('[AuthModal] Global functions registered:', { 
    showAuthModal: typeof window.showAuthModal,
    hideAuthModal: typeof window.hideAuthModal
  });

  overlay.addEventListener('click', hideModal)
  closeBtn.addEventListener('click', hideModal)

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hasAttribute('hidden')) hideModal()
  })

  // \u2500\u2500 Google OAuth \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  // Simple server-side redirect - no client-side Supabase SDK needed
  const googleBtn = document.getElementById('btn-google-signin')
  if (googleBtn) {
    googleBtn.addEventListener('click', function() {
      console.log('[AuthModal] Redirecting to server-side OAuth handler');
      window.location.href = '/auth/signin'
    })
  }

  // \u2500\u2500 Email (magic link) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  const emailToggle = document.getElementById('btn-email-toggle')
  const emailForm   = document.getElementById('auth-email-form')
  const emailInput  = document.getElementById('auth-email-input')
  const emailSubmit = document.getElementById('btn-email-submit')
  const emailHint   = document.getElementById('auth-email-hint')

  emailToggle.addEventListener('click', () => {
    emailForm.removeAttribute('hidden')
    emailToggle.setAttribute('hidden', '')
    emailInput.focus()
  })

  emailSubmit.addEventListener('click', async () => {
    try {
      const email = emailInput.value.trim()
      if (!email) return

      emailSubmit.textContent = 'Sending\u2026'
      emailSubmit.setAttribute('disabled', '')

      // Dynamically load Supabase client
      const { createBrowserClient } = await import('https://esm.sh/@supabase/ssr@0.5.1')
      const supabaseUrl = 'https://porqyokkphflvqfclvkj.supabase.co'
      const supabaseAnonKey = document.querySelector('meta[name="supabase-anon-key"]')?.getAttribute('content') || ''
      
      const client = createBrowserClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          flowType: 'pkce',
          detectSessionInUrl: true,
          persistSession: true,
        }
      })

      const { error } = await client.auth.signInWithOtp({
        email,
        options: { emailRedirectTo: \`\${window.location.origin}/auth/callback\` },
      })

      emailHint.removeAttribute('hidden')
      if (error) {
        emailHint.textContent = error.message
        emailHint.classList.add('auth-email-hint--error')
      } else {
        emailHint.textContent = 'Check your inbox \u2014 magic link sent!'
        emailHint.classList.remove('auth-email-hint--error')
      }

      emailSubmit.removeAttribute('disabled')
      emailSubmit.textContent = 'Send magic link'
    } catch(e) {
      console.error('[AuthModal] Email sign in error:', e)
      emailHint.removeAttribute('hidden')
      emailHint.textContent = 'An error occurred. Please try again.'
      emailHint.classList.add('auth-email-hint--error')
      emailSubmit.removeAttribute('disabled')
      emailSubmit.textContent = 'Send magic link'
    }
  })
<\/script>  `], ["", `<div id="auth-modal" class="auth-modal" hidden aria-modal="true" role="dialog" aria-labelledby="auth-modal-heading" data-astro-cid-crprt5hz> <div class="auth-modal__overlay" data-astro-cid-crprt5hz></div> <div class="auth-modal__card" data-astro-cid-crprt5hz> <button class="auth-modal__close" aria-label="Close" id="auth-modal-close" data-astro-cid-crprt5hz>\u2715</button> <div class="auth-modal__logo" aria-hidden="true" data-astro-cid-crprt5hz>PRISMA</div> <h2 class="auth-modal__heading" id="auth-modal-heading" data-astro-cid-crprt5hz>Join PRISMA</h2> <p class="auth-modal__sub" data-astro-cid-crprt5hz>Track films, rate, and discover your cinematic identity.</p> <div class="auth-modal__actions" data-astro-cid-crprt5hz> <!-- Google OAuth --> <button class="auth-btn auth-btn--google" id="btn-google-signin" type="button" data-astro-cid-crprt5hz> <svg class="auth-btn__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" data-astro-cid-crprt5hz> <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" data-astro-cid-crprt5hz></path> <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" data-astro-cid-crprt5hz></path> <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" data-astro-cid-crprt5hz></path> <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" data-astro-cid-crprt5hz></path> </svg>
Continue with Google
</button> <div class="auth-modal__separator" data-astro-cid-crprt5hz> <span data-astro-cid-crprt5hz>or</span> </div> <!-- Magic link / email --> <div class="auth-email-form" id="auth-email-form" hidden data-astro-cid-crprt5hz> <input type="email" id="auth-email-input" class="auth-email-input" placeholder="your@email.com" autocomplete="email" data-astro-cid-crprt5hz> <button class="auth-btn auth-btn--email-submit" id="btn-email-submit" type="button" data-astro-cid-crprt5hz>
Send magic link
</button> <p class="auth-email-hint" id="auth-email-hint" hidden data-astro-cid-crprt5hz></p> </div> <button class="auth-btn auth-btn--email" id="btn-email-toggle" type="button" data-astro-cid-crprt5hz>
Continue with email
</button> </div> <p class="auth-modal__terms" data-astro-cid-crprt5hz>
By joining you agree to our <a href="/terms" data-astro-cid-crprt5hz>terms</a> and <a href="/privacy" data-astro-cid-crprt5hz>privacy policy</a>.
</p> </div> </div> <script>
  console.log('[AuthModal] Script loaded');

  const modal    = document.getElementById('auth-modal')
  const overlay  = modal.querySelector('.auth-modal__overlay')
  const closeBtn = document.getElementById('auth-modal-close')

  // \u2500\u2500 Show / hide \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  function showModal() { 
    console.log('[AuthModal] Showing modal');
    modal.removeAttribute('hidden') 
  }
  function hideModal() { 
    console.log('[AuthModal] Hiding modal');
    modal.setAttribute('hidden', '') 
  }

  // Expose globally so any page/component can call window.showAuthModal()
  window.showAuthModal = showModal
  window.hideAuthModal = hideModal
  
  console.log('[AuthModal] Global functions registered:', { 
    showAuthModal: typeof window.showAuthModal,
    hideAuthModal: typeof window.hideAuthModal
  });

  overlay.addEventListener('click', hideModal)
  closeBtn.addEventListener('click', hideModal)

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hasAttribute('hidden')) hideModal()
  })

  // \u2500\u2500 Google OAuth \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  // Simple server-side redirect - no client-side Supabase SDK needed
  const googleBtn = document.getElementById('btn-google-signin')
  if (googleBtn) {
    googleBtn.addEventListener('click', function() {
      console.log('[AuthModal] Redirecting to server-side OAuth handler');
      window.location.href = '/auth/signin'
    })
  }

  // \u2500\u2500 Email (magic link) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
  const emailToggle = document.getElementById('btn-email-toggle')
  const emailForm   = document.getElementById('auth-email-form')
  const emailInput  = document.getElementById('auth-email-input')
  const emailSubmit = document.getElementById('btn-email-submit')
  const emailHint   = document.getElementById('auth-email-hint')

  emailToggle.addEventListener('click', () => {
    emailForm.removeAttribute('hidden')
    emailToggle.setAttribute('hidden', '')
    emailInput.focus()
  })

  emailSubmit.addEventListener('click', async () => {
    try {
      const email = emailInput.value.trim()
      if (!email) return

      emailSubmit.textContent = 'Sending\u2026'
      emailSubmit.setAttribute('disabled', '')

      // Dynamically load Supabase client
      const { createBrowserClient } = await import('https://esm.sh/@supabase/ssr@0.5.1')
      const supabaseUrl = 'https://porqyokkphflvqfclvkj.supabase.co'
      const supabaseAnonKey = document.querySelector('meta[name="supabase-anon-key"]')?.getAttribute('content') || ''
      
      const client = createBrowserClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          flowType: 'pkce',
          detectSessionInUrl: true,
          persistSession: true,
        }
      })

      const { error } = await client.auth.signInWithOtp({
        email,
        options: { emailRedirectTo: \\\`\\\${window.location.origin}/auth/callback\\\` },
      })

      emailHint.removeAttribute('hidden')
      if (error) {
        emailHint.textContent = error.message
        emailHint.classList.add('auth-email-hint--error')
      } else {
        emailHint.textContent = 'Check your inbox \u2014 magic link sent!'
        emailHint.classList.remove('auth-email-hint--error')
      }

      emailSubmit.removeAttribute('disabled')
      emailSubmit.textContent = 'Send magic link'
    } catch(e) {
      console.error('[AuthModal] Email sign in error:', e)
      emailHint.removeAttribute('hidden')
      emailHint.textContent = 'An error occurred. Please try again.'
      emailHint.classList.add('auth-email-hint--error')
      emailSubmit.removeAttribute('disabled')
      emailSubmit.textContent = 'Send magic link'
    }
  })
<\/script>  `])), maybeRenderHead());
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/components/auth/AuthModal.astro", void 0);

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a, _b;
const $$Astro = createAstro("https://prisma.film");
const $$BaseLayout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$BaseLayout;
  const {
    title,
    description = "PRISMA — Cinematic visual identity. Every film has a color.",
    ogImage,
    canonicalUrl,
    bodyClass = "",
    jsonLd
  } = Astro2.props;
  const siteUrl = "https://prisma.film";
  const resolvedCanonical = canonicalUrl ?? `${siteUrl}${Astro2.url.pathname}`;
  const resolvedOgImage = ogImage ?? `${siteUrl}/og-default.jpg`;
  const user = Astro2.locals.user;
  return renderTemplate(_b || (_b = __template(['<html lang="en" class="dark" data-astro-cid-37fxchfa> <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="generator"', '><!-- Supabase config for client-side auth --><meta name="supabase-anon-key"', "><title>", '</title><meta name="description"', '><link rel="canonical"', '><!-- Open Graph --><meta property="og:type" content="website"><meta property="og:title"', '><meta property="og:description"', '><meta property="og:image"', '><meta property="og:url"', '><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title"', '><meta name="twitter:description"', '><meta name="twitter:image"', "><!-- Structured data -->", '<!-- Favicon --><link rel="icon" type="image/svg+xml" href="/favicon.svg"><!-- Fonts: DM Serif Display + Inter --><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">', "</head> <body", ' data-astro-cid-37fxchfa> <!-- Site navigation --> <nav class="site-nav" data-astro-cid-37fxchfa> <a href="/" class="site-nav-logo" data-astro-cid-37fxchfa>P<span data-astro-cid-37fxchfa>R</span>ISMA</a> <ul class="site-nav-links" data-astro-cid-37fxchfa> <li data-astro-cid-37fxchfa><a href="/rankings/films" data-astro-cid-37fxchfa>Rankings</a></li> <li data-astro-cid-37fxchfa><a href="/colors" data-astro-cid-37fxchfa>Colors</a></li> <li class="site-nav-dropdown" data-astro-cid-37fxchfa> <span class="site-nav-trigger" data-astro-cid-37fxchfa>Explorar</span> <div class="site-nav-dropdown-menu" data-astro-cid-37fxchfa> <div class="site-nav-dropdown-group" data-astro-cid-37fxchfa> <p class="site-nav-dropdown-label" data-astro-cid-37fxchfa>Ritmo Visual</p> <a href="/ritmo/dinamico-frenetico" data-astro-cid-37fxchfa>Frenético</a> <a href="/ritmo/dinamico-energico" data-astro-cid-37fxchfa>Energético</a> <a href="/ritmo/moderado-balanceado" data-astro-cid-37fxchfa>Balanceado</a> <a href="/ritmo/lento-contemplativo" data-astro-cid-37fxchfa>Contemplativo</a> <a href="/ritmo/estatico-ritualistico" data-astro-cid-37fxchfa>Ritualístico</a> </div> <div class="site-nav-dropdown-group" data-astro-cid-37fxchfa> <p class="site-nav-dropdown-label" data-astro-cid-37fxchfa>Temperatura</p> <a href="/temperatura/calido-apasionado" data-astro-cid-37fxchfa>Apasionado</a> <a href="/temperatura/calido-nostalgico" data-astro-cid-37fxchfa>Nostálgico</a> <a href="/temperatura/neutral-contemplativo" data-astro-cid-37fxchfa>Contemplativo</a> <a href="/temperatura/frio-melancolico" data-astro-cid-37fxchfa>Melancólico</a> <a href="/temperatura/frio-perturbador" data-astro-cid-37fxchfa>Perturbador</a> </div> <div class="site-nav-dropdown-group" data-astro-cid-37fxchfa> <p class="site-nav-dropdown-label" data-astro-cid-37fxchfa>Abstracción</p> <a href="/abstraccion/extremadamente-realista" data-astro-cid-37fxchfa>Realista</a> <a href="/abstraccion/realista-con-estilizacion" data-astro-cid-37fxchfa>Estilizado</a> <a href="/abstraccion/estilizado" data-astro-cid-37fxchfa>Expresivo</a> <a href="/abstraccion/muy-estilizado" data-astro-cid-37fxchfa>Muy Estilizado</a> <a href="/abstraccion/extremadamente-abstracto" data-astro-cid-37fxchfa>Abstracto</a> </div> </div> </li> <li data-astro-cid-37fxchfa><a href="/countries" data-astro-cid-37fxchfa>Countries</a></li> <li data-astro-cid-37fxchfa><a href="/festivals" data-astro-cid-37fxchfa>Festivals</a></li> <li data-astro-cid-37fxchfa><a href="/people" data-astro-cid-37fxchfa>People</a></li> <li data-astro-cid-37fxchfa><a href="/submit" class="nav-submit" data-astro-cid-37fxchfa>Submit</a></li> </ul> <!-- Auth --> <div class="site-nav-auth" data-astro-cid-37fxchfa> ', " </div> </nav> <!-- Auth modal — rendered once globally; shown via window.showAuthModal() --> ", " <!-- Page content --> ", ` <!-- Client-side handlers --> <script>
      console.log('[BaseLayout] Client script loaded');
      
      // Handle sign out form submission
      const signOutForm = document.querySelector('form[action="/auth/signout"]');
      if (signOutForm) {
        console.log('[BaseLayout] Sign out form found, attaching handler');
        signOutForm.addEventListener('submit', function(e) {
          console.log('[BaseLayout] Sign out form submitted');
          // Let the form submit naturally, but force a page reload after
          setTimeout(function() {
            window.location.href = '/';
          }, 100);
        });
      }
    </script> </body> </html> `])), addAttribute(Astro2.generator, "content"), addAttribute("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvcnF5b2trcGhmbHZxZmNsdmtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNDE2MzEsImV4cCI6MjA4NzYxNzYzMX0.q_fDlajLrMQ1Cbg7o_gwDGPhX8Mt7BwhgXapMkY9jN4", "content"), title, addAttribute(description, "content"), addAttribute(resolvedCanonical, "href"), addAttribute(title, "content"), addAttribute(description, "content"), addAttribute(resolvedOgImage, "content"), addAttribute(resolvedCanonical, "content"), addAttribute(title, "content"), addAttribute(description, "content"), addAttribute(resolvedOgImage, "content"), jsonLd && renderTemplate(_a || (_a = __template(['<script type="application/ld+json">', "</script>"])), unescapeHTML(jsonLd)), renderHead(), addAttribute(bodyClass, "class"), user ? renderTemplate`<div class="nav-user" data-astro-cid-37fxchfa> ${user.user_metadata?.avatar_url ? renderTemplate`<a${addAttribute(`/u/${user.id}`, "href")} class="nav-avatar-link" title="My profile" data-astro-cid-37fxchfa> <img${addAttribute(user.user_metadata.avatar_url, "src")}${addAttribute(user.user_metadata?.full_name ?? "Profile", "alt")} class="nav-avatar" referrerpolicy="no-referrer" data-astro-cid-37fxchfa> </a>` : renderTemplate`<a${addAttribute(`/u/${user.id}`, "href")} class="nav-avatar-link nav-avatar--initials" title="My profile" data-astro-cid-37fxchfa> ${(user.user_metadata?.full_name ?? user.email ?? "?")[0].toUpperCase()} </a>`} <form action="/auth/signout" method="POST" style="display:inline" data-astro-cid-37fxchfa> <button type="submit" class="nav-signout" data-astro-cid-37fxchfa>Sign out</button> </form> </div>` : renderTemplate`<button class="nav-signin" onclick="window.showAuthModal?.()" data-astro-cid-37fxchfa>Sign in</button>`, !user && renderTemplate`${renderComponent($$result, "AuthModal", $$AuthModal, { "data-astro-cid-37fxchfa": true })}`, renderSlot($$result, $$slots["default"]));
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/layouts/BaseLayout.astro", void 0);

export { $$BaseLayout as $ };
