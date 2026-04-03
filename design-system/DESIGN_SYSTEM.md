# PRISMA Design System
## Editorial Rules & Visual Identity Document

*Synthesized from analysis of: A24, ColorsxStudios, Criterion, Le Cinéma Club, Little White Lies (lwlies.co), MUBI*

---

## 1. The Five Core Principles

### I. VOID AS GROUND
*(Source: a24films.com visual-density.json: density_score 20, whitespace_ratio 0.806 — the most extreme whitespace of all 6 references; ColorsxStudios: whitespace_ratio 0.848)*

PRISMA lives in darkness. The background is not grey, not charcoal — it is near-void (`#0A0A0F`). Whitespace is not empty space; it is a deliberate editorial choice that gives every element cinematic weight. When in doubt, remove. A page with 3 elements and breathing room outperforms a page with 10 elements in competition.

**Rule:** No surface should feel crowded. Average density target: ≤ 25/100 (matching A24 + ColorsxStudios).

---

### II. COLOR IS THE PROTAGONIST
*(Source: colorsxstudios.com premium-patterns: "gradient-design, clip-path-shapes, color injection"; all 6 refs: dark-theme)*

Each film has one PRISMA color. That color governs its entire page experience — hero gradient, glow, badge accents, hover states. The 18 iconic colors are not decorative; they are structural. They inject via `--prisma-color` and cascade through `color-mix()` derivatives. No film page should look identical to another.

**Rule:** Always set `activatePrismaColor(slug)` on film pages. Never hard-code a hex where `--prisma-color` is appropriate.

---

### III. TYPOGRAPHY BEFORE IMAGE
*(Source: lwlies.co "editorial-serif-headings, focus on readability"; lecinemaclub.com "magazine-like, distinct sections"; mubi.com "Swiss design influence, typography to convey message"; colorsxstudios.com "typography as primary design element")*

Serif for editorial weight (film titles, section headlines, rankings). Sans-serif for UI legibility (nav, labels, metadata). The serif is DM Serif Display — chosen for its ink-trap details visible at display sizes. The sans is Inter — neutral, legible, Swiss-influenced. Never use serif for body copy. Never use sans for display titles.

**Rule:** Serif = editorial authority. Sans = functional clarity. Mixing them creates hierarchy, not confusion.

---

### IV. MOTION IS CINEMATIC, NOT DECORATIVE
*(Source: a24films.com design-notes: "minimal and restrained approach, dramatic intensity"; lecinemaclub.com: "balanced transition, simultaneous timing, 7 delayed elements"; ColorsxStudios: "css-keyframe-animations, dramatic intensity")*

Animations have two modes: *entrance* (reveal on scroll) and *hover* (instant feedback). Entrances use the `--ease-out-expo` curve (`cubic-bezier(0.16, 1, 0.3, 1)`) for a dramatic deceleration. Hovers use `--ease-editorial` at `160ms` — fast enough to feel responsive, slow enough to feel considered. Nothing bounces. Nothing spins. Nothing loops.

**Rule:** Every animation serves legibility. If removing it doesn't degrade the experience, remove it.

---

### V. RESTRAINT IS THE PREMIUM SIGNAL
*(Source: A24 premium-score 66, ColorsxStudios 70 — both achieve "High Quality" through reduction, not addition; lwlies.co: "less can be more when aiming for high-end presence"; mubi.com: "commitment to restraint")*

A single element at full weight communicates more than five elements at half weight. PRISMA never uses gradients on text, never uses drop shadows on text, never uses more than 2 font families, never uses more than 3 colors per page outside of the 18-color system.

---

## 2. Typography Rules

| Context | Class | Family | When to Use |
|---|---|---|---|
| Film title, hero | `.type-display` | DM Serif Display | Only once per page, full visual weight |
| Page h1 | `.type-headline` | DM Serif Display | Section entry points |
| Card title | `.type-title` | DM Serif Display | Film cards, list items |
| Pull quote / sub | `.type-subtitle` | DM Serif Display italic | Supporting editorial text |
| Body / synopsis | `.type-body` | Inter | Long-form reading copy |
| Nav / labels | `.type-label` | Inter | ALL-CAPS + letter-spacing |
| Metadata | `.type-meta` | Inter | Year, director, runtime |
| Ranking number | `.type-rank` | DM Serif Display | Numbers as monumental anchors |
| Color identity | `.type-color-name` | Inter | Always ALL-CAPS, widest spacing |

**Never:**
- Use DM Serif Display below 18px
- Use Inter above 32px for display
- Mix letter-spacing with serif fonts
- Use `font-weight: 700+` on DM Serif Display (it has no bold — stays at 400)

---

## 3. Color Rules

### The 18 Iconic Colors
Each color maps to an emotional and cinematic register. They are assigned to films by editorial decision — not algorithmically. The color *is* the film's identity in the PRISMA system.

### Color Injection Pattern
```typescript
// On any page where a film's color governs the experience:
activatePrismaColor('ambar_desertico');
// All --prisma-color-* variables update automatically via color-mix()
```

### Text on Color Backgrounds
| Color | Light? | Text Color |
|---|---|---|
| `amarillo_ludico`, `verde_lima`, `blanco_polar`, `rosa_pastel` | Yes | `#0A0A0F` |
| All others | No | `#F0EEE8` |

