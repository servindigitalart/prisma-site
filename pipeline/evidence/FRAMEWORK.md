# PRISMA EVIDENCE FRAMEWORK

**Epistemic Architecture for AI-Assisted Color Reasoning**

## I. FOUNDATIONAL PRINCIPLE

**Evidence is substrate, not scaffold.**

Evidence provides cultural and historical material that AI reasoning draws upon, but it does not construct the decision framework. Doctrine provides the framework. Editorial judgment provides the authority. Evidence provides the texture.

This distinction is permanent and non-negotiable.

## II. THE FOUR-LAYER EPISTEMIC MODEL

Prisma's color assignments emerge from four distinct epistemic layers, each with its own authority, mutability, and role:

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: DOCTRINE (Prescriptive, Versioned, Authoritative) │
├─────────────────────────────────────────────────────────────┤
│ • Defines the 12 canonical colors                           │
│ • Establishes assignment philosophy                         │
│ • Sets scoring weights and tier thresholds                  │
│ • Cannot be contradicted by lower layers                    │
│ • Changes only through explicit versioning                  │
└─────────────────────────────────────────────────────────────┘
                              ↓ constrains
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: EDITORIAL (Curatorial, Case-Specific, Final)      │
├─────────────────────────────────────────────────────────────┤
│ • Manual assignments for Canon tier films                   │
│ • Resolution of ambiguous or contested cases                │
│ • Overrides all lower layers                                │
│ • Operates within doctrine, not against it                  │
└─────────────────────────────────────────────────────────────┘
                              ↓ guides
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: AI REASONING (Interpretive, Scalable, Traceable)  │
├─────────────────────────────────────────────────────────────┤
│ • Applies doctrine to specific films                        │
│ • Consults evidence as cultural context                     │
│ • Produces reasoning chains (auditable)                     │
│ • Operates under doctrine constraints                       │
│ • Flags uncertainty for editorial review                    │
└─────────────────────────────────────────────────────────────┘
                              ↓ draws from
┌─────────────────────────────────────────────────────────────┐
│ LAYER 4: EVIDENCE (Descriptive, Plural, Non-Prescriptive)  │
├─────────────────────────────────────────────────────────────┤
│ • Film analyses from critics, scholars, cinematographers    │
│ • Cinematographer statements and philosophies               │
│ • Theoretical frameworks (color theory, semiotics)          │
│ • Historical and cultural context                           │
│ • Preserves ambiguity and contradiction                     │
│ • Never assigns colors, never dictates decisions            │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** Information flows upward (evidence informs AI), but authority flows downward (doctrine constrains AI, editorial overrides AI).

## III. EVIDENCE ACCESS CONTRACT

### What Evidence IS

Evidence is a curated research corpus containing:

**Film-specific analyses**
- Critical essays on cinematography
- Director/DP interviews about color choices
- Scene-by-scene color analysis from scholars
- Production design documentation

**Cinematographer philosophies**
- Stated aesthetic principles
- Career-long color signatures
- Collaborations and influences
- Technical approaches to color

**Theoretical frameworks**
- Color symbolism traditions (cultural, religious, psychological)
- Genre color conventions
- Period-specific aesthetics
- National cinema color practices

**Canonical examples**
- Films widely cited for color identity
- Industry/critical consensus on iconic palettes
- Award-winning cinematography

### What Evidence is NOT

Evidence is not:

❌ A rule system  
❌ A training dataset for ML models  
❌ A color assignment database  
❌ A scoring rubric  
❌ A decision tree  
❌ A substitute for editorial judgment  
❌ A constraint on editorial freedom  

## IV. EVIDENCE USAGE RULES (MANDATORY FOR AI AGENTS)

### Rule 1: Evidence Must Be Cited and Contextualized

**Requirement:** Every evidence reference must include source attribution and acknowledge its descriptive (not prescriptive) nature.

**Example:**
```
✅ Correct:
"Cinematographer Roger Deakins describes his approach to Blade Runner 2049 
as 'justified stylization' (ASC interview, 2017), emphasizing that even 
extreme color choices must serve narrative purpose. This supports the 
azul_nocturno assignment as the blue palette serves the film's themes 
of isolation and artificiality."

❌ Incorrect:
"Evidence shows Blade Runner 2049 is blue."
```

**Principle:** Evidence provides context, not conclusions.

### Rule 2: Multiple Evidence Sources Must Be Synthesized, Not Cherry-Picked

**Requirement:** When multiple sources discuss the same film, AI must acknowledge all perspectives and explain how they inform the reasoning.

**Example:**
```
Multiple sources discuss Amélie's color palette:
- Source A: "Dominated by green and red" (Film Quarterly)
- Source B: "Warm yellows create magical realism" (Sight & Sound)
- Source C: "Blue deliberately removed" (Jeunet interview)

Assessment: The consensus supports verde_esperanza (primary) with 
amarillo_ludico (secondary), while the blue removal technique 
reinforces the warm palette dominance.
```

**Principle:** Synthesis over selection. Acknowledge complexity.

### Rule 3: Evidence Ambiguity Must Be Preserved and Reported

**Requirement:** When evidence sources contradict each other, AI must preserve the ambiguity and flag it as information.

**Example:**
```
Evidence presents three perspectives on Kill Bill's color identity:
1. Yellow as primary (homage to Game of Death)
2. Red as primary (blood, revenge narrative)  
3. Multiple primaries (pop art aesthetic)

Under Prisma doctrine (one primary color required), I assess:
- Yellow is culturally iconic (the jumpsuit is the film's visual signature)
- Red is narratively significant but secondary
- Pop art reading acknowledges secondary colors

Assignment: amarillo_ludico (primary), rojo_pasional (secondary)
Confidence: 0.78 (moderate due to evidence plurality)
Flag: Consider editorial review for Canon tier discussion
```

