# Doctrine Changelog

## v1.0 (2026-02-02)

### Initial Release

**color_doctrine.json**
- Defined 12 Prisma colors with hex values, moods, and genre associations
- Established 2 monochromatic modes (claroscuro_dramatico, monocromatico_intimo)
- Created assignment rules for primary/secondary colors and monochromatic detection
- Documented edge cases (color shift films, desaturated films, multi-segment films)

**score_doctrine.json**
- Defined weighted scoring formula:
  - AI confidence: 30%
  - Authorship: 25%
  - Cultural recognition: 30%
  - Popularity: 15%
- Established tier thresholds (canon: 95+, core: 85+, strong: 70+, peripheral: 50+)
- Created tier ranking rules (canon: editorial, core: hybrid, strong/peripheral: numeric)
- Documented cultural weight signals (festivals, critical canon, cinematography awards, arthouse distribution)
- Defined authorship signals (DP prestige, director visual style, production design)
- Established popularity normalization (log scale to prevent blockbuster bias)

**tier_doctrine.json**
- Defined 5 tiers (canon, core, strong, peripheral, uncertain)
- Created tier transition rules (promotion/demotion criteria)
- Established ranking methodology per tier
- Defined UI design guidelines for visual hierarchy

### Notes

This is the foundational doctrine release. All values are subject to refinement based on:
- Pipeline testing results
- Editorial team feedback
- User engagement patterns
- Algorithm performance

### Next Steps

- Implement pipeline scripts that read from this doctrine
- Run initial film corpus through scoring system
- Validate tier distributions (expect: few canon, many strong)
- Calibrate thresholds based on real data
