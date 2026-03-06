/* empty css                                     */
import { f as createComponent, r as renderTemplate, p as renderHead } from '../../chunks/astro/server_DZETslqp.mjs';
import 'piccolore';
import 'clsx';
export { renderers } from '../../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const prerender = false;
const $$Callback = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate(_a || (_a = __template(["<html> <head><title>Signing in...</title>", "</head> <body> <script>\n(function() {\n  var hash = window.location.hash.substring(1)\n  var params = {}\n  hash.split('&').forEach(function(part) {\n    var eq = part.indexOf('=')\n    if (eq > -1) {\n      params[decodeURIComponent(part.substring(0, eq))] = decodeURIComponent(part.substring(eq + 1))\n    }\n  })\n  \n  var accessToken = params['access_token']\n  var refreshToken = params['refresh_token'] || ''\n  var expiresIn = parseInt(params['expires_in'] || '3600')\n  \n  if (accessToken) {\n    var session = JSON.stringify({\n      access_token: accessToken,\n      refresh_token: refreshToken,\n      expires_in: expiresIn,\n      expires_at: Math.floor(Date.now() / 1000) + expiresIn,\n      token_type: 'bearer'\n    })\n    var expires = new Date(Date.now() + expiresIn * 1000).toUTCString()\n    var cookieName = 'sb-porqyokkphflvqfclvkj-auth-token'\n    document.cookie = cookieName + '=' + encodeURIComponent(session) + '; path=/; expires=' + expires + '; SameSite=Lax'\n    window.location.replace('/')\n  } else {\n    window.location.replace('/auth/error?message=No+token+received')\n  }\n})()\n<\/script> </body> </html>"])), renderHead());
}, "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/auth/callback.astro", void 0);

const $$file = "/Users/servinemilio/Documents/REPOS/prisma-site/src/pages/auth/callback.astro";
const $$url = "/auth/callback";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Callback,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
