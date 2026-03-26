#!/usr/local/bin/python3
"""
Phase 2: Cultural Memory - Gemini Prompter
Aligned with color_doctrine.json v1.3 — 18 colors
v5.0 — PERCEPTION-FIRST REWRITE: asks about visual dominance, not emotional symbolism
"""

from typing import Dict, Any


SYSTEM_PROMPT = """You are a visual perception analyst identifying the dominant color in films based on what the eye sees on screen.

YOUR TASK: Identify the SINGLE MOST VISUALLY DOMINANT COLOR that appears on screen as the viewer watches the film.

═══════════════════════════════════════════════════════════════════════════
CRITICAL INSTRUCTION — READ THIS FIRST:

You must answer based ONLY on VISUAL PERCEPTION — what color the eye sees most.
Do NOT base your answer on:
  ✗ Emotional tone or mood
  ✗ Symbolic meaning or themes
  ✗ What the film "represents" philosophically
  ✗ Genre expectations or cultural associations

ONLY answer based on:
  ✓ What color dominates the screen visually
  ✓ Cinematography, lighting, and color grading
  ✓ Costume design throughout the film
  ✓ Set design and production design
  ✓ The most iconic and reproduced frames
═══════════════════════════════════════════════════════════════════════════

ANALYSIS HIERARCHY (check in this order):

1. ICONIC FRAMES: What color dominates the film's most famous, most reproduced images?
   (The frames that appear in posters, critical essays, film history books)

2. COSTUME DESIGN: What colors dominate the characters' clothing across the entire film?
   (Not just one scene — look at the overall wardrobe palette)

3. PRODUCTION DESIGN: What colors dominate the sets, locations, and environments?
   (Interior walls, exterior architecture, natural landscapes)

4. COLOR GRADING: What overall color hue saturates the cinematography?
   (Does the film have a warm/cool grade? What tint dominates the image?)

5. MEMORABLE VISUAL ELEMENTS: What is the single most visually striking color element
   that audiences remember when they recall this film?

═══════════════════════════════════════════════════════════════════════════
EXAMPLES OF CORRECT PERCEPTION-BASED REASONING:

✓ CORRECT: "In the Mood for Love — rojo_pasional"
  Evidence: Maggie Cheung wears red and burgundy cheongsams in every iconic scene.
  The corridor has warm red lighting. Christopher Doyle's cinematography uses deep
  reds and ambers throughout. Every famous still from this film features red.

✓ CORRECT: "The Matrix — verde_distopico"
  Evidence: The digital rain code is bright green. Every scene inside the Matrix
  has a green tint. The fight scenes are bathed in green light. The iconic image
  is Neo surrounded by green code.

✓ CORRECT: "Amélie — amarillo_ludico"
  Evidence: The entire film is color-graded with warm golden yellow. Amélie's
  apartment walls are yellow. The café is yellow. The streets are bathed in
  yellow-gold light. Every frame has a yellow warmth.

✓ CORRECT: "Blade Runner — azul_nocturno"
  Evidence: The film is dominated by deep blue lighting in rain-soaked night scenes.
  Deckard's apartment has blue tones. The final rooftop scene is dark blue. The
  neon signs cast blue reflections.

═══════════════════════════════════════════════════════════════════════════
EXAMPLES OF INCORRECT REASONING (DO NOT DO THIS):

✗ WRONG: "In the Mood for Love — azul_nocturno because it's emotionally melancholic"
  Problem: This ignores visual perception. The film is VISUALLY red (costumes, lighting).
  The emotion is irrelevant — we only care what the eye sees.

✗ WRONG: "Her — magenta_pop because of the colorful OS interface"
  Problem: The OS interface is a small visual element. The DOMINANT color on screen
  is Theodore's red shirt, warm apartment lighting, and Spike Jonze's warm color grade.

✗ WRONG: "Blade Runner — azul_nocturno because it feels dystopian"
  Problem: The color choice is correct, but the REASONING is wrong. We don't care
  what it "feels" like. We care that the lighting is literally blue on screen.

✗ WRONG: "The Grand Budapest Hotel — magenta_pop because it's visually bold"
  Problem: The dominant color is pastel pink/purple (purpura_onirico), not hot magenta.

═══════════════════════════════════════════════════════════════════════════
SCALE REQUIREMENTS — This must work for ANY film:

✓ Silent films from the 1920s
  → May have color tinting (sepia = ambar_desertico, blue tint = azul_nocturno)
  → Pure B&W = claroscuro_dramatico or monocromatico_intimo

✓ Bollywood musicals
  → Vibrant costume design often dominates (analyze the most frequent costume colors)

✓ Nordic noir
  → Often muted palettes (blanco_polar for snow, cian_melancolico for urban rain)

✓ Japanese documentaries
  → Natural light (verde_lima for countryside, cian_melancolico for urban)

✓ Animated films
  → Stylized color (analyze the background palette, not just character design)

✓ Obscure foreign cinema
  → No Hollywood assumptions. Analyze what's actually on screen.

If you genuinely CANNOT determine a dominant color, state "low" confidence and explain why.
If a film is black and white, choose claroscuro_dramatico (high contrast) or
monocromatico_intimo (soft naturalistic).
═══════════════════════════════════════════════════════════════════════════
"""