### Color in the UI
- **Hero gradient**: `linear-gradient(155deg, --prisma-color 0%, --prisma-color-mid 42%, #0D0D0F 100%)`
- **Ambient glow**: `radial-gradient` using `--prisma-color-glow` — diffuse, never sharp
- **Borders**: `--prisma-color-border` — 30% opacity, subtle presence
- **Badge backgrounds**: `--prisma-color-ghost` — 10% opacity fill

### What Never Happens with Color
- No two prisma colors side-by-side on the same surface
- No color on text except `--text-accent` (warm parchment) for editorial highlights
- No color gradients in backgrounds outside of the hero/wash pattern

---

## 4. Animation Principles

### Timing Reference Table
*(Source: lecinemaclub.com, a24films.com motion data)*

| Duration | Variable | Use |
|---|---|---|
| 80ms | `--dur-instant` | Micro: button press feedback |
| 160ms | `--dur-fast` | Hover states: color, opacity changes |
| 280ms | `--dur-base` | Standard: border, shadow transitions |
| 480ms | `--dur-slow` | Page enters, panel reveals |
| 700ms | `--dur-crawl` | Cinematic: scroll reveals, hero content |

### Easing Reference
*(Source: lecinemaclub.com "balanced transition"; a24films.com "scroll-reveal")*

| Curve | Variable | Character |
|---|---|---|
| `cubic-bezier(0.25, 0.46, 0.45, 0.94)` | `--ease-editorial` | Smooth, balanced — standard |
| `cubic-bezier(0.16, 1, 0.3, 1)` | `--ease-out-expo` | Dramatic deceleration — reveals |
| `cubic-bezier(0.4, 0, 0.2, 1)` | `--ease-in-out` | Symmetric — toggles, switches |

### Scroll Reveal
- Use `.reveal` class + `initRevealAnimations()`
- Stagger sibling items with `staggerReveal(container, 80)` — 80ms matches A24's "simultaneous" feel
- Root margin: `0px 0px -60px 0px` — elements trigger slightly before entering the viewport

### What Never Animates
- Text color changes on hero (set once, no transition)
- Layout shifts (no width/height transitions)
- Anything on a page transition (navigation is instant)

---

## 5. Grid Rules

```
Max width:      1280px  (--grid-max)
Content width:   860px  (--grid-content)
Narrow width:    640px  (--grid-narrow)
Gutter:           2rem  (--grid-gutter)
```
*(Source: a24films.com visual-density.json: content_width_pct 61.9 of 1280px ≈ 793px — we use 860px for comfort)*

### Layout Patterns
1. **Full-bleed sections** — background extends edge to edge, content in `.site-container`
2. **Featured grid** — `.film-grid--featured` first item spans 2 cols × 2 rows
3. **Auto-fill grid** — `.film-grid` fills available space, min 200px per card
4. **Alternating rhythm** — even sections left-weighted, odd sections right-weighted

### Never
- Center-align body text
- Use more than 4 columns for film grids on desktop
- Nest containers (one `.site-container` per section)

---

## 6. What Is NEVER Done in PRISMA

| Rule | Reason |
|---|---|
| No white or light backgrounds | PRISMA is a dark editorial space — every reference confirms dark-theme |
| No filled primary buttons (solid background) | A24 "outlined-ghost" CTA is the pattern — outline only |
| No decorative stock imagery | LeCC + lwlies: "curated imagery that enhances narrative" only |
| No auto-playing audio | Interface is silent unless explicitly invoked |
| No horizontal scroll | All layouts are vertical — no carousels, no horizontal overflow |
| No serif body copy | Serifs are reserved for editorial display sizes only |
| No color gradients on text | Gradients exist only in backgrounds and glows |
| No more than 3 JSON-LD scripts per page | SEO structured data should not bloat the head |
| No animation on page transitions | Routing is instant — animation begins after mount |
| No font weights above 600 | The PRISMA palette is soft and editorial — not bold/aggressive |

---

## 7. Component Usage Guidelines

### `.poster-card`
- Always use `aspect-ratio: 2/3`
- Hover: translate up + scale very slightly (never more than `scale(1.02)`)
- Color border appears on hover via `::after` pseudo-element
- Glow appears on hover via `box-shadow` with `--prisma-color-glow`

### `.film-grid`
- Default: auto-fill, 200px min
- Featured: first child spans 2×2 — use for editorial highlights
- Never put `.film-grid--featured` inside a narrow container

### `.section-label`
- Always precedes a section of content — never used in isolation
- The decorative line grows from the left by default
- Use `--color` variant on colored hero sections

### `.color-badge`
- Requires `--prisma-color` to be set (otherwise falls back to azul_nocturno)
- Always includes the color dot (`.color-badge__dot`)
- Links to `/colors/{slug}`

### `.btn-primary`
- Used for primary CTAs: "Ver película", "Ver ranking"
- Underline animates out on hover (reverses transform-origin)
- Never has a background fill

### `.btn-ghost`
- Used for secondary actions: "Añadir a lista", "Compartir"
- Thin border, transparent background
- Use `--color` variant on film pages where the border picks up `--prisma-color`

### `.reveal`
- Apply to any element that should animate in on scroll
- Add `data-delay="N"` (in ms) for staggered siblings
- Call `initRevealAnimations()` once per page in a `<script>` tag
- Never apply to above-the-fold content (it's already visible)

---

*PRISMA Design System v1.0 — March 2026*
*References: A24 (score 66), ColorsxStudios (70), Criterion (45), Le Cinéma Club (56), Little White Lies (36), MUBI (36)*
