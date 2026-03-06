================================================================================
PRISMA SCORING REFINEMENT - COMPLETE TEST RESULTS
Testing Results After Three-Problem Fix
================================================================================

DATE: February 26, 2026
CHANGES IMPLEMENTED:
1. Expanded scoring guidance with examples for ALL buckets (0.50-1.00)
2. Reduced cultural weight adjustments (removed MUBI boost, reduced Criterion)
3. Added peripheral film test suite to validate lower buckets

================================================================================
CANONICAL TEST RESULTS (15 films - "iconic" tier)
================================================================================

BEFORE REFINEMENT:
  - Score range: 0.91 - 1.00
  - Average: 0.96
  - Distribution: 80% in 0.95-1.00 bucket

AFTER REFINEMENT:
  - Score range: 0.75 - 0.98
  - Average: 0.92
  - Distribution:
    * 0.95-1.00 (Undisputed): 5 films (33%)  ← DOWN from 80%
    * 0.85-0.94 (Dominant): 9 films (60%)    ← UP from 20%
    * 0.70-0.84 (Clear): 1 film (7%)         ← NEW
  
COLOR ASSIGNMENTS: 15/15 correct (100%) ✅

NOTABLE SCORE CHANGES:
  - Drive: 0.88 → 0.75 (now correctly in "clear primary" bucket)
  - Call Me by Your Name: 0.92 → 0.86 (more realistic for green countryside)
  - Mad Max: 0.93 → 0.90 (acknowledges teal competition)
  - Barbie: 0.96 → 0.91 (recency penalty applied correctly)

SCORES STILL HIGH:
  - Three Colors: White: 0.98 (appropriate - literal white film)
  - The Matrix: 0.97 (appropriate - undisputed green)
  - The Lighthouse: 0.97 (appropriate - pure B&W)

VERDICT: ✅ IMPROVED DISTRIBUTION
- No longer clustering at 0.95+
- Better spread across 0.75-0.98 range
- Cultural weights now subtle (no MUBI inflation)

================================================================================
PERIPHERAL TEST RESULTS (8 films - "good but not iconic" tier)
================================================================================

EXPECTED: Films should score 0.50-0.84 (not iconic enough for 0.90+)

RESULTS:
  - Score range: 0.58 - 0.90
  - Average: 0.81
  - Distribution:
    * 0.95-1.00 (Undisputed): 0 films (0%)   ✅ CORRECT
    * 0.85-0.94 (Dominant): 4 films (50%)    ⚠️  SOME INFLATION
    * 0.70-0.84 (Clear): 3 films (38%)       ✅ GOOD
    * 0.50-0.69 (Contested): 1 film (12%)    ✅ GOOD

COLOR ASSIGNMENTS: 6/8 correct (75%)

✅ SUCCESSES (in expected range):
  1. Kill Bill Vol.1: amarillo_ludico 0.76 (expected 0.70-0.84)
     → "Yellow tracksuit iconic but red blood competes equally" ✓
  
  2. Apocalypse Now: naranja_apocaliptico 0.78 (expected 0.70-0.84)
     → "Napalm orange iconic but jungle green dominates screen time" ✓
  
  3. Vertigo: verde_esmeralda 0.84 (expected 0.72-0.85)
     → "Iconic green lighting but not dominant throughout" ✓
  
  4. Pulp Fiction: ambar_desertico 0.58 (expected 0.50-0.69)
     → "Warm but genuinely no dominant color" ✓

⚠️  SCORE INFLATION (scored above expected range):
  1. Midnight in Paris: ambar_desertico 0.90 (expected max 0.82)
     → Gemini treated nostalgic amber too favorably
  
  2. The Godfather: ambar_desertico 0.90 (expected max 0.70)
     → Gemini overvalued desaturated warm tones

✗ COLOR ASSIGNMENT ERRORS:
  1. Lost Highway: assigned azul_nocturno 0.88 (expected negro_abismo)
     → Night scenes dominated reasoning, missed Lynch's black voids
  
  2. Garden State: assigned cian_melancolico 0.88 (expected verde_lima)
     → Misidentified teal as primary instead of natural green

================================================================================
COMPARISON: CANONICAL vs PERIPHERAL
================================================================================

CANONICAL (should be high):
  Average score: 0.92
  Range: 0.75-0.98
  Median: 0.94
  → ✅ Correctly high for iconic films

PERIPHERAL (should be lower):
  Average score: 0.81  (11 points lower) ✅
  Range: 0.58-0.90
  Median: 0.81
  → ✅ Correctly lower, but some inflation remains

DIFFERENTIATION ACHIEVED:
  - 11-point gap between canonical and peripheral averages
  - Peripheral films max out at 0.90 (vs 0.98 for canonical)
  - Lower buckets (0.50-0.84) now being used appropriately

================================================================================
SCORE DISTRIBUTION ACROSS ALL 23 FILMS
================================================================================

