"""
pipeline/enrich_awards_wikidata.py
────────────────────────────────────
Award-centric Wikidata enrichment.

DIRECTION: For each major award category, fetch ALL films that ever won/were
nominated, then match to our works table.

This is complementary to enrich_work_awards.py (which goes film→awards).
This script goes award→films, so it can surface awards for films we already
have in catalog that the per-film script may have missed.

Usage:
  python3 pipeline/enrich_awards_wikidata.py             # full run, live
  python3 pipeline/enrich_awards_wikidata.py --dry-run   # preview only
  python3 pipeline/enrich_awards_wikidata.py --award award_cannes-palme-dor
  python3 pipeline/enrich_awards_wikidata.py --debug     # show unmatched
"""

import sys
import re
import time
import argparse
import os
from collections import Counter
from dotenv import load_dotenv
import requests

load_dotenv(".env.local")
from supabase import create_client

# ─── Config ──────────────────────────────────────────────────────────────────

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "User-Agent": "PRISMA-film-db/1.0 (award enrichment; educational project)",
    "Accept": "application/sparql-results+json",
}
RATE_LIMIT_SLEEP = 1.2  # respect Wikidata API limits

# ─── Award → Wikidata QID mapping ────────────────────────────────────────────
# These are the award entity QIDs (the award itself, not the film).
# P166 = "award received", P1411 = "nominated for"
# QIDs verified against the existing enrich_work_awards.py WIKIDATA_AWARD_MAP.

