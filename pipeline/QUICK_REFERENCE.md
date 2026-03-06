# Quick Reference Card - Cultural Memory System

## 🚀 Quick Start (3 Commands)

```bash
# 1. Set API key
export GEMINI_API_KEY='your-gemini-api-key'

# 2. Test The Matrix (single film)
cd /Users/servinemilio/Documents/REPOS/prisma-site/pipeline
python3 tests/test_integration_matrix.py

# 3. Test all canonical films
python3 tests/test_cultural_memory_canonical.py
```

---

## 📖 What Changed

### Before → After

| Aspect | Before | After |
|--------|--------|-------|
| **The Matrix color** | `rojo_pasion` (red) ❌ | `verde_acido` (green) ✅ |
| **Barbie color** | `violeta_onirico` (purple) ❌ | `rosa_melancolico` (pink) ✅ |
| **Authority** | Genre > Memory | Memory > Genre |
| **Question** | "What color is it?" | "What do people think?" |

---

## 🎯 Core Innovation

```python
# OLD APPROACH (Academic)
"Analyze the cinematographer's color palette choices"
→ Wrong authority, asks wrong question

# NEW APPROACH (Perception)
"What color do people associate with this film?"
→ Correct authority, models cultural memory
```

---

## 🏗️ Integration Example

```python
from pipeline.phase_2_cultural_memory import resolve_cultural_memory
from pipeline.phase_3_visual_resolution import resolve_visual_identity

# Step 1: Resolve cultural memory
cultural_memory = resolve_cultural_memory(
    tmdb_id=603,
    title="The Matrix",
    year=1999,
    genres=["Science Fiction", "Action"],
    api_key=os.getenv('GEMINI_API_KEY')
)

# Step 2: Use in Phase 3 (updated signature)
identity = resolve_visual_identity(
    work_id="tmdb_603",
    color_assignment={},
    cultural_weight={},
    cultural_memory=cultural_memory,  # ← NEW parameter
    film_title="The Matrix"
)

print(f"Color: {identity.color_iconico}")  # verde_acido ✅
```

---

## 📊 Authority Hierarchy

```
1. Hard Evidence      (0.95)  ← Letterboxd, title colors
2. Cultural Memory    (0.85)  ← NEW! What people think
3. Genre Conventions  (0.50)  ← Fallback only
```

**Rule**: Use cultural memory if consensus strength ≥ 0.75

---

## 🧪 Test Expectations

### Integration Test (Matrix)
```
✅ Color: verde_acido (green)
✅ Consensus: ≥ 0.75
✅ Confidence: ≥ 0.80
```

### Canonical Suite (7 films)
```
✅ Pass rate: ≥ 90% (6-7 films)
✅ Matrix → green
✅ Barbie → pink
✅ Schindler's List → monochrome
```

---

## 🐛 Bug Fixes Applied

1. **Genre Key Mismatch** (Phase 2E)
   - Before: `"science_fiction"` → `"science fiction"` → lookup fails
   - After: `"science_fiction"` → genre signals extracted ✅

2. **Pink Mapping** (Phase 2E)
   - Before: `"pink"` → `"violeta_onirico"` (purple)
   - After: `"pink"` → `"rosa_melancolico"` (pink) ✅

---

## 📁 New Files

```
pipeline/
├── phase_2_cultural_memory/      ← NEW MODULE
│   ├── __init__.py
│   ├── schema.py
│   ├── gemini_prompter.py
│   ├── resolver.py
│   ├── README.md
│   └── INTEGRATION.md
├── tests/
│   ├── test_cultural_memory_canonical.py  ← NEW
│   └── test_integration_matrix.py         ← NEW
├── IMPLEMENTATION_SUMMARY.md      ← NEW
├── ARCHITECTURE_DIAGRAM.md        ← NEW
└── TESTING_CHECKLIST.md           ← NEW
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| API key error | `export GEMINI_API_KEY='...'` |
| Import error | Run from `/pipeline` directory |
| Wrong color | Check LLM reasoning, adjust mappings |
| Low consensus | Expected for obscure films, fallback OK |

---

## 📞 Documentation

| Document | Purpose |
|----------|---------|
| `IMPLEMENTATION_SUMMARY.md` | What changed and why |
| `ARCHITECTURE_DIAGRAM.md` | Visual system overview |
| `TESTING_CHECKLIST.md` | Step-by-step testing |
| `phase_2_cultural_memory/README.md` | Module documentation |
| `phase_2_cultural_memory/INTEGRATION.md` | Integration guide |

---

## ✅ Success Criteria

- [ ] Integration test passes (Matrix → green)
- [ ] Canonical suite ≥90% pass rate
- [ ] No syntax errors
- [ ] Barbie → pink verified
- [ ] System ready for production

---

## 💰 Costs

- **Per film**: ~$0.002 (Gemini API)
- **1000 films**: ~$2.00
- **Full catalog (10K)**: ~$20.00

---

## 🎬 Ready to Test?

```bash
export GEMINI_API_KEY='your-key-here'
cd /Users/servinemilio/Documents/REPOS/prisma-site/pipeline
python3 tests/test_integration_matrix.py
```

**Expected**: The Matrix resolves to GREEN with 85% confidence ✅