PRISMA_PALETTE = """
PRISMA OFFICIAL COLOR PALETTE v1.3 — 18 colors (use ONLY these exact IDs):

| ID                    | Color              | HEX     | When to use                                                        | Director / film signatures                        |
|-----------------------|--------------------|---------|--------------------------------------------------------------------|----------------------------------------------------|
| rojo_pasional         | Deep Red           | #8E1B1B | Passion, violence, blood, desire — HUMAN EMOTIONAL RED             | Almodóvar, Wong Kar-wai, Spike Jonze (Her)         |
| naranja_apocaliptico  | Burnt Orange       | #C4471D | Fire, chaos, war, destruction                                      | George Miller, Coppola (Apocalypse Now)            |
| ambar_desertico       | Amber/Gold         | #C98A2E | PAST-looking nostalgia, dust, decay, westerns, faded memory        | Roger Deakins, David Lean, Sergio Leone            |
| amarillo_ludico       | Bright Yellow      | #F2C94C | PRESENT-feeling joy, active playfulness, youth energy, optimism    | Wes Anderson, Jeunet, early Almodóvar              |
| verde_lima            | Light Lime Green   | #7BC96F | Natural sunlight, organic growth, countryside                      | Emmanuel Lubezki, Luca Guadagnino                  |
| verde_esmeralda       | Rich Emerald       | #1F7A5C | Jewel tones, hidden elegance, obsession                            | Hitchcock (Vertigo), Alfonso Cuarón                |
| verde_distopico       | Dark Sickly Green  | #2F4F3E | Digital code, surveillance, cyberpunk, artificial light            | Wachowskis, Ridley Scott (Alien)                   |
| cian_melancolico      | Blue-Green Teal    | #4A7C8C | Urban isolation, rain, cool detachment                             | Sofia Coppola, Michael Mann                        |
| azul_nocturno         | Deep Pure Blue     | #1B2A41 | Profound sorrow, deep night, emotional void                        | Kieślowski (Blue), Villeneuve, Moonlight           |
| violeta_cinetico      | Electric Violet    | #5B3FA4 | Neon energy, 80s kinetic, urban electricity                        | Nicolas Winding Refn, Wong Kar-wai (nights)        |
| purpura_onirico       | Muted Dream Purple | #7A3E6D | Pastel purple, magic realism, liminal poverty                      | Sean Baker, Tim Burton (soft)                      |
| magenta_pop           | Hot Pink/Magenta   | #D63384 | Bold POP CULTURE maximalism, rebellion — NOT emotional red         | Greta Gerwig (Barbie), John Waters                 |
| blanco_polar          | Cold White         | #E8EEF2 | Moral void, clinical cold, winter isolation, existential emptiness | Kieślowski (White), Haneke, Östlund, Fargo         |
| negro_abismo          | Near-Total Black   | #0A0A0F | Gothic darkness, noir extremity, total visual void, menace         | Tim Burton (Batman), Gordon Willis, Se7en          |
| titanio_mecanico      | Metallic Gray      | #8A9199 | Machines, robots, spacecraft, cold industrial future               | Terminator 2, 2001, Ex Machina, Alien              |
| rosa_pastel           | Soft Pastel Pink   | #F4A7B9 | Tender memory, quiet femininity, arthouse nostalgia                | Ed Lachman, Céline Sciamma (Portrait), Carol       |
| claroscuro_dramatico  | B&W High Contrast  | —       | Deep blacks, harsh shadows, expressionist drama                    | Eggers, early Kubrick, German expressionism        |
| monocromatico_intimo  | B&W Soft/Natural   | —       | Gentle naturalistic B&W, intimate humanism                         | Cuarón (Roma), Italian neorealism                  |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL DISAMBIGUATION — read carefully before choosing:

1. rojo_pasional vs magenta_pop — IMPORTANT NEW RULE:
   - rojo_pasional = RED from HUMAN EMOTION. Desire, blood, passion, intensity.
     The color of feelings, bodies, violence, love.
     → Her (the red OS interface and wardrobe), Almodóvar films,
       In the Mood for Love, IT (Pennywise), Suspiria
   - magenta_pop = PINK-MAGENTA from POP CULTURE. Maximalism, iconography,
     commercial rebellion. The color of spectacle, not emotion.
     → Barbie — and almost nothing else at this level of saturation.
   Rule: emotional human red, even if slightly pinkish → rojo_pasional.
         loud pop culture hot pink with zero emotional depth → magenta_pop.
   WARNING: Do NOT use magenta_pop just because a poster has pink tones.
            Ask: is this emotional red or pop culture pink?

2. ambar_desertico vs amarillo_ludico — THE MOST COMMON CONFUSION:
   - ambar_desertico = nostalgia that looks BACKWARD. Dust, decay, faded time.
     → No Country for Old Men, Lawrence of Arabia, Once Upon a Time in Hollywood
   - amarillo_ludico = joy that feels PRESENT and ALIVE. Active energy, play, youth.
     → Amélie, Little Miss Sunshine, Moonrise Kingdom, Wes Anderson in general
   Rule: energetic and playful yellow → amarillo_ludico.
         dusty melancholic gold → ambar_desertico.

3. azul_nocturno vs cian_melancolico:
   - azul_nocturno = DEEP, PURE, SORROWFUL blue. Emotional void, profound night.
     → Three Colors: Blue, Blade Runner, Moonlight
   - cian_melancolico = TEAL, BLUE-GREEN, urban cool detachment.
     → Lost in Translation, Heat (Mann)
   Rule: deep sorrowful blue → azul_nocturno. Teal or urban → cian_melancolico.

4. purpura_onirico vs magenta_pop:
   - purpura_onirico = MUTED, DREAMY, PASTEL purple. Magical poverty, liminal.
     → The Florida Project motel
   - magenta_pop = LOUD, HOT PINK, maximalist pop energy.
     → Barbie
   Rule: soft dreamy purple → purpura_onirico. Loud hot pink → magenta_pop.

5. verde_distopico vs verde_lima:
   - verde_distopico = DARK, ARTIFICIAL, SICKLY green. Technology, control.
     → The Matrix
   - verde_lima = NATURAL, SUNLIT, ORGANIC green. Nature, youth.
     → Call Me By Your Name
   Rule: dark digital green → verde_distopico. Natural light green → verde_lima.

6. blanco_polar vs titanio_mecanico vs claroscuro_dramatico:
   - blanco_polar = WHITE as dominant color in a COLOR film. Cold, empty, snow.
     → Three Colors: White, Fargo, Funny Games
   - titanio_mecanico = METALLIC GRAY. Machines, robots, hard sci-fi, spacecraft.
     → Terminator 2, 2001, Ex Machina, Alien
   - claroscuro_dramatico = BLACK AND WHITE FILM with dramatic contrast.
     → The Lighthouse, Nosferatu, Schindler's List
   Rule: color film dominated by white → blanco_polar.
         color film dominated by metal/machines → titanio_mecanico.
         actual B&W film with drama → claroscuro_dramatico.

7. negro_abismo vs claroscuro_dramatico vs azul_nocturno:
   - negro_abismo = BLACK as dominant color in a COLOR film. Gothic, void, menace.
     → Batman (1989), Se7en, dark superhero films
   - claroscuro_dramatico = actual B&W FILM with high contrast.
     → The Lighthouse, Nosferatu
   - azul_nocturno = deep BLUE night, not pure black.
     → Blade Runner, Three Colors: Blue
   Rule: color film mostly black → negro_abismo.
         actual B&W film → claroscuro_dramatico.
         deep blue night → azul_nocturno.

8. SPECIAL CASE — Wong Kar-wai films:
   - Chungking Express → warm yellow neon of the poster = amarillo_ludico
   - In the Mood for Love → the red dress and deep shadows = rojo_pasional
   - 2046 → cold blues and deep purples = azul_nocturno
   When in doubt with Wong Kar-wai, ask: what color is the POSTER?

9. rosa_pastel vs magenta_pop vs purpura_onirico:
   - rosa_pastel = SOFT, MUTED, DESATURATED pink. Tenderness, nostalgia, quiet femininity.
     Arthouse romance, memory, period costumes. Film grain warmth.
     → Portrait of a Lady on Fire, Carol, Lost in Translation
   - magenta_pop = LOUD, HOT, SATURATED pink. Pop culture maximalism, bold rebellion.
     → Barbie
   - purpura_onirico = DREAMY PURPLE, not pink. Pastel lavender, magical poverty.
     → The Florida Project
   Rule: soft muted pink → rosa_pastel.
         loud hot pink → magenta_pop.
         dreamy purple → purpura_onirico.

10. COLOR ↔ TEMPERATURA COHERENCE:
    calido_apasionado should RARELY pair with azul_nocturno.
    Warm temperature correlates with: rojo_pasional, ambar_desertico,
    amarillo_ludico, naranja_apocaliptico, rosa_pastel.
    If assigning calido_apasionado + azul_nocturno, explain explicitly why
    the visual color contradicts the emotional temperature.

11. verde_esmeralda disambiguation:
    - RICH, JEWEL-TONED emerald. Elegant, obsessive, period.
    → Vertigo (green neon hotel, Madeleine's suit), Portrait of a Lady on Fire
      (French countryside + period costumes), Carol (Todd Haynes jewel tones),
      Far From Heaven, Parasite (the wealthy Park house interiors)
    Rule: expensive/jewel/period green → verde_esmeralda
          natural sunlit → verde_lima
          digital/artificial → verde_distopico

12. DISTRIBUTION CALIBRATION — CRITICAL:
    No color should exceed 20% in a healthy catalog.

    BEFORE choosing claroscuro_dramatico verify:
    - Is the film ACTUALLY black and white?
    - Does chiaroscuro define the ENTIRE film, not just some scenes?
    - Silent films with sepia tinting → ambar_desertico, not claroscuro
    - Soft naturalistic B&W → monocromatico_intimo

    BEFORE choosing azul_nocturno verify:
    - Is blue LITERALLY VISIBLE on screen, not just the emotional mood?
    - Could this be cian_melancolico (teal), verde_distopico (digital),
      or blanco_polar (cold/clinical)?

    UNDERUSED colors — consider actively:
    - naranja_apocaliptico: Apocalypse Now (napalm/jungle fire throughout),
      Mad Max Fury Road, Children of Men, Days of Heaven (harvest fire)
    - purpura_onirico: Mulholland Drive (Club Silencio neon),
      Grand Budapest Hotel (Mendl's pastels), Mirror (Tarkovsky dreams)
    - violeta_cinetico: Drive (Refn neon), Only God Forgives, Climax
    - verde_esmeralda: Vertigo, Portrait of a Lady on Fire, Carol, Parasite
    - rosa_pastel: Portrait of a Lady on Fire, Carol, Mouchette, Certain Women
    - negro_abismo: Se7en, Eraserhead, darkest Lynch, Batman (1989)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def build_cultural_memory_prompt(
    work_id: str,
    title: str,
    year: int,
    director: str = None,
    countries: list = None,
    genres: list = None
) -> str:

    context_parts = [f"Film: {title} ({year})"]
    if director:
        context_parts.append(f"Director: {director}")
    if genres:
        context_parts.append(f"Genres: {', '.join(genres)}")
    if countries:
        context_parts.append(f"Countries: {', '.join(countries)}")

    film_context = "\n".join(context_parts)

    prompt = f"""{film_context}

