# Cultural Memory System - Testing Checklist

## ✅ Implementation Complete

All architectural components have been implemented:

- [x] Phase 2 Cultural Memory module created
- [x] Phase 3 integration updated
- [x] Bug fixes applied (genre key mismatch, pink mapping)
- [x] Test suite created
- [x] Documentation written
- [x] Architecture diagrams created

---

## 🧪 Testing Phase (Next Steps)

### Prerequisites

```bash
# 1. Set API key
export GEMINI_API_KEY='your-gemini-api-key-here'

# 2. Verify Python environment
cd /Users/servinemilio/Documents/REPOS/prisma-site/pipeline
python3 --version  # Should be 3.9+

# 3. Check dependencies (if needed)
pip3 install google-generativeai  # Gemini SDK
```

### Test 1: Integration Test (Single Film)

```bash
# Test The Matrix end-to-end
python3 tests/test_integration_matrix.py
```

**Expected Output:**
```
✅ INTEGRATION TEST PASSED

The Matrix correctly resolves to GREEN via cultural memory!
```

**Pass Criteria:**
- [ ] Cultural memory resolves to `verde_acido` or `verde_esperanza`
- [ ] Consensus strength ≥ 0.75
- [ ] Phase 3 uses cultural memory (not genre fallback)
- [ ] Confidence rank ≥ 0.80

**If Failed:**
- Check GEMINI_API_KEY is set
- Verify API key has quota remaining
- Check internet connection
- Review LLM reasoning output for debugging

---

### Test 2: Canonical Test Suite (7 Films)

```bash
# Test all ground truth films
python3 tests/test_cultural_memory_canonical.py
```

**Expected Output:**
```
Total Tests: 7
Passed: 6-7
Failed: 0-1
Pass Rate: 85-100%

✅ SUITE PASSED - System meets quality threshold
```

**Pass Criteria:**
- [ ] Pass rate ≥ 90% (6-7 out of 7 films)
- [ ] The Matrix → green
- [ ] Barbie → pink
- [ ] Schindler's List → monochrome
- [ ] At least 5 films with strong consensus (≥0.75)

**Ground Truth:**
| Film                | Expected Color       | Must Pass? |
|---------------------|----------------------|------------|
| The Matrix          | verde_acido          | ✅ YES     |
| Barbie              | rosa_melancolico     | ✅ YES     |
| Titanic             | azul_profundo        | ⚠️  Should |
| 12 Monkeys          | ambar_dorado/sepia   | ⚠️  Should |
| Schindler's List    | gris_industrial      | ✅ YES     |
| Midsommar           | blanco_puro/amarillo | ⚠️  Should |
| Inception           | azul_profundo        | ⚠️  Should |

**If Failed:**
- Review which films failed
- Check LLM reasoning for those films
- Adjust color mappings if needed
- Consider lowering threshold if 80-89% pass rate

---

### Test 3: Bug Fix Verification

```bash
# Verify Phase 2E bug fixes
cd /Users/servinemilio/Documents/REPOS/prisma-site/pipeline

# Test genre key extraction
python3 -c "
from phase_2e_cultural_consensus.engine import CulturalConsensusEngine

engine = CulturalConsensusEngine()
result = engine.resolve(
    title='The Matrix',
    year=1999,
    genres=['Science Fiction', 'Action'],
    plot='A computer hacker learns about the true nature of reality.',
    director='The Wachowskis'
)

print(f'Genre signals extracted: {result.genre_signals}')
print(f'Expected: cyberpunk, neon, future, space, etc.')

# Should now include sci-fi signals (was broken before)
assert 'cyberpunk' in result.genre_signals or 'neon' in result.genre_signals
print('✅ Genre key bug FIXED')
"
```

**Pass Criteria:**
- [ ] Genre signals include sci-fi terms (cyberpunk, neon, etc.)
- [ ] No more `"science_fiction" → "science fiction"` transformation

---

### Test 4: Color Mapping Verification

```bash
# Test pink/magenta color mappings
python3 -c "
from phase_2_cultural_memory.resolver import _map_color_to_prisma

# Test pink mapping (was broken: pink → violeta_onirico)
pink = _map_color_to_prisma('pink')
magenta = _map_color_to_prisma('magenta')
hot_pink = _map_color_to_prisma('hot pink')

print(f'pink → {pink}')
print(f'magenta → {magenta}')
print(f'hot pink → {hot_pink}')

assert pink == 'rosa_melancolico', f'Expected rosa_melancolico, got {pink}'
assert magenta == 'rosa_melancolico', f'Expected rosa_melancolico, got {magenta}'
print('✅ Pink/magenta mapping FIXED')
"
```

