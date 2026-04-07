import argparse
import os
import time
from collections import defaultdict

import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(".env.local")

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
SPARQL_HEADERS = {
    "User-Agent": "PRISMA-film-database/1.0 (https://prisma.film; enrichment bot)",
    "Accept": "application/sparql-results+json",
}

RATE_LIMIT_SLEEP = 1.2

AWARD_QUERY_MAP = {
    # ── Oscar (verified QIDs, IDs match awards table) ────────────────────────
    "oscar-best-picture":               {"qid": "Q102427",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Picture"},
    "oscar-best-director":              {"qid": "Q103360",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Director"},
    "oscar-best-actress":               {"qid": "Q103618",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Actress"},
    "oscar-best-actor":                 {"qid": "Q103916",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Actor"},
    "oscar-best-intl-film":             {"qid": "Q105304",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best International Feature Film"},
    "oscar-best-original-screenplay":   {"qid": "Q41417",    "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Original Screenplay"},
    "oscar-best-adapted-screenplay":    {"qid": "Q107258",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Adapted Screenplay"},
    "oscar-best-cinematography":        {"qid": "Q131520",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Cinematography"},
    "oscar-best-supporting-actor":      {"qid": "Q106291",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Supporting Actor"},
    "oscar-best-supporting-actress":    {"qid": "Q106301",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Supporting Actress"},
    "oscar-best-original-score":        {"qid": "Q488651",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Original Score"},
    "oscar-best-film-editing":          {"qid": "Q281939",   "festival": "oscar",        "tier": "A", "label": "Academy Award for Best Film Editing"},
    # ── Cannes (verified QIDs) ───────────────────────────────────────────────
    "cannes-palme-dor":                 {"qid": "Q179808",   "festival": "cannes",       "tier": "A", "label": "Palme d'Or"},
    "cannes-grand-prix":                {"qid": "Q695106",   "festival": "cannes",       "tier": "A", "label": "Cannes Grand Prix"},
    "cannes-jury-prize":                {"qid": "Q164200",   "festival": "cannes",       "tier": "B", "label": "Cannes Jury Prize"},
    "cannes-best-director":             {"qid": "Q1136734",  "festival": "cannes",       "tier": "B", "label": "Cannes Best Director Prize"},
    "cannes-best-actress":              {"qid": "Q1401748",  "festival": "cannes",       "tier": "B", "label": "Cannes Best Actress Prize"},
    "cannes-best-actor":                {"qid": "Q1400853",  "festival": "cannes",       "tier": "B", "label": "Cannes Best Actor Prize"},
    "cannes-camera-dor":                {"qid": "Q775091",   "festival": "cannes",       "tier": "B", "label": "Caméra d'Or"},
    "cannes-special-jury":              {"qid": "Q1361014",  "festival": "cannes",       "tier": "B", "label": "Cannes Special Jury Prize"},
    # ── Berlin (verified QIDs) ───────────────────────────────────────────────
    "berlin-golden-bear":               {"qid": "Q154590",   "festival": "berlin",       "tier": "A", "label": "Golden Bear"},
    "berlin-silver-bear-director":      {"qid": "Q706031",   "festival": "berlin",       "tier": "B", "label": "Silver Bear for Best Director"},
    "berlin-silver-bear-actress":       {"qid": "Q376834",   "festival": "berlin",       "tier": "B", "label": "Silver Bear for Best Actress"},
    "berlin-silver-bear-actor":         {"qid": "Q819973",   "festival": "berlin",       "tier": "B", "label": "Silver Bear for Best Actor"},
    "berlin-silver-bear-jury":          {"qid": "Q632291",   "festival": "berlin",       "tier": "B", "label": "Silver Bear — Jury Grand Prix"},
    # ── Venice (verified QIDs) ───────────────────────────────────────────────
    "venice-golden-lion":               {"qid": "Q209459",   "festival": "venice",       "tier": "A", "label": "Golden Lion"},
    "venice-special-jury":              {"qid": "Q2996614",  "festival": "venice",       "tier": "B", "label": "Venice Special Jury Prize"},
    "venice-volpi-cup-actress":         {"qid": "Q2089918",  "festival": "venice",       "tier": "B", "label": "Volpi Cup for Best Actress"},
    "venice-volpi-cup-actor":           {"qid": "Q2089923",  "festival": "venice",       "tier": "B", "label": "Volpi Cup for Best Actor"},
    # ── BAFTA (verified QIDs) ────────────────────────────────────────────────
    "bafta-best-film":                  {"qid": "Q139184",   "festival": "bafta",        "tier": "A", "label": "BAFTA Award for Best Film"},
    "bafta-best-director":              {"qid": "Q787131",   "festival": "bafta",        "tier": "A", "label": "BAFTA Award for Best Direction"},
    "bafta-best-cinematography":        {"qid": "Q1576399",  "festival": "bafta",        "tier": "B", "label": "BAFTA Award for Best Cinematography"},
    "bafta-best-original-screenplay":   {"qid": "Q41375",    "festival": "bafta",        "tier": "B", "label": "BAFTA Award for Best Original Screenplay"},
    # ── Golden Globe (verified QIDs, IDs match awards table gg- prefix) ──────
    "gg-best-film-drama":               {"qid": "Q1011509",  "festival": "golden-globe", "tier": "A", "label": "Golden Globe for Best Motion Picture – Drama"},
    "gg-best-director":                 {"qid": "Q586356",   "festival": "golden-globe", "tier": "A", "label": "Golden Globe for Best Director"},
    "gg-best-intl-film":                {"qid": "Q387380",   "festival": "golden-globe", "tier": "B", "label": "Golden Globe for Best Non-English Language Film"},
    # ── César (verified QIDs) ────────────────────────────────────────────────
    "cesar-best-film":                  {"qid": "Q645595",   "festival": "cesar",        "tier": "B", "label": "César Award for Best Film"},
    "cesar-best-director":              {"qid": "Q24137",    "festival": "cesar",        "tier": "B", "label": "César Award for Best Director"},
    "cesar-best-actress":               {"qid": "Q24241",    "festival": "cesar",        "tier": "B", "label": "César Award for Best Actress"},
    "cesar-best-actor":                 {"qid": "Q900494",   "festival": "cesar",        "tier": "B", "label": "César Award for Best Actor"},
    # ── Goya (verified QIDs) ─────────────────────────────────────────────────
    "goya-best-film":                   {"qid": "Q1467554",  "festival": "goya",         "tier": "C", "label": "Goya Award for Best Film"},
    "goya-best-director":               {"qid": "Q1540553",  "festival": "goya",         "tier": "C", "label": "Goya Award for Best Director"},
    # ── Ariel (verified QIDs) ────────────────────────────────────────────────
    "ariel-best-film":                  {"qid": "Q2108656",  "festival": "ariel",        "tier": "C", "label": "Ariel Award for Best Picture"},
    "ariel-best-director":              {"qid": "Q2887050",  "festival": "ariel",        "tier": "C", "label": "Ariel Award for Best Director"},
    # ── San Sebastián (verified QIDs, IDs match awards table sansebastian-) ──
    "sansebastian-golden-shell":        {"qid": "Q775086",   "festival": "san-sebastian","tier": "B", "label": "San Sebastián Golden Shell"},
    "sansebastian-silver-shell-actress":{"qid": "Q610152",   "festival": "san-sebastian","tier": "C", "label": "San Sebastián Silver Shell for Best Actress"},
    "sansebastian-silver-shell-actor":  {"qid": "Q610136",   "festival": "san-sebastian","tier": "C", "label": "San Sebastián Silver Shell for Best Actor"},
    # ── Locarno (verified QIDs) ──────────────────────────────────────────────
    "locarno-golden-leopard":           {"qid": "Q1700510",  "festival": "locarno",      "tier": "B", "label": "Locarno Golden Leopard"},
    # ── Sundance (verified QIDs) ─────────────────────────────────────────────
    "sundance-grand-jury-drama":        {"qid": "Q1377733",  "festival": "sundance",     "tier": "B", "label": "Sundance Grand Jury Prize — Dramatic"},
    "sundance-grand-jury-doc":          {"qid": "Q1377734",  "festival": "sundance",     "tier": "B", "label": "Sundance Grand Jury Prize — Documentary"},
    "sundance-directing-drama":         {"qid": "Q3439490",  "festival": "sundance",     "tier": "C", "label": "Sundance Directing Award — Dramatic"},
    # ── Toronto (verified QIDs) ──────────────────────────────────────────────
    "toronto-peoples-choice":           {"qid": "Q39087364", "festival": "toronto",      "tier": "B", "label": "Toronto People's Choice Award"},
    # ── Mar del Plata (verified QIDs) ────────────────────────────────────────
    "mar-del-plata-golden-astor":       {"qid": "Q908557",   "festival": "mar-del-plata","tier": "C", "label": "Mar del Plata Golden Astor"},
    # ── FICG — Festival Internacional de Cine de Guadalajara ─────────────────
    "ficg-mayahuel-best-ibero":         {"qid": "Q16572427", "festival": "ficg",         "tier": "C", "label": "FICG Mayahuel Award — Best Ibero-American Film"},
    # ── FICM — Festival Internacional de Cine de Morelia ─────────────────────
    "ficm-best-mexican-film":           {"qid": "Q5962681",  "festival": "ficm",         "tier": "C", "label": "FICM Award for Best Mexican Film"},
}

SPARQL_TEMPLATE = """
SELECT DISTINCT ?film ?imdb ?result WHERE {{
  {{
    ?film wdt:P166 wd:{qid} .
    ?film wdt:P345 ?imdb .
    FILTER(STRSTARTS(STR(?imdb), "tt"))
    BIND("win" AS ?result)
  }} UNION {{
    ?film p:P1411 ?stmt .
    ?stmt ps:P1411 wd:{qid} .
    ?film wdt:P345 ?imdb .
    FILTER(STRSTARTS(STR(?imdb), "tt"))
    BIND("nomination" AS ?result)
  }}
}}
"""


def sparql_query(qid):
    q = SPARQL_TEMPLATE.format(qid=qid)
    for attempt in range(2):
        try:
            resp = requests.get(
                SPARQL_ENDPOINT,
                params={"query": q, "format": "json"},
                headers=SPARQL_HEADERS,
                timeout=30,
            )
            if resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"    429 rate-limited — waiting {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            rows = []
            for b in resp.json().get("results", {}).get("bindings", []):
                if "imdb" not in b:
                    continue
                raw = b["imdb"]["value"]
                if raw.startswith("http"):
                    raw = raw.rstrip("/").split("/")[-1]
                if not raw.startswith("tt"):
                    continue
                rows.append({
                    "imdb": raw,
                    "result": b.get("result", {}).get("value", "win"),
                })
            return rows
        except requests.exceptions.Timeout:
            if attempt == 0:
                print(f"    timeout — retrying after 10s")
                time.sleep(10)
            else:
                print(f"    timeout — skipping")
                return []
        except Exception as e:
            print(f"    error: {e}")
            return []
    return []


def fetch_award_winners(award_qid: str) -> list[dict]:
    """Return films that *won* award_qid.

    Each dict has keys: film_qid, film_label, year, director, imdb_id, result.
    film_qid / film_label / year / director may be None when Wikidata lacks data;
    imdb_id is always present (rows without one are dropped).
    result is always "win".
    """
    rows = sparql_query(award_qid)
    return [
        {
            "film_qid":    None,
            "film_label":  r["imdb"],   # best label we have without extra SPARQL
            "year":        None,
            "director":    None,
            "imdb_id":     r["imdb"],
            "result":      "win",
        }
        for r in rows if r["result"] == "win"
    ]


def fetch_award_nominees(award_qid: str) -> list[dict]:
    """Return films *nominated* for award_qid (result == "nomination").

    Same shape as fetch_award_winners, result is always "nomination".
    """
    rows = sparql_query(award_qid)
    return [
        {
            "film_qid":    None,
            "film_label":  r["imdb"],
            "year":        None,
            "director":    None,
            "imdb_id":     r["imdb"],
            "result":      "nomination",
        }
        for r in rows if r["result"] == "nomination"
    ]


def fetch_catalog(db):
    works = []
    offset = 0
    while True:
        batch = (db.table("works").select("id, imdb_id")
                 .not_.is_("imdb_id", "null")
                 .range(offset, offset + 999).execute().data or [])
        works.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    imdb_map = {r["imdb_id"].strip(): r["id"] for r in works if r.get("imdb_id", "").strip()}

    existing = []
    offset = 0
    while True:
        batch = (db.table("work_awards").select("work_id, award_id")
                 .range(offset, offset + 999).execute().data or [])
        existing.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000

    existing_pairs = {(r["work_id"], r["award_id"]) for r in existing}
    return imdb_map, existing_pairs


def insert_rows(db, rows):
    if not rows:
        return 0
    inserted = 0
    for i in range(0, len(rows), 50):
        batch = rows[i:i+50]
        try:
            db.table("work_awards").insert(batch).execute()
            inserted += len(batch)
        except Exception as batch_err:
            # Batch failed — try one by one and surface errors
            for rec in batch:
                try:
                    db.table("work_awards").insert(rec).execute()
                    inserted += 1
                except Exception as e:
                    print(f"  ✗ insert failed for {rec.get('award_id')} / {rec.get('work_id')}: {e}")
    return inserted


def main():
    parser = argparse.ArgumentParser(description="Enrich work_awards from Wikidata")
    parser.add_argument("--festival", "-f", default=None,
                        help="Festival to run: oscar, cannes, berlin, venice, bafta, sundance, toronto, golden-globe, cesar, goya, ariel, san-sebastian, locarno, ficg, ficm, mar-del-plata (omit to run all)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    targets = {k: v for k, v in AWARD_QUERY_MAP.items()
               if args.festival is None or v["festival"] == args.festival}

    if not targets:
        valid = sorted(set(v["festival"] for v in AWARD_QUERY_MAP.values()))
        print(f"Unknown festival '{args.festival}'. Valid: {valid}")
        return

    print(f"Loading catalog...")
    imdb_map, existing_pairs = fetch_catalog(db)
    print(f"  Works: {len(imdb_map)}  Existing awards: {len(existing_pairs)}")

    totals = {"new": 0, "skipped": 0, "unmatched": 0}

    for i, (award_id, meta) in enumerate(targets.items(), 1):
        qid = meta["qid"]
        full_id = f"award_{award_id}"
        print(f"[{i}/{len(targets)}] {award_id} ({qid})")

        results = sparql_query(qid)
        if not results:
            print(f"  → 0 results")
            time.sleep(2)
            continue

        to_insert = []
        for row in results:
            work_id = imdb_map.get(row["imdb"])
            if not work_id:
                totals["unmatched"] += 1
                continue
            pair = (work_id, full_id)
            if pair in existing_pairs:
                totals["skipped"] += 1
                continue
            to_insert.append({"work_id": work_id, "award_id": full_id, "result": row["result"]})
            existing_pairs.add(pair)
            totals["new"] += 1

        print(f"  Wikidata: {len(results)}  new: {len(to_insert)}  skipped: {totals['skipped']}")

        if to_insert and not args.dry_run:
            written = insert_rows(db, to_insert)
            print(f"  ✓ inserted {written}")

        time.sleep(2)

    print(f"\nSUMMARY: new={totals['new']} skipped={totals['skipped']} unmatched={totals['unmatched']}")


if __name__ == "__main__":
    main()