{PRISMA_PALETTE}

YOUR TASK: Identify the SINGLE MOST VISUALLY DOMINANT COLOR in "{title}" ({year})

STEP 1: VISUAL PERCEPTION ANALYSIS

Answer this question: What color dominates the screen when you watch this film?

Check these visual elements IN ORDER:
1. What color dominates the most iconic, most reproduced frames from this film?
2. What colors dominate the costume design throughout the runtime?
3. What colors dominate the production design (sets, locations, environments)?
4. What color hue dominates the cinematography and color grading?
5. What is the single most visually memorable color element from this film?

You MUST provide specific visual evidence. Name 2-3 concrete examples:
- "Maggie Cheung's red cheongsams in the corridor scenes"
- "The green digital rain code in the action sequences"
- "The warm yellow color grade in every interior scene"

DO NOT say vague things like "the film has a melancholic tone" or "it feels blue."
ONLY cite what the eye literally sees on screen.

STEP 2: MAP TO PRISMA PALETTE

Choose the SINGLE color ID from the Prisma palette table above that best matches
the visual dominance you identified.

If choosing between similar colors (e.g. rojo_pasional vs naranja_apocaliptico,
or ambar_desertico vs amarillo_ludico), explicitly state why you chose one over
the other using the disambiguation rules in the table.

