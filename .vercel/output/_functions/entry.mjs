import { renderers } from './renderers.mjs';
import { c as createExports, s as serverEntrypointModule } from './chunks/_@astrojs-ssr-adapter_Di8k0pxs.mjs';
import { manifest } from './manifest_oQ1VnXST.mjs';

const serverIslandMap = new Map();;

const _page0 = () => import('./pages/_image.astro.mjs');
const _page1 = () => import('./pages/abstraccion/_slug_.astro.mjs');
const _page2 = () => import('./pages/admin/curator.astro.mjs');
const _page3 = () => import('./pages/admin/ficha/_id_.astro.mjs');
const _page4 = () => import('./pages/admin/review.astro.mjs');
const _page5 = () => import('./pages/admin/submissions.astro.mjs');
const _page6 = () => import('./pages/api/admin/approve-article.astro.mjs');
const _page7 = () => import('./pages/api/admin/bunny-upload.astro.mjs');
const _page8 = () => import('./pages/api/admin/override-color.astro.mjs');
const _page9 = () => import('./pages/api/admin/publish/_id_.astro.mjs');
const _page10 = () => import('./pages/api/admin/reject-article.astro.mjs');
const _page11 = () => import('./pages/api/admin/send-ficha.astro.mjs');
const _page12 = () => import('./pages/api/admin/submissions/_id_.astro.mjs');
const _page13 = () => import('./pages/api/ficha/_token_.astro.mjs');
const _page14 = () => import('./pages/api/share/film-card.astro.mjs');
const _page15 = () => import('./pages/api/stream-token/_work_id_.astro.mjs');
const _page16 = () => import('./pages/api/submit.astro.mjs');
const _page17 = () => import('./pages/api/user/follow.astro.mjs');
const _page18 = () => import('./pages/api/user/rate.astro.mjs');
const _page19 = () => import('./pages/api/user/review.astro.mjs');
const _page20 = () => import('./pages/api/user/seen.astro.mjs');
const _page21 = () => import('./pages/api/user/watchlist.astro.mjs');
const _page22 = () => import('./pages/auth/callback.astro.mjs');
const _page23 = () => import('./pages/auth/error.astro.mjs');
const _page24 = () => import('./pages/auth/signin.astro.mjs');
const _page25 = () => import('./pages/auth/signout.astro.mjs');
const _page26 = () => import('./pages/colors/_slug_.astro.mjs');
const _page27 = () => import('./pages/colors.astro.mjs');
const _page28 = () => import('./pages/countries/_slug_.astro.mjs');
const _page29 = () => import('./pages/countries.astro.mjs');
const _page30 = () => import('./pages/decades/_decade_.astro.mjs');
const _page31 = () => import('./pages/decades.astro.mjs');
const _page32 = () => import('./pages/explorar.astro.mjs');
const _page33 = () => import('./pages/festivals/_slug_.astro.mjs');
const _page34 = () => import('./pages/festivals.astro.mjs');
const _page35 = () => import('./pages/ficha/_token_.astro.mjs');
const _page36 = () => import('./pages/films/_slug_.astro.mjs');
const _page37 = () => import('./pages/people/_slug_.astro.mjs');
const _page38 = () => import('./pages/people.astro.mjs');
const _page39 = () => import('./pages/rankings/films.astro.mjs');
const _page40 = () => import('./pages/ritmo/_slug_.astro.mjs');
const _page41 = () => import('./pages/share/_work_id_.astro.mjs');
const _page42 = () => import('./pages/sitemap.xml.astro.mjs');
const _page43 = () => import('./pages/studios/_slug_.astro.mjs');
const _page44 = () => import('./pages/submit.astro.mjs');
const _page45 = () => import('./pages/temperatura/_slug_.astro.mjs');
const _page46 = () => import('./pages/u/_id_.astro.mjs');
const _page47 = () => import('./pages/index.astro.mjs');
const pageMap = new Map([
    ["node_modules/astro/dist/assets/endpoint/generic.js", _page0],
    ["src/pages/abstraccion/[slug].astro", _page1],
    ["src/pages/admin/curator.astro", _page2],
    ["src/pages/admin/ficha/[id].astro", _page3],
    ["src/pages/admin/review.astro", _page4],
    ["src/pages/admin/submissions.astro", _page5],
    ["src/pages/api/admin/approve-article.ts", _page6],
    ["src/pages/api/admin/bunny-upload.ts", _page7],
    ["src/pages/api/admin/override-color.ts", _page8],
    ["src/pages/api/admin/publish/[id].ts", _page9],
    ["src/pages/api/admin/reject-article.ts", _page10],
    ["src/pages/api/admin/send-ficha.ts", _page11],
    ["src/pages/api/admin/submissions/[id].ts", _page12],
    ["src/pages/api/ficha/[token].ts", _page13],
    ["src/pages/api/share/film-card.ts", _page14],
    ["src/pages/api/stream-token/[work_id].ts", _page15],
    ["src/pages/api/submit.ts", _page16],
    ["src/pages/api/user/follow.ts", _page17],
    ["src/pages/api/user/rate.ts", _page18],
    ["src/pages/api/user/review.ts", _page19],
    ["src/pages/api/user/seen.ts", _page20],
    ["src/pages/api/user/watchlist.ts", _page21],
    ["src/pages/auth/callback.astro", _page22],
    ["src/pages/auth/error.astro", _page23],
    ["src/pages/auth/signin.ts", _page24],
    ["src/pages/auth/signout.ts", _page25],
    ["src/pages/colors/[slug].astro", _page26],
    ["src/pages/colors/index.astro", _page27],
    ["src/pages/countries/[slug].astro", _page28],
    ["src/pages/countries/index.astro", _page29],
    ["src/pages/decades/[decade].astro", _page30],
    ["src/pages/decades/index.astro", _page31],
    ["src/pages/explorar/index.astro", _page32],
    ["src/pages/festivals/[slug].astro", _page33],
    ["src/pages/festivals/index.astro", _page34],
    ["src/pages/ficha/[token].astro", _page35],
    ["src/pages/films/[slug].astro", _page36],
    ["src/pages/people/[slug].astro", _page37],
    ["src/pages/people/index.astro", _page38],
    ["src/pages/rankings/films.astro", _page39],
    ["src/pages/ritmo/[slug].astro", _page40],
    ["src/pages/share/[work_id].astro", _page41],
    ["src/pages/sitemap.xml.ts", _page42],
    ["src/pages/studios/[slug].astro", _page43],
    ["src/pages/submit.astro", _page44],
    ["src/pages/temperatura/[slug].astro", _page45],
    ["src/pages/u/[id].astro", _page46],
    ["src/pages/index.astro", _page47]
]);

const _manifest = Object.assign(manifest, {
    pageMap,
    serverIslandMap,
    renderers,
    actions: () => import('./noop-entrypoint.mjs'),
    middleware: () => import('./_astro-internal_middleware.mjs')
});
const _args = {
    "middlewareSecret": "83756560-00e3-4d77-9d22-e16a1159d8f3",
    "skewProtection": false
};
const _exports = createExports(_manifest, _args);
const __astrojsSsrVirtualEntry = _exports.default;
const _start = 'start';
if (Object.prototype.hasOwnProperty.call(serverEntrypointModule, _start)) ;

export { __astrojsSsrVirtualEntry as default, pageMap };
