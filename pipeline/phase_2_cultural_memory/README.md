# Phase 2: Cultural Memory Resolution

## Purpose

Identify a film's **iconic color as remembered by collective cultural memory**, not through academic analysis or genre inference.

The system asks: **"What color do people think of when they hear this film's title?"**

## Philosophy

Films live in cultural consciousness through:
- 🎨 **Marketing materials**: Posters, trailers, promotional imagery
- 💬 **Popular discourse**: Letterboxd reviews, social media, cultural commentary
- 🎬 **Cultural impact**: Memes, references, collective perception
- 🏆 **Awards/Recognition**: How the film is remembered and discussed

Films do NOT necessarily live through:
- ❌ Cinematographer's technical intentions
- ❌ Academic color theory analysis
- ❌ Shot-by-shot palette statistics
- ❌ Genre convention expectations

## Authority Hierarchy

When determining a film's visual identity, cultural memory is the **second-highest authority**:

1. **Hard Evidence** (strongest)
   - Letterboxd canonical data
   - Title-embedded colors ("Three Colors: Blue")
   - Director signature styles with citations

2. **Cultural Memory** (this module)
   - Consensus strength ≥ 0.75
   - Must have substantive reasoning
   - Used when evidence is clear and strong

3. **Genre Conventions** (weakest fallback)
   - Only when no cultural memory exists
   - Generic defaults based on film type

## Usage

### Basic Resolution

```python
from pipeline.phase_2_cultural_memory import resolve_cultural_memory, should_use_consensus

result = resolve_cultural_memory(
    tmdb_id=603,
    title="The Matrix",
    year=1999,
    genres=["Science Fiction", "Action"],
    api_key="your-gemini-api-key"
)

if should_use_consensus(result):
    print(f"Iconic color: {result.iconic_color}")
    print(f"Confidence: {result.color_consensus_strength}")
    print(f"Reasoning: {result.reasoning}")
else:
    print("No strong cultural consensus, fallback to genre")
```

### Expected Outputs (Ground Truth)

| Film | Expected Color | Reasoning |
|------|----------------|-----------|
| **The Matrix** | `verde_acido` or `verde_esperanza` | Green "digital rain" code is the film's most iconic visual |
| **Barbie** | `rosa_melancolico` | Hot pink branding, marketing saturation, "Barbiecore" |
| **Three Colors: Blue** | `azul_profundo` | Title explicitly references blue, visual motif |
| **Almodóvar films** | `rojo_pasion` | Director's signature bold red aesthetic |
| **Little Miss Sunshine** | `ambar_dorado` | Yellow VW van is cultural icon of the film |
| **Roma** | `gris_industrial` | Black-and-white cinematography, memory as theme |
| **The Lighthouse** | `gris_industrial` | High-contrast monochrome, gothic atmosphere |

### Integration with Phase 3

```python
from pipeline.phase_2_cultural_memory import resolve_cultural_memory, should_use_consensus
from pipeline.phase_3_visual_resolution import resolve_visual_identity

# Get cultural memory
cultural_memory = resolve_cultural_memory(
    tmdb_id=film.tmdb_id,
    title=film.title,
    year=film.year,
    genres=film.genres,
    api_key=gemini_key
)

# Resolve final identity with cultural context
identity = resolve_visual_identity(
    phase_1_result=phase_1,
    phase_2d_result=phase_2d,
    cultural_memory=cultural_memory,  # New parameter
    film_title=film.title
)
```

## Schema

### CulturalMemoryResult

```python
@dataclass
class CulturalMemoryResult:
    # Core resolution
    iconic_color: str  # Prisma palette key (e.g., "verde_acido")
    secondary_colors: List[str]  # Additional colors in memory
    color_consensus_strength: float  # 0.0-1.0 confidence score
    
    # Supporting context
    visual_rhythm: VisualRhythm  # CONTEMPLATIVE, DYNAMIC, SUSPENDED, KINETIC
    color_temperature: ColorTemperature  # COOL, WARM, NEUTRAL
    abstraction_level: AbstractionLevel  # LITERAL, SYMBOLIC, VISCERAL
    
    # Metadata
    reasoning: str  # LLM explanation of cultural memory
    sources_cited: List[str]  # Evidence sources (posters, marketing, etc.)
    resolved_at: str  # ISO timestamp
```