STEP 3: NUMERIC COLOR RANK (0.0 to 1.0)

Assign a precise numeric score representing how strongly this color dominates the film.
Score to EXACTLY TWO DECIMAL PLACES (e.g., 0.94, not 0.9 or 0.940).

COLOR RANK SCORING GUIDE (0.0 to 1.0)
Score to exactly two decimal places. Justify your exact number in color_rank_reasoning.

BUCKET DEFINITIONS WITH CANONICAL EXAMPLES:

0.95 - 1.00 │ THIS COLOR IS THE FILM. Undisputed. Every iconic frame, every 
             │ poster, every cultural reference points to one color.
             │ Examples:
             │   → The Matrix: verde_distopico 0.97 (digital rain defines 85%+ of frames)
             │   → Barbie: magenta_pop 0.96 (every set, costume, poster is hot pink)
             │   → Roma: monocromatico_intimo 0.99 (literally shot in B&W)
             │   → Three Colors: Blue: azul_nocturno 0.98 (the film IS blue)
             │ Use this range ONLY when no other color meaningfully competes.

0.85 - 0.94 │ DOMINANT but one other color competes meaningfully (15-25% of frames).
             │ Examples:
             │   → Moonrise Kingdom: amarillo_ludico 0.90 (yellow dominates but 
             │     amber is consistently present in earth tones throughout)
             │   → Blade Runner: azul_nocturno 0.92 (deep blue dominates but 
             │     violeta_cinetico neon signs create real visual competition)
             │   → Mad Max Fury Road: naranja_apocaliptico 0.91 (orange dominant 
             │     but teal sky genuinely competes in 20%+ of shots)
             │ Use this range when you find yourself writing "dominant but..."

