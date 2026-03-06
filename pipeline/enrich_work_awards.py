"""
pipeline/enrich_work_awards.py
────────────────────────────────
Enriches work_awards for all catalog films using Wikidata SPARQL.

Strategy:
  1. Load all works from Supabase (uses imdb_id to find Wikidata QID)
  2. For each work, query Wikidata for P166 (wins) + P1411 (nominations)
  3. Match Wikidata award QIDs → PRISMA award IDs via WIKIDATA_AWARD_MAP
  4. Upsert matched rows into work_awards

Usage:
  python3 pipeline/enrich_work_awards.py           # full catalog
  python3 pipeline/enrich_work_awards.py --test    # first 5 films only
  python3 pipeline/enrich_work_awards.py --force   # re-process even if already has awards
  python3 pipeline/enrich_work_awards.py --work work_parasite_2019  # single film
  python3 pipeline/enrich_work_awards.py --debug   # print unmatched Wikidata QIDs

NOTE: work_awards requires a unique constraint for upsert. Add via Supabase SQL editor:
  ALTER TABLE work_awards ADD CONSTRAINT work_awards_unique
    UNIQUE (work_id, award_id, result);
Until then, the script uses delete+insert (idempotent).
"""

import sys
import time
import argparse
import os
from dotenv import load_dotenv
import requests

load_dotenv(".env.local")
from supabase import create_client

# ─── Config ──────────────────────────────────────────────────────────────────

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "User-Agent": "PRISMA-film-db/1.0 (cinematic color catalog; educational project)",
    "Accept": "application/sparql-results+json",
}
RATE_LIMIT_SLEEP = 1.2  # seconds between Wikidata requests

# ─── Award mapping: Wikidata QID → PRISMA award_id ───────────────────────────
# Canonical new IDs take priority; legacy IDs kept for completeness.
# No duplicate keys — each QID maps to exactly one award_id.

WIKIDATA_AWARD_MAP = {
    # Cannes — both QIDs seen in the wild
    "Q41445":   "award_cannes-palme-dor",  # Palme d'Or (concept item)
    "Q179808":  "award_cannes-palme-dor",  # Palme d'Or (award item — used by most films)
    "Q695106":  "award_cannes-grand-prix",
    "Q844804":  "award_cannes-grand-prix",  # alias QID seen in catalog
    "Q631033":  "award_cannes-jury-prize",
    "Q1136734": "award_cannes-best-director",
    "Q631454":  "award_cannes-camera-dor",
    # Cannes acting — new
    "Q1401748": "award_cannes-best-actress",
    "Q1400853": "award_cannes-best-actor",
    "Q1361014": "award_cannes-special-jury",
    # Berlin
    "Q181699":  "award_berlin-golden-bear",
    "Q703764":  "award_berlin-silver-bear-director",
    "Q632291":  "award_berlin-silver-bear-jury",
    # Berlin acting — new
    "Q702400":  "award_berlin-silver-bear-actress",
    "Q702402":  "award_berlin-silver-bear-actor",
    # Venice
    "Q180942":  "award_venice-golden-lion",
    "Q209459":  "award_venice-golden-lion",   # alias QID seen in catalog
    "Q1135659": "award_venice-silver-lion-director",
    "Q1361066": "award_venice-grand-jury",
    # Venice acting — new
    "Q901330":  "award_venice-volpi-cup-actress",
    "Q901332":  "award_venice-volpi-cup-actor",
    "Q2996614": "award_venice-special-jury",
    # Oscar — Q105304 is the actual QID used by films in Wikidata
    "Q102427":  "award_oscar-best-picture",
    "Q103360":  "award_oscar-best-director",
    "Q205490":  "award_oscar-best-intl-film",  # original QID from spec
    "Q105304":  "award_oscar-best-intl-film",  # actual QID used by Wikidata film items
    "Q229407":  "award_oscar-best-cinematography",
    "Q131520":  "award_oscar-best-cinematography",   # alias QID seen in catalog
    "Q21995136":"award_oscar-best-cinematography",   # alias QID seen in catalog
    "Q103618":  "award_oscar-best-actress",
    "Q103916":  "award_oscar-best-actor",
    "Q106291":  "award_oscar-best-supporting-actor",   # new
    "Q106301":  "award_oscar-best-supporting-actress", # new
    "Q41417":   "award_oscar-best-original-screenplay",  # new — 12x in catalog
    "Q107258":  "award_oscar-best-adapted-screenplay",   # new
    "Q488651":  "award_oscar-best-original-score",       # new
    "Q22752868":"award_oscar-best-original-score",       # alias
    "Q22235329":"award_oscar-best-original-score",       # alias
    "Q277751":  "award_oscar-best-production-design",    # new — 12x in catalog
    "Q281939":  "award_oscar-best-film-editing",         # new — 8x in catalog
    "Q830079":  "award_oscar-best-sound",                # new — 9x in catalog
    # BAFTA
    "Q637514":  "award_bafta-best-film",
    "Q139184":  "award_bafta-best-film",    # alias QID seen in catalog
    "Q677507":  "award_bafta-best-director",
    "Q1576399": "award_bafta-best-cinematography",  # new
    "Q1576340": "award_bafta-best-original-screenplay",  # new
    # Golden Globe — Q1011509 is the QID used by film items
    "Q1011547": "award_gg-best-film-drama",  # original QID from spec
    "Q1011509": "award_gg-best-film-drama",  # actual QID used by Wikidata film items
    "Q1011540": "award_gg-best-director",
    "Q1011560": "award_gg-best-intl-film",
    # César
    "Q695280":  "award_cesar-best-film",
    "Q695299":  "award_cesar-best-director",
    "Q24241":   "award_cesar-best-actress",   # new — 4x in catalog
    "Q695291":  "award_cesar-best-actor",     # new
    # Goya — Q1467554 is the QID used by film items
    "Q1665932": "award_goya-best-film",   # original QID from spec
    "Q1467554": "award_goya-best-film",   # actual QID used by Wikidata film items
    "Q1571511": "award_goya-best-director",
    # Ariel
    "Q1143196": "award_ariel-best-film",
    "Q3041798": "award_ariel-best-director",
    # Locarno
    "Q216366":  "award_locarno-golden-leopard",
    "Q2644546": "award_locarno-special-jury",   # new
    # San Sebastián
    "Q1143177": "award_sansebastian-golden-shell",
    "Q1234936": "award_sansebastian-silver-shell-actress",  # new
    "Q1234946": "award_sansebastian-silver-shell-actor",    # new
    # Toronto
    "Q1047652": "award_toronto-peoples-choice",
    # Sundance
    "Q1377733": "award_sundance-grand-jury-drama",
    "Q1377740": "award_sundance-world-cinema-drama",
    "Q3439490": "award_sundance-directing-drama",   # new
    "Q1377734": "award_sundance-grand-jury-doc",    # new
    # Rotterdam
    "Q1076955": "award_rotterdam-tiger",  # new
    # FIPRESCI
    "Q651176":  "award_fipresci",
    "Q1377697": "award_fipresci-cannes",   # new (festival-specific)
    "Q1377702": "award_fipresci-berlin",   # new
    "Q1377706": "award_fipresci-venice",   # new
}