AWARD_QUERY_MAP: dict[str, dict] = {
    # ── Cannes ──────────────────────────────────────────────────────────────
    "award_cannes-palme-dor": {
        "qid": "Q179808",
        "label": "Palme d'Or",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-grand-prix": {
        "qid": "Q695106",
        "label": "Grand Prix (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-best-director": {
        "qid": "Q1136734",
        "label": "Best Director (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-jury-prize": {
        "qid": "Q631033",
        "label": "Jury Prize (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-best-actress": {
        "qid": "Q1401748",
        "label": "Best Actress (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-best-actor": {
        "qid": "Q1400853",
        "label": "Best Actor (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-special-jury": {
        "qid": "Q1361014",
        "label": "Special Jury Prize (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-best-screenplay": {
        "qid": "Q1412911",
        "label": "Best Screenplay (Cannes)",
        "festival": "festival_cannes",
        "tier": "A",
    },
    "award_cannes-un-certain-regard": {
        "qid": "Q2306255",
        "label": "Un Certain Regard Prize",
        "festival": "festival_cannes",
        "tier": "B",
    },
    "award_cannes-fipresci": {
        "qid": "Q1377697",
        "label": "FIPRESCI Prize (Cannes)",
        "festival": "festival_cannes",
        "tier": "C",
    },
    # ── Berlin ──────────────────────────────────────────────────────────────
    "award_berlin-golden-bear": {
        "qid": "Q181699",
        "label": "Golden Bear",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-silver-bear-director": {
        "qid": "Q703764",
        "label": "Silver Bear Best Director",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-silver-bear-jury": {
        "qid": "Q632291",
        "label": "Silver Bear Grand Jury",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-silver-bear-actress": {
        "qid": "Q702400",
        "label": "Silver Bear Best Actress",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-silver-bear-actor": {
        "qid": "Q702402",
        "label": "Silver Bear Best Actor",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-silver-bear-screenplay": {
        "qid": "Q694585",
        "label": "Silver Bear Best Screenplay",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-jury-grand-prix": {
        "qid": "Q15862511",
        "label": "Berlin Jury Grand Prix",
        "festival": "festival_berlin",
        "tier": "A",
    },
    "award_berlin-fipresci": {
        "qid": "Q1377702",
        "label": "FIPRESCI Prize (Berlin)",
        "festival": "festival_berlin",
        "tier": "C",
    },
    # ── Venice ──────────────────────────────────────────────────────────────
    "award_venice-golden-lion": {
        "qid": "Q180942",
        "label": "Golden Lion",
        "festival": "festival_venice",
        "tier": "A",
    },
    "award_venice-silver-lion-director": {
        "qid": "Q1135659",
        "label": "Silver Lion Best Director",
        "festival": "festival_venice",
        "tier": "A",
    },
    "award_venice-grand-jury": {
        "qid": "Q1361066",
        "label": "Grand Jury Prize (Venice)",
        "festival": "festival_venice",
        "tier": "A",
    },
    "award_venice-special-jury": {
        "qid": "Q2996614",
        "label": "Special Jury Prize (Venice)",
        "festival": "festival_venice",
        "tier": "A",
    },
    "award_venice-volpi-cup-actress": {
        "qid": "Q901330",
        "label": "Volpi Cup Best Actress",
        "festival": "festival_venice",
        "tier": "A",
    },
    "award_venice-volpi-cup-actor": {
        "qid": "Q901332",
        "label": "Volpi Cup Best Actor",
        "festival": "festival_venice",
        "tier": "A",
    },
    "award_venice-fipresci": {
        "qid": "Q1377706",
        "label": "FIPRESCI Prize (Venice)",
        "festival": "festival_venice",
        "tier": "C",
    },
    # ── BAFTA ────────────────────────────────────────────────────────────────
    "award_bafta-best-film": {
        "qid": "Q637514",
        "label": "BAFTA Best Film",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-director": {
        "qid": "Q677507",
        "label": "BAFTA Best Director",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-cinematography": {
        "qid": "Q1576399",
        "label": "BAFTA Best Cinematography",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-original-screenplay": {
        "qid": "Q1576340",
        "label": "BAFTA Best Original Screenplay",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-actress": {
        "qid": "Q1135430",
        "label": "BAFTA Best Actress",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-actor": {
        "qid": "Q1135428",
        "label": "BAFTA Best Actor",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-screenplay": {
        "qid": "Q1135435",
        "label": "BAFTA Best Screenplay",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-editing": {
        "qid": "Q1135432",
        "label": "BAFTA Best Editing",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-score": {
        "qid": "Q1135436",
        "label": "BAFTA Best Score",
        "festival": "festival_bafta",
        "tier": "A",
    },
    "award_bafta-best-intl-film": {
        "qid": "Q3027434",
        "label": "BAFTA Best International Film",
        "festival": "festival_bafta",
        "tier": "A",
    },
    # ── César ────────────────────────────────────────────────────────────────
    "award_cesar-best-film": {
        "qid": "Q695280",
        "label": "César Best Film",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-director": {
        "qid": "Q695299",
        "label": "César Best Director",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-actress": {
        "qid": "Q24241",
        "label": "César Best Actress",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-actor": {
        "qid": "Q695291",
        "label": "César Best Actor",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-screenplay": {
        "qid": "Q633836",
        "label": "César Best Screenplay",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-cinematography": {
        "qid": "Q633837",
        "label": "César Best Cinematography",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-editing": {
        "qid": "Q633838",
        "label": "César Best Editing",
        "festival": "festival_cesar",
        "tier": "B",
    },
    "award_cesar-best-score": {
        "qid": "Q633841",
        "label": "César Best Score",
        "festival": "festival_cesar",
        "tier": "B",
    },
    # ── Goya ─────────────────────────────────────────────────────────────────
    "award_goya-best-film": {
        "qid": "Q1467554",
        "label": "Goya Best Film",
        "festival": "festival_goya",
        "tier": "B",
    },
    "award_goya-best-director": {
        "qid": "Q1571511",
        "label": "Goya Best Director",
        "festival": "festival_goya",
        "tier": "B",
    },
    "award_goya-best-actress": {
        "qid": "Q895819",
        "label": "Goya Best Actress",
        "festival": "festival_goya",
        "tier": "B",
    },
    "award_goya-best-actor": {
        "qid": "Q895818",
        "label": "Goya Best Actor",
        "festival": "festival_goya",
        "tier": "B",
    },
    "award_goya-best-screenplay": {
        "qid": "Q895824",
        "label": "Goya Best Screenplay",
        "festival": "festival_goya",
        "tier": "B",
    },
    "award_goya-best-cinematography": {
        "qid": "Q895823",
        "label": "Goya Best Cinematography",
        "festival": "festival_goya",
        "tier": "B",
    },
    "award_goya-best-intl-film": {
        "qid": "Q4892936",
        "label": "Goya Best International Film",
        "festival": "festival_goya",
        "tier": "B",
    },
    # ── Oscar ────────────────────────────────────────────────────────────────
    "award_oscar-best-picture": {
        "qid": "Q102427",
        "label": "Oscar Best Picture",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-director": {
        "qid": "Q103360",
        "label": "Oscar Best Director",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-intl-film": {
        "qid": "Q105304",
        "label": "Oscar Best International Feature Film",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-cinematography": {
        "qid": "Q229407",
        "label": "Oscar Best Cinematography",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-actress": {
        "qid": "Q103618",
        "label": "Oscar Best Actress",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-actor": {
        "qid": "Q103916",
        "label": "Oscar Best Actor",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-original-screenplay": {
        "qid": "Q41417",
        "label": "Oscar Best Original Screenplay",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-adapted-screenplay": {
        "qid": "Q107258",
        "label": "Oscar Best Adapted Screenplay",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-original-score": {
        "qid": "Q488651",
        "label": "Oscar Best Original Score",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-supporting-actor": {
        "qid": "Q106291",
        "label": "Oscar Best Supporting Actor",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-supporting-actress": {
        "qid": "Q106301",
        "label": "Oscar Best Supporting Actress",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    "award_oscar-best-film-editing": {
        "qid": "Q281939",
        "label": "Oscar Best Film Editing",
        "festival": "festival_academy-awards",
        "tier": "A",
    },
    # ── Golden Globe ─────────────────────────────────────────────────────────
    "award_gg-best-film-drama": {
        "qid": "Q1011509",
        "label": "Golden Globe Best Film (Drama)",
        "festival": "festival_golden-globe",
        "tier": "B",
    },
    "award_gg-best-director": {
        "qid": "Q1011540",
        "label": "Golden Globe Best Director",
        "festival": "festival_golden-globe",
        "tier": "B",
    },
    "award_gg-best-intl-film": {
        "qid": "Q1011560",
        "label": "Golden Globe Best International Film",
        "festival": "festival_golden-globe",
        "tier": "B",
    },
    "award_gg-best-actress-drama": {
        "qid": "Q1053284",
        "label": "Golden Globe Best Actress (Drama)",
        "festival": "festival_golden-globe",
        "tier": "B",
    },
    "award_gg-best-actor-drama": {
        "qid": "Q1053282",
        "label": "Golden Globe Best Actor (Drama)",
        "festival": "festival_golden-globe",
        "tier": "B",
    },
    "award_gg-best-screenplay": {
        "qid": "Q1053292",
        "label": "Golden Globe Best Screenplay",
        "festival": "festival_golden-globe",
        "tier": "B",
    },
    # ── Sundance ─────────────────────────────────────────────────────────────
    "award_sundance-grand-jury-drama": {
        "qid": "Q1377733",
        "label": "Sundance Grand Jury Prize (Drama)",
        "festival": "festival_sundance",
        "tier": "A",
    },
    "award_sundance-grand-jury-doc": {
        "qid": "Q1377734",
        "label": "Sundance Grand Jury Prize (Documentary)",
        "festival": "festival_sundance",
        "tier": "A",
    },
    "award_sundance-directing-drama": {
        "qid": "Q3439490",
        "label": "Sundance Directing Award",
        "festival": "festival_sundance",
        "tier": "A",
    },
    "award_sundance-grand-jury-documentary": {
        "qid": "Q7755039",
        "label": "Sundance Grand Jury Prize (Documentary) — alt",
        "festival": "festival_sundance",
        "tier": "A",
    },
    "award_sundance-audience-drama": {
        "qid": "Q15241820",
        "label": "Sundance Audience Award (Drama)",
        "festival": "festival_sundance",
        "tier": "A",
    },
    "award_sundance-directing-documentary": {
        "qid": "Q30587702",
        "label": "Sundance Directing Award (Documentary)",
        "festival": "festival_sundance",
        "tier": "A",
    },
    # ── San Sebastián ─────────────────────────────────────────────────────────
    "award_sansebastian-golden-shell": {
        "qid": "Q1143177",
        "label": "Golden Shell",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    "award_sansebastian-silver-shell-actress": {
        "qid": "Q1234936",
        "label": "Silver Shell Best Actress",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    "award_sansebastian-silver-shell-actor": {
        "qid": "Q1234946",
        "label": "Silver Shell Best Actor",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    # Canonical san-sebastian- prefix aliases (same QIDs)
    "award_san-sebastian-golden-shell": {
        "qid": "Q598703",
        "label": "Golden Shell (San Sebastián)",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    "award_san-sebastian-silver-shell-director": {
        "qid": "Q5765050",
        "label": "Silver Shell Best Director (San Sebastián)",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    "award_san-sebastian-silver-shell-actress": {
        "qid": "Q5765051",
        "label": "Silver Shell Best Actress (San Sebastián)",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    "award_san-sebastian-silver-shell-actor": {
        "qid": "Q5765052",
        "label": "Silver Shell Best Actor (San Sebastián)",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    "award_san-sebastian-jury-prize": {
        "qid": "Q5765053",
        "label": "Jury Prize (San Sebastián)",
        "festival": "festival_san-sebastian",
        "tier": "B",
    },
    # ── Locarno ──────────────────────────────────────────────────────────────
    "award_locarno-golden-leopard": {
        "qid": "Q216366",
        "label": "Golden Leopard",
        "festival": "festival_locarno",
        "tier": "B",
    },
    "award_locarno-silver-leopard": {
        "qid": "Q2346071",
        "label": "Silver Leopard (Locarno)",
        "festival": "festival_locarno",
        "tier": "B",
    },
    "award_locarno-jury-prize": {
        "qid": "Q2346070",
        "label": "Jury Prize (Locarno)",
        "festival": "festival_locarno",
        "tier": "B",
    },
    "award_locarno-best-director": {
        "qid": "Q2346069",
        "label": "Best Director (Locarno)",
        "festival": "festival_locarno",
        "tier": "B",
    },
    # ── Ariel ────────────────────────────────────────────────────────────────
    "award_ariel-best-film": {
        "qid": "Q1143196",
        "label": "Ariel Best Film",
        "festival": "festival_ariel",
        "tier": "B",
    },
    "award_ariel-best-director": {
        "qid": "Q3041798",
        "label": "Ariel Best Director",
        "festival": "festival_ariel",
        "tier": "B",
    },
    "award_ariel-best-actress": {
        "qid": "Q2887052",
        "label": "Ariel Best Actress",
        "festival": "festival_ariel",
        "tier": "B",
    },
    "award_ariel-best-actor": {
        "qid": "Q2887051",
        "label": "Ariel Best Actor",
        "festival": "festival_ariel",
        "tier": "B",
    },
    "award_ariel-best-screenplay": {
        "qid": "Q2887058",
        "label": "Ariel Best Screenplay",
        "festival": "festival_ariel",
        "tier": "B",
    },
    "award_ariel-best-cinematography": {
        "qid": "Q2887054",
        "label": "Ariel Best Cinematography",
        "festival": "festival_ariel",
        "tier": "B",
    },
    # ── Mar del Plata ─────────────────────────────────────────────────────────
    "award_mar-del-plata-golden-astor": {
        "qid": "Q4114882",
        "label": "Golden Astor (Mar del Plata)",
        "festival": "festival_mar-del-plata",
        "tier": "B",
    },
    "award_mar-del-plata-silver-astor": {
        "qid": "Q4114883",
        "label": "Silver Astor (Mar del Plata)",
        "festival": "festival_mar-del-plata",
        "tier": "B",
    },
    # ── Guadalajara FICG ──────────────────────────────────────────────────────
    "award_ficg-ibero-american-film": {
        "qid": "Q5428507",
        "label": "FICG Best Ibero-American Film",
        "festival": "festival_guadalajara",
        "tier": "B",
    },
    "award_ficg-mexican-film": {
        "qid": "Q17040890",
        "label": "FICG Best Mexican Film",
        "festival": "festival_guadalajara",
        "tier": "B",
    },
    # ── Toronto (TIFF) ────────────────────────────────────────────────────────
    "award_toronto-peoples-choice": {
        "qid": "Q1377681",
        "label": "TIFF People's Choice Award",
        "festival": "festival_toronto",
        "tier": "A",
    },
    "award_toronto-platform-prize": {
        "qid": "Q30587700",
        "label": "TIFF Platform Prize",
        "festival": "festival_toronto",
        "tier": "A",
    },
    # ── FIPRESCI ─────────────────────────────────────────────────────────────
    "award_fipresci-cannes": {
        "qid": "Q1377697",
        "label": "FIPRESCI Prize (Cannes)",
        "festival": "festival_fipresci",
        "tier": "C",
    },
    "award_fipresci-berlin": {
        "qid": "Q1377702",
        "label": "FIPRESCI Prize (Berlin)",
        "festival": "festival_fipresci",
        "tier": "C",
    },
    "award_fipresci-venice": {
        "qid": "Q1377706",
        "label": "FIPRESCI Prize (Venice)",
        "festival": "festival_fipresci",
        "tier": "C",
    },
}


# ─── SPARQL helpers ───────────────────────────────────────────────────────────

def sparql_query(sparql: str) -> list[dict]:
    """Execute a SPARQL query against Wikidata and return bindings."""
    try:
        resp = requests.get(
            SPARQL_ENDPOINT,
            params={"query": sparql, "format": "json"},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("results", {}).get("bindings", [])
    except requests.exceptions.Timeout:
        print("    [SPARQL] Request timed out", file=sys.stderr)
        return []
    except Exception as e:
        print(f"    [SPARQL] Error: {e}", file=sys.stderr)
        return []


def fetch_award_winners(award_qid: str) -> list[dict]:
    """
    Fetch all films that RECEIVED (won) a given award.
    Returns list of {film_qid, film_label, year, director, imdb_id, result}.
    Also fetches IMDb ID (P345) for high-confidence matching.
    """
    sparql = f"""
SELECT ?film ?filmLabel ?year ?directorLabel ?imdbID WHERE {{
  ?film wdt:P31 wd:Q11424 .
  ?film wdt:P166 wd:{award_qid} .
  OPTIONAL {{
    ?film wdt:P577 ?date .
    BIND(YEAR(?date) AS ?year)
  }}
  OPTIONAL {{ ?film wdt:P57 ?director . }}
  OPTIONAL {{ ?film wdt:P345 ?imdbID . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
ORDER BY ?year
LIMIT 500
"""
    bindings = sparql_query(sparql)
    results = []
    for b in bindings:
        film_uri = b.get("film", {}).get("value", "")
        film_qid = film_uri.split("/")[-1] if film_uri else None
        year_raw = b.get("year", {}).get("value")
        results.append({
            "film_qid": film_qid,
            "film_label": b.get("filmLabel", {}).get("value", ""),
            "year": int(year_raw) if year_raw else None,
            "director": b.get("directorLabel", {}).get("value", ""),
            "imdb_id": b.get("imdbID", {}).get("value"),
            "result": "win",
        })
    return results


def fetch_award_nominees(award_qid: str) -> list[dict]:
    """
    Fetch films nominated for (but potentially didn't win) a given award.
    P1411 = nominated for. Less consistently populated in Wikidata.
    """
    sparql = f"""
SELECT ?film ?filmLabel ?year ?directorLabel ?imdbID WHERE {{
  ?film wdt:P31 wd:Q11424 .
  ?film wdt:P1411 wd:{award_qid} .
  OPTIONAL {{
    ?film wdt:P577 ?date .
    BIND(YEAR(?date) AS ?year)
  }}
  OPTIONAL {{ ?film wdt:P57 ?director . }}
  OPTIONAL {{ ?film wdt:P345 ?imdbID . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
ORDER BY ?year
LIMIT 1000
"""
    bindings = sparql_query(sparql)
    results = []
    for b in bindings:
        film_uri = b.get("film", {}).get("value", "")
        film_qid = film_uri.split("/")[-1] if film_uri else None
        year_raw = b.get("year", {}).get("value")
        results.append({
            "film_qid": film_qid,
            "film_label": b.get("filmLabel", {}).get("value", ""),
            "year": int(year_raw) if year_raw else None,
            "director": b.get("directorLabel", {}).get("value", ""),
            "imdb_id": b.get("imdbID", {}).get("value"),
            "result": "nomination",
        })
    return results


# ─── Work matching ────────────────────────────────────────────────────────────

# Articles stripped from the front of titles before normalising.
# Covers English, French, Spanish, Italian, German, Portuguese.
_ARTICLES = re.compile(
    r"^(the|a|an|le|la|les|l'|un|une|des|el|los|las|un|una|unos|unas"
    r"|der|die|das|ein|eine|il|lo|gli|i|un'|o|os|a|as)\s+",
    re.IGNORECASE,
)


def _norm(title: str) -> str:
    """
    Aggressive normalisation for fuzzy matching:
      1. lower-case and strip outer whitespace
      2. strip a leading article (multi-language)
      3. remove all non-alphanumeric characters (punctuation, apostrophes, etc.)
      4. collapse internal whitespace
    """
    t = title.lower().strip()
    t = _ARTICLES.sub("", t)
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


class WorksIndex:
    """
    Multi-key lookup index for works.

    Priority order inside match():
      1. wikidata_qid  (exact, most reliable)
      2. imdb_id       (exact, very reliable)
      3. (norm_title, year)    with ±2 year tolerance
      4. (exact_lower, year)   with ±2 year tolerance
      5. norm_title alone      (title-only fallback, no year)
      6. exact_lower alone
    """

    def __init__(self, works: list[dict]):
        # Primary exact-ID indexes
        self.by_wikidata: dict[str, str] = {}   # wikidata_qid  → work_id
        self.by_imdb:     dict[str, str] = {}   # imdb_id       → work_id

        # Title-based indexes: key → work_id
        # (norm_title, year) and (exact_lower, year) tuples
        self.by_norm_year:  dict[tuple, str] = {}
        self.by_exact_year: dict[tuple, str] = {}
        # title-only fallbacks
        self.by_norm:  dict[str, str] = {}
        self.by_exact: dict[str, str] = {}

        for w in works:
            wid  = w["id"]
            year = w.get("year")

            # ── ID-based ──────────────────────────────────────────────────
            if w.get("wikidata_id"):
                self.by_wikidata[w["wikidata_id"]] = wid
            if w.get("imdb_id"):
                self.by_imdb[w["imdb_id"]] = wid

            # ── Title-based ───────────────────────────────────────────────
            exact = w["title"].lower().strip()
            norm  = _norm(w["title"])

            self.by_norm_year[(norm, year)]   = wid
            self.by_exact_year[(exact, year)] = wid

            # Title-only: first-seen wins (avoids clobbering more-specific entries)
            if norm not in self.by_norm:
                self.by_norm[norm] = wid
            if exact not in self.by_exact:
                self.by_exact[exact] = wid

    def match(
        self,
        film_label: str,
        year: int | None,
        film_qid: str | None = None,
        imdb_id: str | None = None,
    ) -> str | None:
        # 1. Wikidata QID — highest confidence
        if film_qid and film_qid in self.by_wikidata:
            return self.by_wikidata[film_qid]

        # 2. IMDb ID — very high confidence
        if imdb_id and imdb_id in self.by_imdb:
            return self.by_imdb[imdb_id]

        norm  = _norm(film_label)
        exact = film_label.lower().strip()

        # 3 & 4. Title + year (± 0, ±1, ±2)
        for delta in (0, -1, 1, -2, 2):
            y = (year + delta) if year else None
            if (norm, y) in self.by_norm_year:
                return self.by_norm_year[(norm, y)]
            if (exact, y) in self.by_exact_year:
                return self.by_exact_year[(exact, y)]

        # 5 & 6. Title-only fallback (no year available or no year match)
        if norm in self.by_norm:
            return self.by_norm[norm]
        if exact in self.by_exact:
            return self.by_exact[exact]

        return None


def build_works_index(db) -> "WorksIndex":
    """
    Load all works from DB and return a WorksIndex supporting multi-key lookup.
    Fetches: id, title, year, wikidata_id, imdb_id.
    """
    r = db.table("works").select("id, title, year, wikidata_id, imdb_id").execute()
    idx = WorksIndex(r.data)
    n_works = len(r.data)
    print(f"   {n_works} works loaded → "
          f"{len(idx.by_wikidata)} wikidata QIDs, "
          f"{len(idx.by_imdb)} IMDb IDs, "
          f"{len(idx.by_norm_year)} norm+year keys")
    return idx


def match_film(
    film_label: str,
    year: int | None,
    works_index: "WorksIndex",
    film_qid: str | None = None,
    imdb_id: str | None = None,
) -> str | None:
    """Thin wrapper kept for API compatibility. Delegates to WorksIndex.match()."""
    return works_index.match(film_label, year, film_qid=film_qid, imdb_id=imdb_id)


# ─── DB insert ────────────────────────────────────────────────────────────────

def insert_rows(db, rows: list[dict]) -> int:
    """
    Batch-insert rows into work_awards in groups of 50.
    Assumes duplicate-guarding has already been done via existing_pairs.
    Returns count of inserted rows.
    """
    if not rows:
        return 0
    inserted = 0
    # Batch in groups of 50
    for i in range(0, len(rows), 50):
        batch = rows[i:i + 50]
        try:
            db.table("work_awards").insert(batch).execute()
            inserted += len(batch)
        except Exception as exc:
            # Batch failed — try one by one
            for rec in batch:
                try:
                    db.table("work_awards").insert(rec).execute()
                    inserted += 1
                except Exception:
                    pass
    return inserted


def fetch_existing_pairs(db, award_id: str) -> set[tuple]:
    """
    Return set of (work_id, award_id) tuples already in work_awards for this award.
    Also prints first 3 result values as a sanity-check on DB format.
    """
    r = db.table("work_awards").select("work_id, award_id, result").eq("award_id", award_id).execute()
    if r.data:
        sample = [x["result"] for x in r.data[:3]]
        print(f"   [DB check] existing result values (first 3): {sample}")
    return {(x["work_id"], x["award_id"]) for x in r.data}


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Enrich work_awards from Wikidata (award-centric)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without inserting")
    parser.add_argument("--award", help="Process only this award_id (e.g. award_cannes-palme-dor)")
    parser.add_argument("--debug", action="store_true", help="Print unmatched films")
    parser.add_argument("--wins-only", action="store_true", help="Skip P1411 nomination queries")
    args = parser.parse_args()

    db = create_client(os.environ["PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("📥 Loading works index from DB...")
    works_index = build_works_index(db)
    print()

    awards_to_process = AWARD_QUERY_MAP
    if args.award:
        if args.award not in AWARD_QUERY_MAP:
            print(f"❌ Unknown award_id: {args.award}", file=sys.stderr)
            print(f"   Known: {', '.join(sorted(AWARD_QUERY_MAP.keys()))}")
            sys.exit(1)
        awards_to_process = {args.award: AWARD_QUERY_MAP[args.award]}

    total_fetched = total_inserted = total_skipped = total_unmatched = 0

    for award_id, meta in awards_to_process.items():
        qid = meta["qid"]
        label = meta["label"]
        print(f"🔍 {award_id} (QID: {qid})")

        # ── Fetch wins ──
        print(f"   Querying wins (P166)...")
        wins = fetch_award_winners(qid)
        print(f"   → {len(wins)} wins found")
        time.sleep(RATE_LIMIT_SLEEP)

        # ── Fetch nominations (unless skipped) ──
        noms = []
        if not args.wins_only:
            print(f"   Querying nominations (P1411)...")
            noms = fetch_award_nominees(qid)
            print(f"   → {len(noms)} nominations found")
            time.sleep(RATE_LIMIT_SLEEP)

        all_records = wins + noms
        total_fetched += len(all_records)

        # ── Deduplicate by (film_qid, result) — Wikidata returns one row per
        #    statement qualifier, so a single win can appear many times with
        #    slightly different years. Keep the row whose year is most common
        #    (modal), falling back to the median, so the award year is accurate.
        seen: dict[tuple, list] = {}   # (film_qid, result) → [rows]
        for r in all_records:
            key = (r.get("film_qid") or r["film_label"].lower(), r["result"])
            seen.setdefault(key, []).append(r)
        deduped_all: list[dict] = []
        for rows in seen.values():
            # Pick the modal year; if all unique, pick middle value
            years = [r["year"] for r in rows if r["year"] is not None]
            if years:
                modal_year = Counter(years).most_common(1)[0][0]
            else:
                modal_year = None
            # Find a representative row with that year (or any row if no year)
            rep = next((r for r in rows if r["year"] == modal_year), rows[0])
            deduped_all.append(rep)

        # ── Drop nominations where the same film already has a win ──
        win_qids = {r.get("film_qid") or r["film_label"].lower()
                    for r in deduped_all if r["result"] == "win"}
        deduped = []
        for r in deduped_all:
            if r["result"] == "nomination":
                key = r.get("film_qid") or r["film_label"].lower()
                if key in win_qids:
                    continue
            deduped.append(r)

        # ── Fetch existing pairs from DB (guards against duplicates) ──
        existing_pairs: set[tuple] = set()
        if not args.dry_run:
            existing_pairs = fetch_existing_pairs(db, award_id)

        # ── Match to works ──
        rows_to_insert = []
        unmatched = []
        skipped = 0
        for r in deduped:
            work_id = match_film(
                r["film_label"], r["year"], works_index,
                film_qid=r.get("film_qid"),
                imdb_id=r.get("imdb_id"),
            )
            if work_id:
                if (work_id, award_id) in existing_pairs:
                    skipped += 1
                    continue
                rows_to_insert.append({
                    "work_id": work_id,
                    "award_id": award_id,
                    "year": r["year"],
                    "category": label,
                    "result": r["result"],
                    "person_id": None,
                })
            else:
                unmatched.append(r)

        total_unmatched += len(unmatched)
        if args.debug and unmatched:
            print(f"   ⚠  Unmatched ({len(unmatched)}):")
            for u in unmatched[:20]:
                print(
                    f"      {u['film_label']!r:45s} "
                    f"yr={u.get('year')}  "
                    f"qid={u.get('film_qid','?'):12s} "
                    f"imdb={u.get('imdb_id') or '?':12s} "
                    f"dir={u.get('director','?')[:25]}"
                )
            if len(unmatched) > 20:
                print(f"      ... and {len(unmatched)-20} more")

        # ── Insert (batched, duplicates already filtered by existing_pairs) ──
        if rows_to_insert or skipped:
            if args.dry_run:
                for row in rows_to_insert:
                    print(f"    [DRY RUN] would insert: {row['work_id']} | {row['award_id']} | {row['result']} | {row.get('year')}")
                inserted = len(rows_to_insert)
            else:
                inserted = insert_rows(db, rows_to_insert)
            total_inserted += inserted
            total_skipped += skipped
            print(f"   ✅ {inserted} inserted, {skipped} already existed, {len(unmatched)} unmatched\n")
        else:
            print(f"   ℹ  No matching works found for {award_id}\n")

    print("─" * 60)
    print(f"SUMMARY")
    print(f"  Awards processed : {len(awards_to_process)}")
    print(f"  Records fetched  : {total_fetched}")
    print(f"  Inserted         : {total_inserted}")
    print(f"  Already existed  : {total_skipped}")
    print(f"  No work match    : {total_unmatched}")
    if args.dry_run:
        print("  (DRY RUN — no changes made)")


if __name__ == "__main__":
    main()