0.70 - 0.84 │ CLEAR PRIMARY but the film is genuinely multi-color. The iconic 
             │ color wins but another color is equally memorable to audiences.
             │ Examples:
             │   → Kill Bill Vol.1: amarillo_ludico 0.76 (yellow tracksuit is 
             │     THE iconic image but red blood is equally present and memorable)
             │   → Apocalypse Now: naranja_apocaliptico 0.78 (napalm and fire 
             │     are iconic but deep jungle greens dominate equal screen time)
             │   → Drive: violeta_cinetico 0.75 (neon purple nights are iconic 
             │     but warm daytime scenes and black interiors split the palette)
             │ Use this range when TWO colors are both genuinely iconic in the film.

0.50 - 0.69 │ CONTESTED. Two or more colors fight for dominance. This color wins 
             │ slightly but a casual viewer might name a different color.
             │ Examples:
             │   → Pulp Fiction: ambar_desertico 0.58 (warm amber dominates diner 
             │     scenes but the film has no single color identity — red, yellow,
             │     and brown all compete without a clear winner)
             │   → The Godfather: ambar_desertico 0.55 (warm but so desaturated 
             │     that no single color clearly dominates — multiple viewers would 
             │     name different colors)
             │   → A film where you're genuinely unsure which color to pick
             │ Use this range when you debate between two colors before deciding.

0.30 - 0.49 │ WEAK ASSIGNMENT. The film has no strong color identity. This is 
             │ the best match from the palette but it's not truly iconic.
             │ Examples:
             │   → A naturalistic drama with no color grading
             │   → A film where every scene has a different color palette
             │   → Documentary-style films with no visual stylization
             │ Use this range when the color assignment feels like a guess.

CRITICAL RULE: If you are assigning a canonical film (The Matrix, Barbie, Roma, 
Three Colors trilogy, etc.) you may use 0.95+. For ALL OTHER FILMS, start your 
reasoning at 0.70 and justify upward. Default assumption is 0.75, not 0.95.
Reaching 0.90+ requires explicit justification of WHY this film belongs with 
the most iconic examples.

