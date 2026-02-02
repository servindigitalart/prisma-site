# Prisma Evidence Layer v2.0

## Purpose of Evidence Layer

The **Evidence Layer v2.0** is an expanded structured repository of cinema color research extracted from the comprehensive "Cinema Color Research Project Corpus" document. This layer provides:

- **Cinematographer philosophies** and documented approaches to color
- **Director color authorship** patterns and strategies
- **Film case studies** with detailed color analysis
- **Cinematic movements and periods** with their color characteristics
- **Color themes** and their narrative functions
- **Technologies** and their aesthetic impacts
- **Politics and representation** in color usage

This is **descriptive research**, not prescriptive rules.

## Relationship to Doctrine

**CRITICAL**: This evidence layer **SUPPORTS** Prisma's doctrine but **NEVER OVERRIDES** it.

### Evidence vs. Doctrine Hierarchy:
1. **Doctrine** (pipeline/doctrine/) = **NORMATIVE** - Defines rules, thresholds, and decision logic
2. **Evidence** (pipeline/evidence/) = **DESCRIPTIVE** - Provides research context and reference material
3. **Editorial** (pipeline/editorial/) = **AUTHORITATIVE** - Human curators make final decisions

### What Evidence Does:
✅ Provides research backing for editorial decisions  
✅ Offers context for AI reasoning  
✅ Supports collection ideation  
✅ Documents historical and theoretical frameworks  

### What Evidence Does NOT Do:
❌ **Assign Prisma colors to films**  
❌ **Rank or tier films**  
❌ **Override doctrine rules**  
❌ **Make editorial decisions**  
❌ **Define new color categories**  

## Content Principles

### All Content is Descriptive, Not Prescriptive
Every entry in this evidence layer describes what sources have documented about color usage in cinema. **No interpretive leaps** beyond what sources explicitly state.

### Examples are Illustrative Only
Film examples cited throughout this evidence are:
- **Non-exclusive** - Many other films could exemplify the same concepts
- **Non-canonical** - Not definitive assignments to Prisma color categories
- **Context-dependent** - Same film may be discussed for different color aspects
- **Source-attributed** - Claims tied to specific academic or industry sources

### Ambiguity is Preserved
Where sources disagree or present conflicting interpretations, that **ambiguity is maintained** rather than resolved. This reflects the genuine complexity of color interpretation in cinema.

### No Prisma Color Assignments
**STRICT RULE**: No film in this evidence layer is assigned to any of Prisma's 12 canonical colors or monochromatic modes. All color descriptions use:
- **Source terminology** (as documented in original research)
- **Generic color terms** (red, blue, warm, cool, etc.)
- **Technical descriptions** (saturated, desaturated, high-contrast, etc.)
- **Contextual qualifiers** (neon-like, earth-toned, pastel, etc.)

## Source Document

### cinema_color_research_corpus_v2.docx
- **Location:** `pipeline/evidence/sources/cinema_color_research_corpus_v2.docx`
- **Title:** "The Chromatic Turn: A Comprehensive Analysis of Color in Global Cinema"
- **Scope:** Comprehensive examination of color in cinema covering:
  - Technical evolution (Technicolor, Eastmancolor, Digital Intermediate)
  - Cinematographer philosophies and approaches
  - Director color authorship patterns
  - Cinematic movements and their color characteristics
  - Global cinema traditions (Hollywood, European, Asian, Latin American)
  - Contemporary digital aesthetics
  - Politics of representation in color usage
- **Sources:** 60+ academic and industry references
- **Coverage:** Hundreds of films across multiple decades and traditions

The structured JSON files in this directory are **extractions** from this source document, normalized for machine readability while preserving the descriptive, non-prescriptive nature of the original research.

## File Structure

### cinematographers.json
Documented color philosophies and approaches from major cinematographers, including their key concepts, recurring ideas, and cited films (illustrative only).

### directors.json
Directors with distinctive color authorship, their approaches to color as narrative tool, thematic patterns, and representative works.

### film_case_studies.json
Detailed analysis of specific films frequently cited for their color strategies, including narrative function, cultural context, and technical approaches.

### movements_and_periods.json
Cinematic movements and historical periods defined by their color characteristics, technological basis, and ideological context.

### color_themes.json
Thematic uses of color across cinema (red as ambivalence, blue as melancholy, etc.), including examples and contradictions.

### technologies.json
Color technologies and their aesthetic effects, from Technicolor to Digital Intermediate, including technical descriptions and cultural impact.

### politics_and_representation.json
Issues of representation, power, and politics in color usage, including skin tone politics, colonial palettes, and corrective cinematography.

### bibliography.json
Consolidated sources with full citations, categorized by type and relevance to color research.

## Usage Guidelines

### For AI Agents
- Use evidence to **contextualize** color reasoning
- **Cite sources** when referencing evidence
- **Never assign** Prisma colors based on evidence alone
- Preserve **ambiguity** where sources disagree
- Remember: Evidence **informs**, doctrine **decides**

### For Human Editors
- Reference evidence for **historical context**
- Use case studies as **discussion points**
- Cite frameworks to **justify decisions**
- Override AI when evidence suggests different interpretation
- Evidence **supports** but never **replaces** editorial judgment

### For Collection Authors
- Draw on case studies for **film examples**
- Reference movements for **historical context**
- Quote cinematographers for **authority**
- Link to technologies for **technical background**
- Remember: Examples are **illustrative**, not **exclusive**

## Limitations

1. **Western-Centric Bias**: Despite global coverage, sources still emphasize Hollywood and European cinema
2. **Temporal Gaps**: Some periods (early cinema, non-Western traditions) less comprehensively covered
3. **Source Dependency**: Quality of evidence depends on quality of original sources
4. **Translation Issues**: Some non-English sources may lose nuance in translation
5. **Technological Evolution**: Rapid changes in digital technology may date some technical descriptions

## Version Notes

**v2.0 represents a significant expansion from v1.0:**
- **Scope**: Hundreds of films vs. dozens in v1.0
- **Global Coverage**: Expanded beyond Hollywood/European focus
- **Movements**: Systematic coverage of cinematic periods
- **Technologies**: Comprehensive technical history
- **Politics**: New focus on representation and power dynamics
- **Sources**: 60+ references vs. 40+ in v1.0

---

**Remember**: Evidence informs. Doctrine governs. Editors decide.