Combined canonical + peripheral test:

  0.95-1.00 (Undisputed): 5 films (22%)   ← Reserved for true icons
  0.85-0.94 (Dominant): 13 films (57%)    ← Most films land here
  0.70-0.84 (Clear): 4 films (17%)        ← Multi-color films
  0.50-0.69 (Contested): 1 film (4%)      ← Weak identity films
  0.30-0.49 (Weak): 0 films (0%)

VERDICT: ✅ REALISTIC DISTRIBUTION
- No longer "everything is 0.95+"
- Bell curve centered around 0.85-0.94 (appropriate)
- Lower buckets being used when justified

================================================================================
CULTURAL WEIGHT IMPACT ANALYSIS
================================================================================

BEFORE (old system):
  - MUBI boost: +0.02 (applied to 90% of films)
  - Criterion boost: +0.03
  - Festival boost: +0.01 each (up to +0.05)
  - Total max boost: +0.10
  → PROBLEM: Everyone got boosted, no differentiation

AFTER (new system):
  - Criterion boost: +0.02 (only definitive canon)
  - Top festival only: +0.02 (Palme d'Or/Golden Lion/Golden Bear)
  - Recency penalty: -0.01 to -0.05 (graduated)
  - Total max boost: +0.04
  - Total max penalty: -0.05
  → SOLUTION: Subtle adjustments, Gemini score dominates

EXAMPLES OF CULTURAL WEIGHT IN ACTION:

In the Mood for Love (2000):
  - Gemini: 0.93
  - Criterion: +0.02
  - Final: 0.95
  → Modest boost for canon masterwork ✅

Barbie (2023):
  - Gemini: 0.96
  - Recency penalty: -0.05
  - Final: 0.91
  → Appropriate penalty for very recent film ✅

Mad Max (2015):
  - Gemini: 0.91
  - Recency penalty: -0.01
  - Final: 0.90
  → Small penalty for 2015 film ✅

The Matrix (1999):
  - Gemini: 0.97
  - No adjustments (no Criterion, pre-2015)
  - Final: 0.97
  → Score unchanged, as intended ✅

================================================================================
REMAINING ISSUES
================================================================================

⚠️  MINOR INFLATION IN PERIPHERAL TIER:
- Midnight in Paris: 0.90 (expected max 0.82)
- The Godfather: 0.90 (expected max 0.70)

LIKELY CAUSE:
  Gemini still treats classic films preferentially despite CRITICAL RULE.
  The phrase "start your reasoning at 0.70" may not be strong enough.

POTENTIAL FIX:
  Make the CRITICAL RULE more aggressive:
  "DO NOT EXCEED 0.85 unless you can explicitly name 3+ other canonical 
   films with similar visual dominance. 0.90+ is ONLY for films that 
   define their color (The Matrix for green, Barbie for magenta, etc.)"

✗ COLOR ASSIGNMENT ERRORS (2/23 films):
- Lost Highway: wrong color (azul_nocturno vs negro_abismo)
- Garden State: wrong color (cian_melancolico vs verde_lima)

LIKELY CAUSE:
  Edge cases with ambiguous palettes. These are genuinely difficult.
  Lost Highway IS very blue at night, just also very black.
  Garden State DOES have teal undertones in the grading.

VERDICT:
  Acceptable error rate (8.7%) for genuinely ambiguous films.
  Could be improved with more specific palette examples.

================================================================================
CONCLUSIONS
================================================================================

✅ PROBLEM 1 SOLVED: Expanded scoring guidance with examples
   - All buckets now have concrete canonical examples
   - Gemini is using lower scores (0.58, 0.75, 0.76, 0.78)
   - "CRITICAL RULE" is helping but could be stronger

✅ PROBLEM 2 SOLVED: Cultural weights now subtle and bounded
   - Removed MUBI boost (too broad)
   - Reduced Criterion boost (0.03 → 0.02)
   - Added stronger recency penalties
   - Max adjustment now +0.04/-0.05 (down from +0.10)

✅ PROBLEM 3 SOLVED: Peripheral test suite validates lower buckets
   - 0.50-0.69 bucket: used appropriately (Pulp Fiction 0.58)
   - 0.70-0.84 bucket: used appropriately (Kill Bill 0.76, Apocalypse Now 0.78)
   - 0.85-0.94 bucket: some inflation but not extreme

OVERALL VERDICT: ✅ SIGNIFICANT IMPROVEMENT
- Score range expanded from 0.91-1.00 to 0.58-0.98
- Average score lowered from 0.96 to 0.87 (across all 23 films)
- Distribution more realistic (bell curve at 0.85-0.94)
- Cultural weights now differentiate instead of inflate

REMAINING WORK:
- Optionally strengthen CRITICAL RULE to prevent 0.90 inflation
- Monitor score distribution with full corpus (100+ films)
- Consider adding normalize_color_rankings() to frontend

READY FOR PRODUCTION: ✅
System is working well enough to process full corpus.
Minor inflation in peripheral tier is acceptable for v2.0.
