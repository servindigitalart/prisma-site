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

AWARD_QUERY_MAP = {
    # ── Oscar (verified QIDs, IDs match awards table) ────────────────────────
    "oscar-best-picture":               {"qid": "Q102427",   "festival": "oscar"},
    "oscar-best-director":              {"qid": "Q103360",   "festival": "oscar"},
    "oscar-best-actress":               {"qid": "Q103618",   "festival": "oscar"},
    "oscar-best-actor":                 {"qid": "Q103916",   "festival": "oscar"},
    "oscar-best-intl-film":             {"qid": "Q105304",   "festival": "oscar"},
    "oscar-best-original-screenplay":   {"qid": "Q41417",    "festival": "oscar"},
    "oscar-best-adapted-screenplay":    {"qid": "Q107258",   "festival": "oscar"},
    "oscar-best-cinematography":        {"qid": "Q131520",   "festival": "oscar"},
    "oscar-best-supporting-actor":      {"qid": "Q106291",   "festival": "oscar"},
    "oscar-best-supporting-actress":    {"qid": "Q106301",   "festival": "oscar"},
    "oscar-best-original-score":        {"qid": "Q488651",   "festival": "oscar"},
    "oscar-best-film-editing":          {"qid": "Q281939",   "festival": "oscar"},
    # ── Cannes (verified QIDs) ───────────────────────────────────────────────
    "cannes-palme-dor":                 {"qid": "Q179808",   "festival": "cannes"},
    "cannes-grand-prix":                {"qid": "Q695106",   "festival": "cannes"},
    "cannes-jury-prize":                {"qid": "Q164200",   "festival": "cannes"},
    "cannes-best-director":             {"qid": "Q1136734",  "festival": "cannes"},
    "cannes-best-actress":              {"qid": "Q1401748",  "festival": "cannes"},
    "cannes-best-actor":                {"qid": "Q1400853",  "festival": "cannes"},
    "cannes-camera-dor":                {"qid": "Q775091",   "festival": "cannes"},
    "cannes-special-jury":              {"qid": "Q1361014",  "festival": "cannes"},
    # ── Berlin (verified QIDs) ───────────────────────────────────────────────
    "berlin-golden-bear":               {"qid": "Q154590",   "festival": "berlin"},
    "berlin-silver-bear-director":      {"qid": "Q706031",   "festival": "berlin"},
    "berlin-silver-bear-actress":       {"qid": "Q376834",   "festival": "berlin"},
    "berlin-silver-bear-actor":         {"qid": "Q819973",   "festival": "berlin"},
    "berlin-silver-bear-jury":          {"qid": "Q632291",   "festival": "berlin"},
    # ── Venice (verified QIDs) ───────────────────────────────────────────────
    "venice-golden-lion":               {"qid": "Q209459",   "festival": "venice"},
    "venice-special-jury":              {"qid": "Q2996614",  "festival": "venice"},
    "venice-volpi-cup-actress":         {"qid": "Q2089918",  "festival": "venice"},
    "venice-volpi-cup-actor":           {"qid": "Q2089923",  "festival": "venice"},
    # ── BAFTA (verified QIDs) ────────────────────────────────────────────────
    "bafta-best-film":                  {"qid": "Q139184",   "festival": "bafta"},
    "bafta-best-director":              {"qid": "Q787131",   "festival": "bafta"},
    "bafta-best-cinematography":        {"qid": "Q1576399",  "festival": "bafta"},
    "bafta-best-original-screenplay":   {"qid": "Q41375",    "festival": "bafta"},
    # ── Golden Globe (verified QIDs, IDs match awards table gg- prefix) ──────
    "gg-best-film-drama":               {"qid": "Q1011509",  "festival": "golden-globe"},
    "gg-best-director":                 {"qid": "Q586356",   "festival": "golden-globe"},
    "gg-best-intl-film":                {"qid": "Q387380",   "festival": "golden-globe"},
    # ── César (verified QIDs) ────────────────────────────────────────────────
    "cesar-best-film":                  {"qid": "Q645595",   "festival": "cesar"},
    "cesar-best-director":              {"qid": "Q24137",    "festival": "cesar"},
    "cesar-best-actress":               {"qid": "Q24241",    "festival": "cesar"},
    "cesar-best-actor":                 {"qid": "Q900494",   "festival": "cesar"},
    # ── Goya (verified QIDs) ─────────────────────────────────────────────────
    "goya-best-film":                   {"qid": "Q1467554",  "festival": "goya"},
    "goya-best-director":               {"qid": "Q1540553",  "festival": "goya"},
    # ── Ariel (verified QIDs) ────────────────────────────────────────────────
    "ariel-best-film":                  {"qid": "Q2108656",  "festival": "ariel"},
    "ariel-best-director":              {"qid": "Q2887050",  "festival": "ariel"},
    # ── San Sebastián (verified QIDs, IDs match awards table sansebastian-) ──
    "sansebastian-golden-shell":        {"qid": "Q775086",   "festival": "san-sebastian"},
    "sansebastian-silver-shell-actress":{"qid": "Q610152",   "festival": "san-sebastian"},
    "sansebastian-silver-shell-actor":  {"qid": "Q610136",   "festival": "san-sebastian"},
    # ── Locarno (verified QIDs) ──────────────────────────────────────────────
    "locarno-golden-leopard":           {"qid": "Q1700510",  "festival": "locarno"},
    # ── Sundance (verified QIDs) ─────────────────────────────────────────────
    "sundance-grand-jury-drama":        {"qid": "Q1377733",  "festival": "sundance"},
    "sundance-grand-jury-doc":          {"qid": "Q1377734",  "festival": "sundance"},
    "sundance-directing-drama":         {"qid": "Q3439490",  "festival": "sundance"},
    # ── Toronto (verified QIDs) ──────────────────────────────────────────────
    "toronto-peoples-choice":           {"qid": "Q39087364", "festival": "toronto"},
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
                        help="Festival to run: oscar, cannes, berlin, venice, bafta, sundance, toronto, golden-globe, cesar, goya, ariel, san-sebastian, locarno, ficg, ficm, mar-del-plata")
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