**Pass Criteria:**
- [ ] `pink` → `rosa_melancolico` (not `violeta_onirico`)
- [ ] `magenta` → `rosa_melancolico` (not `violeta_onirico`)
- [ ] `hot pink` → `rosa_melancolico`

---

## 📊 Validation Metrics

After running tests, record results:

### Test Results

```
Date: _______________
Environment: Local / Production
API Key: (last 4 chars) ____

┌────────────────────────────┬────────┬──────────┐
│ Test                       │ Result │ Notes    │
├────────────────────────────┼────────┼──────────┤
│ Integration Test (Matrix)  │ □ PASS │          │
│                            │ □ FAIL │          │
├────────────────────────────┼────────┼──────────┤
│ Canonical Suite (7 films)  │ □ PASS │ __/7     │
│                            │ □ FAIL │ pass     │
├────────────────────────────┼────────┼──────────┤
│ Bug Fix: Genre Keys        │ □ PASS │          │
│                            │ □ FAIL │          │
├────────────────────────────┼────────┼──────────┤
│ Bug Fix: Pink Mapping      │ □ PASS │          │
│                            │ □ FAIL │          │
└────────────────────────────┴────────┴──────────┘

Overall: □ READY FOR PRODUCTION
         □ NEEDS ADJUSTMENT
         □ MAJOR ISSUES
```

### Consensus Strength Distribution

After canonical tests, analyze consensus strength:

```
High Confidence (≥0.85):  __ films (expected: 3-5)
Good Confidence (0.75-0.84): __ films (expected: 2-3)
Low Confidence (<0.75):   __ films (expected: 0-2)

Average Consensus: ______ (expected: ≥0.80)
```

---

## 🐛 Troubleshooting

### Issue: API Key Error

```
Error: GEMINI_API_KEY not set
```

**Solution:**
```bash
export GEMINI_API_KEY='your-key-here'
# Or add to ~/.zshrc for persistence
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: Low Consensus Strength

```
Consensus strength: 0.45 (below 0.75 threshold)
```

**Solution:**
- Check LLM reasoning - is it generic?
- Verify film has clear cultural memory (not obscure)
- May be acceptable for lesser-known films (fallback to genre)

### Issue: Wrong Color Despite High Consensus

```
Consensus: 0.90, but color is wrong
```

**Solution:**
- Review `reasoning` field - what sources did LLM cite?
- Check color mapping in `resolver.py` - missing synonym?
- Add mapping to `COLOR_MAPPING` dict

### Issue: Import Error

```
ImportError: No module named 'phase_2_cultural_memory'
```

**Solution:**
```bash
# Ensure you're in the correct directory
cd /Users/servinemilio/Documents/REPOS/prisma-site/pipeline

# Verify __init__.py exists
ls -la phase_2_cultural_memory/__init__.py

# Run from pipeline directory
python3 tests/test_integration_matrix.py
```

---

## 🚀 Post-Testing Actions

### If All Tests Pass (≥90%)

- [ ] Update production pipeline to include cultural memory
- [ ] Set up caching for cultural memory results (optional)
- [ ] Monitor consensus strength on production data
- [ ] Document any edge cases discovered
- [ ] Consider deprecating Phase 2E to `_deprecated/`

### If Tests Partially Pass (70-89%)

- [ ] Analyze failed cases - are they obscure films?
- [ ] Adjust color mappings for missing synonyms
- [ ] Consider lowering threshold from 0.75 to 0.70
- [ ] Run additional spot checks on production data

### If Tests Fail (<70%)

- [ ] Review LLM prompts - are they clear enough?
- [ ] Check API key and quota
- [ ] Verify Gemini model version (should be 1.5+)
- [ ] Analyze reasoning outputs for patterns
- [ ] Consider adjusting consensus strength calculation

---

## 📝 Final Checklist

Before marking complete:

- [ ] All tests run successfully
- [ ] The Matrix → green (verified)
- [ ] Barbie → pink (verified)
- [ ] ≥90% canonical pass rate
- [ ] No major errors or crashes
- [ ] Documentation reviewed
- [ ] Team notified of results

---

## 📞 Support

If you encounter issues:

1. Check [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
2. Review [INTEGRATION.md](./phase_2_cultural_memory/INTEGRATION.md)
3. See [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)
4. Check test verbose output: `python3 tests/test_cultural_memory_canonical.py -v`

---

**Ready to test?** Start with:

```bash
export GEMINI_API_KEY='your-key-here'
python3 tests/test_integration_matrix.py
```

Good luck! 🎬🎨
