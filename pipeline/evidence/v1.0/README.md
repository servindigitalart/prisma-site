# Prisma Evidence Layer v1.0

## Primary Research Sources

The evidence layer v1.0 is derived from the following primary source document:

### cinema_color_research_v1.docx
- **Location:** `pipeline/evidence/sources/cinema_color_research_v1.docx`
- **Origin:** External cinema color research (Gemini Deep Research–assisted)
- **Date:** 2026-02-02
- **Scope:** Historical, theoretical, and editorial discussion of color in cinema, covering:
  - Cinematographer philosophies and documented approaches
  - Film case studies and color analysis
  - Theoretical frameworks from cinema theory and cognitive science
  - Technical history of color processes (Technicolor, film stocks, etc.)
  - Critical discourse on color in contemporary and historical cinema
- **Role:** Primary evidence artifact supporting Prisma doctrine and editorial decisions
- **Important:** This document is **descriptive, not prescriptive**. It does not define rules, assign colors to films, or create rankings. It provides research context and reference material for editorial judgment.

The structured JSON files in this directory (`cinematographers.json`, `film_color_case_studies.json`, `theoretical_frameworks.json`, `bibliography.json`) are extractions from this source document, normalized for machine readability.

---

## What This Is

The **Evidence Layer** is a structured repository of cinema color research extracted from authoritative sources. It provides:

- **Cinematographer philosophies** and documented approaches to color
- **Film case studies** discussing color in specific works
- **Theoretical frameworks** from cinema theory and cognitive science
- **Bibliography** of sources that inform our understanding of color in film

This is **descriptive research**, not prescriptive rules.

## What This Is NOT

❌ **Not Doctrine** - This does not define Prisma's rules, thresholds, or decision logic  
❌ **Not Assignments** - Film examples are illustrative references, not color assignments  
❌ **Not Rankings** - No film is scored, tiered, or canonized here  
❌ **Not Prescriptive** - Does not tell editors or AI what decisions to make  
❌ **Not Final Truth** - Sources may disagree; ambiguity is preserved

## Relationship to Prisma's Architecture

Prisma has a **layered editorial architecture**:

### 1. Doctrine (Normative, Versioned)
**Location:** `pipeline/doctrine/`

- Defines rules, principles, thresholds, and decision logic
- **Versioned and immutable** - changes require new version
- **Final authority** on how Prisma operates
- **You cannot modify** doctrine based on evidence

### 2. Evidence (Descriptive, Non-normative) ← **YOU ARE HERE**
**Location:** `pipeline/evidence/`

- Supports, contextualizes, and justifies doctrine
- Provides research backing for editorial decisions
- **Never overrides** doctrine
- **Informs but does not decide**

### 3. Editorial Decisions (Human-Only)
**Location:** `pipeline/editorial/`

- Human curators make final color assignments
- Editorial overrides always win
- **Not your responsibility** as an AI agent

## Evidence Usage Framework

**MANDATORY:** All AI agents operating within Prisma's color assignment system must comply with the formal Evidence Usage Framework documented in:

**📋 `pipeline/evidence/FRAMEWORK.md`**

This framework defines:
- The four-layer epistemic model (Doctrine → Editorial → AI Reasoning → Evidence)
- Mandatory evidence usage rules for AI agents
- Required reasoning chain structure
- Prohibited behaviors and failure modes
- Editorial relationship protocols

**Compliance with this framework is required, not optional.**

## How to Use This Evidence

### For AI Color Agents

**MUST** follow `pipeline/evidence/FRAMEWORK.md` requirements.

When generating color reasoning for a film:

1. **Consult cinematographer philosophies** if known DP is in evidence
2. **Reference similar case studies** for context and precedent
3. **Apply relevant theoretical frameworks** to support reasoning
4. **Cite sources** from bibliography when making claims
5. **Remember**: Your output is a **recommendation**, not a decision

### For Human Editors

When reviewing color assignments:

1. **Use case studies** as reference points for discussion
2. **Leverage cinematographer philosophies** to understand intent
3. **Consider theoretical frameworks** as lenses for interpretation
4. **Cite evidence** in editorial notes to explain decisions
5. **Override AI** when evidence suggests different interpretation

### For Collections Authors

When writing editorial essays:

1. **Draw on case studies** for film examples
2. **Quote cinematographer philosophies** for authority
3. **Reference frameworks** to contextualize color choices
4. **Link to bibliography** for further reading
5. **Remember**: Examples are illustrative, not exclusive

## Structure

### cinematographers.json
- Documented color philosophies from practitioners
- Signature techniques and approaches
- Referenced films (illustrative only)
- Source citations

**Key Principle**: This describes what cinematographers **have said** about their work, not what their work "means."

### film_color_case_studies.json
- Color discussions from credible sources
- Themes and approaches identified by critics
- Key insights from analysis
- Source citations

**Key Principle**: This is **descriptive** (how film has been discussed), not **classificatory** (what color it "is").

### theoretical_frameworks.json
- Named frameworks and recurring ideas
- Key concepts and application contexts
- Originator and sources
- Conceptual tools, not rules

**Key Principle**: These are **lenses for interpretation**, not formulas for decision.

### bibliography.json
- Consolidated source metadata
- Categorized by type (primary philosophy, critical theory, etc.)
- Intellectual landscape of color discourse

**Key Principle**: These are **authoritative references**, not gospel.

## Strict Rules for Using Evidence

### ✅ DO:
- Quote or paraphrase faithfully
- Preserve ambiguity where sources disagree
- Include source metadata in reasoning
- Use evidence to **support** editorial judgment
- Prefer omission over speculation
- Cite sources when making claims

### ❌ DO NOT:
- Assign Prisma colors based on evidence
- Treat film examples as canonical assignments
- Override doctrine with evidence
- Make interpretive leaps not stated in sources
- Assume single source is definitive
- Invent information not in evidence

## Versioning

This is **v1.0** of the evidence layer, created 2026-02-02.

**Evidence versions are independent of doctrine versions.** Evidence can be updated with new research without changing how Prisma operates (doctrine). Conversely, doctrine can evolve based on editorial philosophy without requiring new evidence.

### When to Create New Evidence Version

- Significant new research added (new sources, frameworks)
- Major corrections to existing evidence (factual errors)
- Restructuring of evidence schema

### When NOT to Create New Version

- Minor additions to existing case studies
- New bibliography entries for same frameworks
- Clarifications that don't change content

## Limitations and Caveats

1. **Incomplete by Design**: This evidence layer represents a snapshot of available research. It is not comprehensive.

2. **Source Quality Varies**: Primary sources (cinematographer interviews) are more authoritative than secondary critical analysis. Weight accordingly.

3. **Cultural Bias**: Much of this research centers Western cinema and Hollywood practice. Non-Western color traditions are underrepresented.

4. **Temporal Context**: Color perception and cultural meaning evolve. Historical context matters.

5. **Ambiguity is Honest**: Where sources disagree or are unclear, that ambiguity is preserved rather than resolved.

## Future Directions

Potential expansions to evidence layer (not current scope):

- **Color in non-Western cinema** (Bollywood, Hong Kong, Nollywood traditions)
- **Production designer philosophies** (set and costume color)
- **Colorist perspectives** (DI grading philosophy)
- **Audience perception studies** (empirical data on color reception)
- **Historical color systems** (two-strip Technicolor, Kinemacolor, etc.)

## Questions?

This evidence layer was created as a **research support system**, not a decision engine. 

If you're unsure whether to use evidence or defer to doctrine:
- **Always defer to doctrine for rules**
- Use evidence for **context and justification**

If you're unsure whether evidence permits something:
- **Always prefer omission over speculation**
- Flag ambiguity rather than inventing resolution

---

**Remember**: Evidence informs. Editors decide. Doctrine governs.