# ─── Wikidata queries ─────────────────────────────────────────────────────────

def find_wikidata_id_by_imdb(imdb_id: str) -> str | None:
    """Find Wikidata QID via IMDb ID (P345)."""
    sparql = f"""
    SELECT ?item WHERE {{
      ?item wdt:P345 "{imdb_id}" .
    }}
    LIMIT 1
    """
    try:
        resp = requests.get(
            SPARQL_ENDPOINT,
            params={"query": sparql, "format": "json"},
            headers=HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
        if bindings:
            uri = bindings[0]["item"]["value"]
            return uri.split("/")[-1]  # e.g. "Q123456"
        return None
    except Exception as e:
        print(f"    [SPARQL error finding QID for {imdb_id}]: {e}")
        return None


def query_wikidata_awards(wikidata_id: str) -> list[dict]:
    """
    Query Wikidata for all award wins (P166) and nominations (P1411) for a film.
    Returns list of dicts: {award_qid, award_label, year, result, person_qid, person_label}
    """
    sparql = f"""
    SELECT ?award ?awardLabel ?year ?result ?person ?personLabel WHERE {{
      {{
        wd:{wikidata_id} p:P166 ?awardStatement .
        ?awardStatement ps:P166 ?award .
        OPTIONAL {{ ?awardStatement pq:P585 ?date . BIND(YEAR(?date) AS ?year) }}
        OPTIONAL {{ ?awardStatement pq:P1686 ?person }}
        BIND("win" AS ?result)
      }}
      UNION
      {{
        wd:{wikidata_id} p:P1411 ?nomStatement .
        ?nomStatement ps:P1411 ?award .
        OPTIONAL {{ ?nomStatement pq:P585 ?date . BIND(YEAR(?date) AS ?year) }}
        OPTIONAL {{ ?nomStatement pq:P1686 ?person }}
        BIND("nomination" AS ?result)
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }}
    """
    try:
        resp = requests.get(
            SPARQL_ENDPOINT,
            params={"query": sparql, "format": "json"},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        bindings = resp.json().get("results", {}).get("bindings", [])
        results = []
        for b in bindings:
            award_uri = b.get("award", {}).get("value", "")
            award_qid = award_uri.split("/")[-1] if award_uri else None
            person_uri = b.get("person", {}).get("value", "")
            person_qid = person_uri.split("/")[-1] if person_uri else None
            results.append({
                "award_qid": award_qid,
                "award_label": b.get("awardLabel", {}).get("value", ""),
                "year": b.get("year", {}).get("value", None),
                "result": b.get("result", {}).get("value", "win"),
                "person_qid": person_qid,
                "person_label": b.get("personLabel", {}).get("value", ""),
            })
        return results
    except Exception as e:
        print(f"    [SPARQL error querying awards for {wikidata_id}]: {e}")
        return []


# ─── Person QID → person_id lookup ───────────────────────────────────────────

def build_person_qid_map(db) -> dict[str, str]:
    """
    Build a mapping from wikidata_id → person_id using the people table.
    Only includes people that have a wikidata_id set.
    """
    result = db.table("people").select("id, wikidata_id").not_.is_("wikidata_id", "null").execute()
    return {r["wikidata_id"]: r["id"] for r in result.data if r.get("wikidata_id")}


def build_person_name_map(db) -> dict[str, str]:
    """
    Build a mapping from normalized name → person_id for all people.
    Used as fallback when Wikidata QID is not in person_qid_map.
    Loaded in pages of 1000 to bypass Supabase default limit.
    """
    all_people = []
    offset = 0
    while True:
        batch = db.table("people").select("id, name").range(offset, offset + 999).execute()
        all_people.extend(batch.data)
        if len(batch.data) < 1000:
            break
        offset += 1000

    name_map: dict[str, str] = {}
    for p in all_people:
        name_lower = (p.get("name") or "").strip().lower()
        if name_lower:
            # First person wins on name collision (rare)
            if name_lower not in name_map:
                name_map[name_lower] = p["id"]
    return name_map


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Enrich work_awards from Wikidata")
    parser.add_argument("--test",  action="store_true", help="Only process first 5 works")
    parser.add_argument("--force", action="store_true", help="Re-process works that already have awards")
    parser.add_argument("--work",  type=str, help="Process a single work by ID (e.g. work_parasite_2019)")
    parser.add_argument("--debug", action="store_true", help="Print unmatched Wikidata award QIDs")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    # ── Load works ────────────────────────────────────────────────────────────
    print("Loading works from Supabase...")
    works_res = db.table("works").select("id, title, year, wikidata_id, imdb_id").execute()
    works = works_res.data

    if args.work:
        works = [w for w in works if w["id"] == args.work]
        if not works:
            print(f"ERROR: Work '{args.work}' not found.")
            sys.exit(1)
    elif args.test:
        # Pick 5 interesting films across different eras and countries
        test_ids = [
            "work_parasite_2019",
            "work_mulholland-drive_2001",
            "work_all-about-my-mother_1999",
            "work_chungking-express_1994",
            "work_the-godfather_1972",
        ]
        works = [w for w in works if w["id"] in test_ids]
        # Preserve order
        works.sort(key=lambda w: test_ids.index(w["id"]) if w["id"] in test_ids else 999)
        print(f"TEST MODE — processing {len(works)} films\n")

    # ── Skip works already enriched (unless --force) ──────────────────────────
    if not args.force and not args.work:
        existing_res = db.table("work_awards").select("work_id").execute()
        already_done = {r["work_id"] for r in existing_res.data}
        before = len(works)
        works = [w for w in works if w["id"] not in already_done]
        skipped = before - len(works)
        if skipped:
            print(f"Skipping {skipped} works already enriched (use --force to re-process)")

    total = len(works)
    print(f"Processing {total} works...\n")

    # ── Load person maps ────────────────────────────────────────────────────────
    person_qid_map = build_person_qid_map(db)
    print(f"Loaded {len(person_qid_map)} people with Wikidata IDs")
    person_name_map = build_person_name_map(db)
    print(f"Loaded {len(person_name_map)} people for name-based matching\n")

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats = {
        "processed": 0,
        "wikidata_found": 0,
        "wikidata_missing": 0,
        "awards_inserted": 0,
        "awards_skipped_no_match": 0,
        "zero_awards": 0,
        "errors": 0,
    }
    wikidata_cache: dict[str, str | None] = {}  # imdb_id → wikidata_id

    for i, work in enumerate(works, 1):
        work_id = work["id"]
        title = work["title"]
        year = work["year"]
        imdb_id = work.get("imdb_id")
        wikidata_id = work.get("wikidata_id")

        print(f"[{i:3d}/{total}] {title} ({year})", end="")

        # ── Resolve Wikidata QID ───────────────────────────────────────────────
        if not wikidata_id and imdb_id:
            if imdb_id in wikidata_cache:
                wikidata_id = wikidata_cache[imdb_id]
            else:
                wikidata_id = find_wikidata_id_by_imdb(imdb_id)
                wikidata_cache[imdb_id] = wikidata_id
                time.sleep(RATE_LIMIT_SLEEP)

            if wikidata_id:
                # Persist back to DB for next run
                db.table("works").update({"wikidata_id": wikidata_id}).eq("id", work_id).execute()

        if not wikidata_id:
            print(f" → NO Wikidata QID found")
            stats["wikidata_missing"] += 1
            stats["processed"] += 1
            continue

        stats["wikidata_found"] += 1
        print(f" ({wikidata_id})", end="")

        # ── Query Wikidata awards ──────────────────────────────────────────────
        raw_awards = query_wikidata_awards(wikidata_id)
        time.sleep(RATE_LIMIT_SLEEP)

        # ── Match to PRISMA award IDs ─────────────────────────────────────────
        rows_to_insert = []
        seen = set()  # dedupe (award_id, result) pairs
        unmatched_qids: dict[str, str] = {}  # qid → label, for debug

        for award_entry in raw_awards:
            qid = award_entry["award_qid"]
            if not qid or qid not in WIKIDATA_AWARD_MAP:
                if qid and args.debug:
                    unmatched_qids[qid] = award_entry.get("award_label", "")
                stats["awards_skipped_no_match"] += 1
                continue

            award_id = WIKIDATA_AWARD_MAP[qid]
            result_val = award_entry["result"]

            # Dedupe within this work
            dedup_key = (award_id, result_val)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            # Resolve person_id: try Wikidata QID first, then name-based fallback
            person_id = None
            p_qid = award_entry.get("person_qid")
            if p_qid:
                if p_qid in person_qid_map:
                    person_id = person_qid_map[p_qid]
                else:
                    # Fallback: match by normalized name from Wikidata label
                    p_label = (award_entry.get("person_label") or "").strip().lower()
                    if p_label:
                        person_id = person_name_map.get(p_label)

            # Parse year
            award_year = None
            if award_entry.get("year"):
                try:
                    award_year = int(award_entry["year"])
                except (ValueError, TypeError):
                    pass
            if not award_year and year:
                award_year = year

            rows_to_insert.append({
                "work_id": work_id,
                "award_id": award_id,
                "year": award_year,
                "category": award_entry.get("award_label") or None,
                "result": result_val,
                "person_id": person_id,
            })

        if args.debug and unmatched_qids:
            for qid, label in list(unmatched_qids.items())[:8]:
                print(f"\n      [unmatched] {qid}: {label}")

        if not rows_to_insert:
            print(f" → 0 awards matched (Wikidata returned {len(raw_awards)} raw entries)")
            stats["zero_awards"] += 1
        else:
            # Delete existing rows for this work, then insert fresh (idempotent).
            # A unique constraint on (work_id, award_id, result) would allow upsert,
            # but delete+insert works without it.
            try:
                db.table("work_awards").delete().eq("work_id", work_id).execute()
                db.table("work_awards").insert(rows_to_insert).execute()
                matched_count = len(rows_to_insert)
                wins = sum(1 for r in rows_to_insert if r["result"] == "win")
                noms = matched_count - wins
                print(f" → {matched_count} awards ({wins}W/{noms}N)")
                stats["awards_inserted"] += matched_count
            except Exception as e:
                print(f" → INSERT ERROR: {e}")
                stats["errors"] += 1

        stats["processed"] += 1

    # ── Final summary ─────────────────────────────────────────────────────────
    print(f"""
{'='*60}
SUMMARY
{'='*60}
  Works processed:        {stats['processed']:>4}
  Wikidata QID found:     {stats['wikidata_found']:>4}
  Wikidata QID missing:   {stats['wikidata_missing']:>4}
  Awards inserted:        {stats['awards_inserted']:>4}
  Works with 0 matches:   {stats['zero_awards']:>4}
  Unmatched award QIDs:   {stats['awards_skipped_no_match']:>4}  (not in our award map)
  Errors:                 {stats['errors']:>4}
{'='*60}
""")

    # Quick DB check
    total_wa = db.table("work_awards").select("id", count="exact").execute()
    print(f"work_awards table now has: {total_wa.count} rows total")

    works_with_awards = db.table("work_awards").select("work_id").execute()
    unique_works = len({r["work_id"] for r in works_with_awards.data})
    print(f"Works with ≥1 award entry: {unique_works}")


if __name__ == "__main__":
    main()
