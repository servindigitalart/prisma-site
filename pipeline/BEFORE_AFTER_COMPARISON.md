================================================================================
CANONICAL TEST SUITE - BEFORE vs AFTER COMPARISON
================================================================================

Film                          | BEFORE | AFTER | CHANGE | Notes
------------------------------|--------|-------|--------|-------------------
The Matrix                    |  0.97  | 0.97  |  0.00  | Unchanged (perfect)
In the Mood for Love          |  1.00  | 0.95  | -0.05  | Less MUBI/Criterion boost
Amélie                        |  0.99  | 0.95  | -0.04  | Less MUBI boost
Blade Runner                  |  0.97  | 0.94  | -0.03  | Less boosts
Mad Max: Fury Road            |  0.93  | 0.90  | -0.03  | Recency penalty applied
Moonlight                     |  0.96  | 0.94  | -0.02  | Less boosts
The Grand Budapest Hotel      |  0.97  | 0.92  | -0.05  | Less boosts + recency
Her                           |  0.95  | 0.90  | -0.05  | Less MUBI boost
The Lighthouse                |  1.00  | 0.97  | -0.03  | Recency penalty
Barbie                        |  0.96  | 0.91  | -0.05  | Strong recency penalty
Call Me by Your Name          |  0.92  | 0.86  | -0.06  | More realistic
Lost in Translation           |  0.99  | 0.92  | -0.07  | Less boosts
No Country for Old Men        |  0.95  | 0.90  | -0.05  | Less MUBI boost
Drive                         |  0.91  | 0.75  | -0.16  | ✅ MAJOR IMPROVEMENT
Three Colors: White           |  1.00  | 0.98  | -0.02  | Still near-perfect

STATISTICS:
  Before avg: 0.96 | After avg: 0.92 | Improvement: -0.04
  Before range: 0.91-1.00 | After range: 0.75-0.98
  Before stdev: 0.03 | After stdev: 0.06 (more variation ✅)

BIGGEST IMPROVEMENT:
  Drive: 0.91 → 0.75 (-0.16)
  → Now correctly reflects purple/violet as clear primary but genuinely 
    contested by warm tones and noir blacks. This is the kind of film
    that should score in the 0.70-0.84 bucket.

DISTRIBUTION SHIFT:
  Before:
    - 0.95-1.00: 12 films (80%)
    - 0.85-0.94: 3 films (20%)
  
  After:
    - 0.95-1.00: 5 films (33%)  ← 47% reduction in top bucket
    - 0.85-0.94: 9 films (60%)  ← Most films now here
    - 0.70-0.84: 1 film (7%)    ← Drive correctly placed

================================================================================
PERIPHERAL TEST SUITE - NEW RESULTS
================================================================================

Film                     | Score | Bucket      | Expected    | Status
-------------------------|-------|-------------|-------------|--------
Kill Bill Vol.1          | 0.76  | Clear (0.70-0.84) | 0.70-0.84 | ✅ PASS
Apocalypse Now           | 0.78  | Clear (0.70-0.84) | 0.70-0.84 | ✅ PASS
Vertigo                  | 0.84  | Clear (0.70-0.84) | 0.72-0.85 | ✅ PASS
Pulp Fiction             | 0.58  | Contested (0.50-0.69) | 0.50-0.69 | ✅ PASS
Midnight in Paris        | 0.90  | Dominant (0.85-0.94) | 0.65-0.82 | ⚠️  HIGH
Lost Highway             | 0.88  | Dominant (0.85-0.94) | 0.65-0.82 | ⚠️  HIGH (wrong color)
Garden State             | 0.88  | Dominant (0.85-0.94) | 0.55-0.75 | ⚠️  HIGH (wrong color)
The Godfather            | 0.90  | Dominant (0.85-0.94) | 0.50-0.70 | ⚠️  HIGH

SUCCESS RATE:
  - Correct color + in range: 4/8 (50%)
  - Correct color but high: 2/8 (25%)
  - Wrong color: 2/8 (25%)

LOWER BUCKETS VALIDATED:
  ✅ 0.50-0.69 (Contested): Pulp Fiction 0.58
  ✅ 0.70-0.84 (Clear): Kill Bill 0.76, Apocalypse Now 0.78, Vertigo 0.84

INFLATION STILL PRESENT:
  ⚠️  Midnight in Paris, The Godfather both scored 0.90 (expected 0.65-0.82)
  → Classic films still get preferential treatment from Gemini

================================================================================
COMBINED INSIGHTS (23 total films tested)
================================================================================

SCORE DISTRIBUTION:
  0.95-1.00 (Undisputed):     5 films (22%)  ← Only true icons
  0.85-0.94 (Dominant):      13 films (57%)  ← Most films
  0.70-0.84 (Clear primary):  4 films (17%)  ← Multi-color
  0.50-0.69 (Contested):      1 film  (4%)   ← Weak identity
  
AVERAGE SCORES BY TIER:
  Canonical films: 0.92 (expected: high)
  Peripheral films: 0.81 (expected: lower)
  Gap: 11 points ✅

FILMS SCORING EXACTLY AS EXPECTED:
  1. The Matrix 0.97 - undisputed green
  2. Kill Bill 0.76 - yellow/red dual-color
  3. Apocalypse Now 0.78 - orange/green dual-color
  4. Pulp Fiction 0.58 - contested warm palette
  5. Drive 0.75 - purple but multi-color

FILMS NEEDING ATTENTION:
  1. Midnight in Paris 0.90 - should be ~0.75
  2. The Godfather 0.90 - should be ~0.60
  → Both are classic films that Gemini treats too favorably

COLOR ASSIGNMENT ACCURACY:
  21/23 correct (91.3%) ✅
  Errors: Lost Highway (wrong), Garden State (wrong)

================================================================================
VERDICT: SYSTEM IS SIGNIFICANTLY IMPROVED
================================================================================

✅ ACHIEVED:
  - Expanded score range (0.58-0.98 vs 0.91-1.00)
  - Better distribution (bell curve at 0.85-0.94)
  - Lower buckets being used appropriately
  - Cultural weights subtle and bounded
  - Differentiation between canonical and peripheral

⚠️  REMAINING ISSUES:
  - Some classic films still score high (The Godfather 0.90)
  - 2 color assignment errors in ambiguous cases

💡 RECOMMENDATION:
  Ship v2.0 with current system. Monitor score distribution with full corpus.
  If inflation persists with 100+ films, strengthen CRITICAL RULE in prompt.