**Principle:** Ambiguity in evidence is information, not noise. Preserve it.

### Rule 4: Evidence Cannot Override Doctrine

**Requirement:** When evidence uses color terminology outside Prisma's 12-color palette, AI must translate to doctrine vocabulary while acknowledging the source perspective.

**Example:**
```
✅ Correct:
"Scholar X describes The Godfather as 'sepia nostalgia' (Source Y, p.23).
Prisma palette does not include sepia. Examining doctrine:
- ambar_desertico (#C98A2E): warmth, nostalgia, decay
This closely matches the sepia characterization.
Assignment: ambar_desertico"

❌ Incorrect:
"Evidence assigns sepia, but Prisma doesn't have sepia, so I'll skip this film."
```

**Principle:** Evidence operates in its own vocabulary. AI translates to doctrine vocabulary.

### Rule 5: Canonical Examples in Evidence Are Illustrative, Not Definitive

**Requirement:** When evidence lists films as "canonical examples" of colors, treat these as strong reference points, not automatic assignments.

**Example:**
If evidence lists "Blade Runner" as a canonical blue film:

✅ This means:
- Blade Runner is a strong candidate for azul_nocturno
- This supports AI reasoning if other factors align

❌ This does NOT mean:
- Automatic assignment guaranteed
- Editorial cannot reassign
- "Blue films = films like Blade Runner"

AI must still:
- Apply doctrine criteria (cultural memory, DP intent, narrative function)
- Consider the specific film's context
- Calculate cultural weight
- Produce independent reasoning

**Principle:** Canonical examples are reference points, not templates.

### Rule 6: Evidence Silence Is Not Evidence of Absence

**Requirement:** If evidence lacks information about a film, AI must not assume the film is unworthy of assignment.

**Example:**
```
✅ Correct:
"Limited evidence available for [Film X]. Based on available metadata 
(director, DP, genre, year) and doctrine criteria, preliminary assessment 
suggests verde_esmeralda. Confidence: 0.45 (low due to limited evidence). 
Recommend: Research additional sources or editorial review."

❌ Incorrect:
"No evidence for [Film X], therefore no assignment possible."
```

**Principle:** Evidence gaps indicate research opportunities, not film inadequacy.

## V. AI REASONING CHAIN REQUIREMENTS

Every AI color assignment must produce a structured reasoning chain containing:

### 1. Evidence Consultation
- **Sources referenced:** List all evidence sources consulted
- **Perspectives synthesized:** Acknowledge multiple viewpoints
- **Gaps identified:** Note missing information

### 2. Doctrine Application
- **Color definitions:** Reference specific Prisma color characteristics
- **Assignment philosophy:** Apply cultural memory over pixel dominance
- **Tier consideration:** Assess against tier thresholds

### 3. Cultural Weight Assessment
- **Cinematographer significance:** DP awards, recognition, influence
- **Critical consensus:** Festival selections, critical canon membership
- **Cultural penetration:** Audience awareness, cultural impact

### 4. Confidence and Uncertainty
- **Confidence score:** 0.0-1.0 with justification
- **Uncertainty factors:** Ambiguous evidence, limited sources, contested interpretations
- **Editorial flags:** Cases requiring human review

### 5. Alternative Considerations
- **Secondary colors:** Supporting palette elements
- **Rejected options:** Other colors considered and why rejected
- **Edge cases:** Monochromatic, color-shift, or ambiguous films

## VI. FAILURE MODES AND PROHIBITIONS

### Prohibited AI Behaviors

❌ **Evidence Laundering:** Using evidence to justify predetermined assignments  
❌ **Cherry-Picking:** Selecting only supportive sources while ignoring contradictions  
❌ **False Certainty:** Claiming high confidence when evidence is ambiguous  
❌ **Doctrine Violation:** Assigning colors not in the canonical 12-color palette  
❌ **Editorial Override:** Contradicting existing editorial assignments  
❌ **Evidence Invention:** Creating or inferring evidence not present in sources  

### Required Failure Responses

When AI encounters:

**Insufficient Evidence**
→ Lower confidence, flag for additional research

**Contradictory Evidence** 
→ Synthesize perspectives, acknowledge ambiguity, flag for editorial review

**Doctrine Conflicts**
→ Prioritize doctrine, explain translation from evidence terminology

**Technical Limitations**
→ Acknowledge constraints, recommend human review

**Uncertain Cases**
→ Provide reasoning but flag as requiring editorial judgment

## VII. EVIDENCE LAYER VERSIONING AND UPDATES

### Evidence Evolution
- Evidence layers can be updated independently of doctrine
- New evidence does not automatically change existing assignments
- Evidence updates trigger re-evaluation, not automatic reassignment

### Version Compatibility
- AI agents must specify which evidence version they consulted
- Reasoning chains must be reproducible with cited evidence version
- Editorial decisions override AI reasoning regardless of evidence version

### Quality Assurance
- All evidence must be source-attributed
- Academic and industry sources preferred over secondary sources
- Cultural and historical context must be preserved
- Ambiguity and contradiction must be maintained, not resolved

## VIII. EDITORIAL RELATIONSHIP

### Editorial Authority
- Editorial assignments override all AI reasoning
- Evidence cannot be used to challenge editorial decisions
- AI must acknowledge editorial assignments as final

### Editorial Support
- Evidence provides context for editorial decision-making
- AI reasoning chains assist editorial review
- Evidence gaps can guide editorial research priorities

### Collaborative Framework
- AI provides scalable reasoning within doctrine constraints
- Editorial provides curatorial expertise and final authority
- Evidence provides shared foundation for both AI and editorial work

---

**This framework is canonical and mandatory for all AI agents operating within Prisma's color assignment system. Compliance is required, not optional.**