## Consensus Strength Calculation

Strength is determined by multiple factors:

```python
def _calculate_consensus_strength(perception: dict) -> float:
    """
    Returns 0.0-1.0 based on:
    - Clarity of color identification
    - Number of sources cited
    - Consistency across perception dimensions
    - Explicitness of cultural memory
    """
    strength = 0.5  # Base
    
    # Clear color identification (+0.3)
    if "iconic_color" is specific and named
    
    # Multiple sources (+0.2)
    if sources_cited >= 3
    
    # Consistent secondary colors (+0.1)
    if secondary colors align with iconic
    
    # Title/marketing mentions (+0.2)
    if reasoning mentions posters/marketing
    
    # Cultural impact evidence (+0.2)
    if reasoning mentions memes/discourse
    
    return min(strength, 1.0)
```

## Threshold Logic

```python
def should_use_consensus(result: CulturalMemoryResult) -> bool:
    """
    Use cultural memory if:
    - Consensus strength ≥ 0.75 (strong confidence)
    - Has substantive reasoning (not generic)
    - Has at least 2 sources cited
    """
    if result.color_consensus_strength < 0.75:
        return False
    if len(result.reasoning) < 50:  # Too generic
        return False
    if len(result.sources_cited) < 2:  # Weak evidence
        return False
    return True
```

## Color Mapping to Prisma Palette

The module maps natural language colors to Prisma's emotional palette:

```python
COLOR_MAPPING = {
    # Greens
    "green": "verde_esperanza",
    "neon green": "verde_acido",
    "acid green": "verde_acido",
    "bright green": "verde_acido",
    
    # Pinks/Reds
    "pink": "rosa_melancolico",
    "hot pink": "rosa_melancolico",
    "magenta": "rosa_melancolico",
    "red": "rojo_pasion",
    
    # Blues
    "blue": "azul_profundo",
    "cyan": "azul_frio",
    "teal": "azul_frio",
    
    # Monochrome
    "black and white": "gris_industrial",
    "monochrome": "gris_industrial",
    "grayscale": "gris_industrial",
    
    # Warm tones
    "yellow": "ambar_dorado",
    "amber": "ambar_dorado",
    "orange": "ambar_dorado",
    "sepia": "sepia_vintage",
}
```

## Testing

Run canonical tests to validate the system:

```bash
# Test against ground truth films
python -m pytest tests/test_cultural_memory_canonical.py -v

# See detailed LLM reasoning
python -m pytest tests/test_cultural_memory_canonical.py -v -s
```

Expected pass rate: **≥90% on obvious cases** (Barbie, The Matrix, Three Colors: Blue)

## Troubleshooting

### Issue: Consensus strength too low (<0.75)

**Cause**: LLM response lacks specificity or sources
**Fix**: Check `reasoning` field - should mention posters, marketing, or cultural impact

### Issue: Wrong color mapped

**Cause**: Color mapping incomplete or LLM used unexpected term
**Fix**: Add mapping to `COLOR_MAPPING` in `resolver.py`

### Issue: Generic responses

**Cause**: LLM reverting to academic analysis
**Fix**: System prompt emphasizes popular perception, but may need API key with proper context window

## Future Enhancements

- [ ] Cache results per TMDB ID to avoid redundant API calls
- [ ] Multi-language support for international film perception
- [ ] Temporal analysis (how memory changes over time)
- [ ] A/B test different LLM prompt strategies
- [ ] Integration with Letterboxd API for direct poster color extraction

## See Also

- [Phase 3 Visual Resolution](../phase_3_visual_resolution/README.md)
- [Genre Conventions (Fallback)](../phase_2e_cultural_consensus/README.md)
- [Prisma Palette Definitions](../core/palette.py)