JUSTIFICATION REQUIRED:
You MUST explain your exact score in "color_rank_reasoning". State:
- What percentage of iconic frames feature this color
- What specific visual elements justify the score
- Why you deducted points (if any) from 1.0
- What competing colors exist (if any) and why they don't win

Examples of good reasoning:
- "0.94: Green digital rain dominates 80%+ of The Matrix's iconic frames and all marketing.
   Deducted 0.06 because black is significant in real-world scenes (~20% runtime)."
- "0.76: Yellow is Kill Bill's poster color and Beatrix's iconic tracksuit, but deep red
   blood and lighting compete equally in fight scenes. Genuinely dual-color film."
- "0.58: Warm amber dominates diner scenes in Pulp Fiction but the film has no single 
   color identity — red, yellow, and brown all compete without a clear winner."

STEP 4: SECONDARY COLORS (optional, 1-2 maximum)

List 1-2 other Prisma color IDs that have significant visual presence, but are NOT
the dominant color. Only include colors that genuinely appear frequently on screen.

If no secondary colors apply, return an empty array [].

═══════════════════════════════════════════════════════════════════════════
DIMENSION ANALYSIS — THREE AXES:

STEP 5 — RITMO VISUAL (visual rhythm) — choose ONE:
  dinamico_frenetico   → Editing under 2 seconds/shot. Pure kinetic energy.
                         → Mad Max: Fury Road, Whiplash, City of God, Requiem for a Dream
  dinamico_energico    → Fast but coherent. Action with clarity.
                         → Children of Men, No Country for Old Men, The Dark Knight,
                           Do the Right Thing, Nashville (Altman's roving multi-camera)
  moderado_balanceado  → ONLY when truly neither fast nor slow. Classical pacing.
                         → Most standard narrative films. Use sparingly — this is NOT the default.
  lento_contemplativo  → Long takes. Scenes breathe. Time felt as material.
                         → Stalker, Barry Lyndon, Tokyo Story, La Dolce Vita, 2001: A Space Odyssey,
                           Apocalypse Now (extended jungle sequences), Wong Kar-wai
  estatico_ritualistico → Extreme slowness. Duration as artistic statement.
                         → Jeanne Dielman (Akerman), Sátántangó, Béla Tarr, Ozu late films

  ⚠️ WARNING: moderado_balanceado is chronically over-assigned.
  If a film has ANY notable pacing characteristic, choose that value instead.
  Only use moderado_balanceado for truly unremarkable pacing (e.g. a generic thriller).
  Ask: is this film known for its pace? If yes, it is NOT moderado_balanceado.

STEP 6 — TEMPERATURA EMOCIONAL (emotional temperature) — choose ONE:
  calido_apasionado    → Intense positive emotion. Love, joy, passion, vitality.
                         → Cinema Paradiso, Life is Beautiful, Amélie, Do the Right Thing
  calido_nostalgico    → Warm but bittersweet. Memory, loss, tenderness.
                         → Tokyo Story, Barry Lyndon, The Godfather, Nashville, Amarcord
  neutral_contemplativo → Observational distance. Neither warm nor cold.
                         → Jeanne Dielman, Caché, Le Fils, most Chantal Akerman
  frio_melancolico     → Sadness, alienation, grief, quiet despair.
                         → Three Colors: Blue, Moonlight, Stalker, Mulholland Drive
  frio_perturbador     → Cold + disturbing. Menace, dread, psychological horror.
                         → Funny Games, Caché, Eraserhead, The White Ribbon

  ⚠️ WARNING: frio_melancolico is chronically over-assigned.
  Many films feel melancholic but are actually calido_nostalgico (warm + bittersweet).
  Ask: is this film emotionally cold/alienated, or warm but sad?
  The Godfather = calido_nostalgico (family, nostalgia, lament), NOT frio_melancolico.
  Barry Lyndon = calido_nostalgico (amber candlelight, elegiac tone), NOT calido_apasionado.

STEP 7 — GRADO ABSTRACCION (abstraction level) — choose ONE:
  hiperrealista          → Ultra-realistic. Documentary-style. Reality without filter.
                           → Roma (Cuarón), Bicycle Thieves, Shoah, any neorealism,
                             Jeanne Dielman, Harlan County USA
  realista_estilizado    → Realistic but with clear visual choices. Recognizable world, crafted.
                           → The Godfather, Nashville, Stalker (partly), most quality narrative cinema
  estilizado             → Clearly artificial. Style over realism. Visible directorial hand.
                           → Apocalypse Now, Mulholland Drive, Wong Kar-wai, Almodóvar,
                             Barry Lyndon (Barry Lyndon = very), 2001 (outer space sequences)
  muy_estilizado         → Extreme stylization. World barely resembles reality.
                           → Wes Anderson, Dogville, The Lobster, early Godard
  abstracto_experimental → Not narrative. Pure visual/formal experiment.
                           → Meshes of the Afternoon, Man with a Movie Camera, Stan Brakhage

  ⚠️ WARNING: estilizado is chronically over-assigned.
  Most quality narrative films are realista_estilizado, not estilizado.
  Only use estilizado when the artificial quality is PROMINENT and INTENTIONAL.
  Neorealism, social realism, naturalism → hiperrealista o realista_estilizado.
═══════════════════════════════════════════════════════════════════════════

CRITICAL NEGATIVE INSTRUCTION — READ BEFORE ANSWERING:

DO NOT choose a color based on:
  ✗ What the film is "about" thematically
  ✗ The emotional mood or tone
  ✗ Symbolic meaning
  ✗ Genre conventions
  ✗ Your interpretation of what the color "represents"

ONLY choose based on:
  ✓ What color you literally see most on screen
  ✓ Specific visual elements you can name (costumes, sets, lighting, grading)
═══════════════════════════════════════════════════════════════════════════

RESPOND WITH VALID JSON ONLY (no markdown, no commentary):

{{
  "iconic_color": "verde_distopico",
  "color_rank": 0.94,
  "color_rank_reasoning": "Green dominates 85%+ of The Matrix's iconic frames. The digital rain code, Matrix simulation scenes, and all fight choreography use green lighting. Deducted 0.06 because real-world scenes (~15% runtime) use dark blue/black with no green presence.",
  "color_reasoning": "The Matrix's visual palette is dominated by green. The digital rain code is bright green. All scenes inside the Matrix simulation have a green color grade. The fight choreography is lit with green. The most iconic images (Neo dodging bullets, the opening credits) are saturated with green. Chose verde_distopico over verde_lima because this green is dark, artificial, and digital — not natural sunlight.",
  "secondary_colors": ["negro_abismo"],
  "secondary_reasoning": {{
    "negro_abismo": "Real world scenes and the Nebuchadnezzar ship interior are near-total black with minimal light"
  }},
  "visual_rhythm": "dinamico_energico",
  "emotional_temperature": "frio_perturbador",
  "abstraction_level": "estilizado",
  "supporting_evidence": [
    "Green digital rain code in opening credits and action scenes",
    "Green color grade saturates all Matrix simulation scenes",
    "Iconic bullet-time sequence bathed in green light"
  ]
}}"""

    return prompt


def extract_perception_response(llm_response: str) -> dict:
    import json

    try:
        data = json.loads(llm_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM response is not valid JSON: {e}\nRaw: {llm_response[:300]}")

    required_fields = [
        "iconic_color",
        "color_rank",
        "color_rank_reasoning",
        "color_reasoning",
        "secondary_colors",
        "visual_rhythm",
        "emotional_temperature",
        "abstraction_level",
    ]

    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"LLM response missing required fields: {missing}")
    
    # Validate color_rank is float between 0.0 and 1.0
    if not isinstance(data.get("color_rank"), (int, float)):
        raise ValueError(f"color_rank must be a number, got: {type(data.get('color_rank'))}")
    
    color_rank = float(data["color_rank"])
    if not (0.0 <= color_rank <= 1.0):
        raise ValueError(f"color_rank {color_rank} out of bounds [0.0, 1.0]")
    
    # Validate color_rank_reasoning is present and non-empty
    if not data.get("color_rank_reasoning") or not isinstance(data["color_rank_reasoning"], str):
        raise ValueError("color_rank_reasoning must be a non-empty string")

    # supporting_evidence is optional — fallback to color_reasoning
    if "supporting_evidence" not in data or not data["supporting_evidence"]:
        data["supporting_evidence"] = [data.get("color_reasoning", "No evidence provided")]

    return data
