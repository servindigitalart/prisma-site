#!/usr/bin/env python3
"""
pipeline/scrape_wikipedia_awards.py

Scrapes Wikipedia award pages to populate candidates table with
complete historical coverage of winners and nominees.

Uses the MediaWiki API (wikitext) — no HTML parsing needed.

Usage:
  python pipeline/scrape_wikipedia_awards.py --festival cannes
  python pipeline/scrape_wikipedia_awards.py --festival cannes --year 2024
  python pipeline/scrape_wikipedia_awards.py --festival cannes --from-year 2000
  python pipeline/scrape_wikipedia_awards.py --all
  python pipeline/scrape_wikipedia_awards.py --report
  python pipeline/scrape_wikipedia_awards.py --dry-run --festival berlin
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from supabase import create_client

# Import shared scoring constants and helpers from populate_candidates
sys.path.insert(0, str(Path(__file__).parent))
from populate_candidates import (
    FESTIVAL_TIER_WEIGHT,
    CATEGORY_FILM_MULTIPLIER,
    DEFAULT_CATEGORY_MULTIPLIER,
    DEFAULT_FESTIVAL_WEIGHT,
    upsert_candidates,
    tmdb_from_imdb,
    get_scoring_map,
)

load_dotenv(Path(__file__).parent.parent / ".env.local")
load_dotenv(Path(__file__).parent.parent / ".env")

# ─── Constants ────────────────────────────────────────────────────────────────

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
TMDB_API      = "https://api.themoviedb.org/3"
TMDB_KEY      = os.environ.get("TMDB_API_KEY", "")

WIKIPEDIA_UA  = "PRISMA-film-database/1.0 (https://prisma.film; historical award scraper)"
WIKIPEDIA_HEADERS = {"User-Agent": WIKIPEDIA_UA}

WIKIPEDIA_SLEEP   = 1.1   # seconds between Wikipedia API calls
TMDB_SLEEP        = 0.26  # seconds between TMDB calls (≤40 req/10s)

CHECKPOINT_DIR = Path(__file__).parent / "scrape_checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)

# ─── Festival page definitions ────────────────────────────────────────────────
#
# "title_type" controls how Wikipedia page titles are built:
#   "year"    → "{year} Cannes Film Festival"          (simplest, Wikipedia redirects)
#   "ordinal" → "{ordinal} Academy Awards"             (ordinal from start_year)
#   "ordinal_custom" → use explicit ORDINAL_MAP table  (festivals with gaps)
#
# For "ordinal" festivals the edition = (year - start_year + 1) minus any skip
# years listed in "skip_years".  Wikipedia resolves redirects automatically so
# we just need to produce the title Wikipedia *recognises*.

FESTIVAL_PAGES: dict[str, dict] = {
    # ── Year-indexed (Wikipedia uses "{year} Name" as canonical title) ────────
    "cannes": {
        "years":      range(1946, 2026),
        "title_type": "year",
        "pattern":    "{year} Cannes Film Festival",
        "awards": {
            "Palme d'Or":           "award_cannes-palme-dor",
            "Grand Prix":           "award_cannes-grand-prix",
            "Jury Prize":           "award_cannes-jury-prize",
            "Best Director":        "award_cannes-best-director",
            "Best Actress":         "award_cannes-best-actress",
            "Best Actor":           "award_cannes-best-actor",
            "Best Screenplay":      "award_cannes-best-screenplay",
            "Caméra d'Or":          "award_cannes-camera-dor",
            "Camera d'Or":          "award_cannes-camera-dor",   # ASCII fallback for older pages
            "Un Certain Regard":    "award_cannes-un-certain-regard",
            "Special Jury Prize":   "award_cannes-special-jury",
        },
    },
    "berlin": {
        "years":      range(1951, 2026),
        "title_type": "year",
        "pattern":    "{year} Berlin International Film Festival",
        "awards": {
            "Golden Bear":                        "award_berlin-golden-bear",
            "Silver Bear Grand Jury Prize":       "award_berlin-grand-jury-prize",
            "Silver Bear for Best Director":      "award_berlin-silver-bear-director",
            "Silver Bear for Best Actress":       "award_berlin-silver-bear-actress",
            "Silver Bear for Best Actor":         "award_berlin-silver-bear-actor",
            "Silver Bear Jury Prize":             "award_berlin-silver-bear-jury",
            "Silver Bear for Best Leading Performance": "award_berlin-silver-bear-actor",
        },
    },
    "venice": {
        "years":      range(1932, 2026),
        "title_type": "year",
        "pattern":    "{year} Venice Film Festival",
        "awards": {
            "Golden Lion":                  "award_venice-golden-lion",
            "Silver Lion":                  "award_venice-silver-lion",
            "Grand Jury Prize":             "award_venice-grand-jury",
            "Best Director":                "award_venice-best-director",
            "Volpi Cup for Best Actress":   "award_venice-volpi-cup-actress",
            "Volpi Cup for Best Actor":     "award_venice-volpi-cup-actor",
            "Special Jury Prize":           "award_venice-special-jury",
        },
    },
    "sundance": {
        "years":      range(1985, 2026),   # Sundance brand started 1985
        "title_type": "year",
        "pattern":    "{year} Sundance Film Festival",
        "awards": {
            "Grand Jury Prize Drama":           "award_sundance-grand-jury-drama",
            "Grand Jury Prize Documentary":     "award_sundance-grand-jury-doc",
            "Audience Award Drama":             "award_sundance-audience-drama",
            "Directing Award Drama":            "award_sundance-directing-drama",
            "Grand Jury Prize":                 "award_sundance-grand-jury-drama",
        },
    },
    # ── Ordinal-indexed (Wikipedia uses "{nth} Name" as canonical title) ──────
    "oscar": {
        # 1st Academy Awards = 1929 ceremony
        "years":      range(1929, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Academy Awards",
        "start_year": 1929,
        "skip_years": [],
        "awards": {
            # Canonical names used in our DB
            "Best Picture":                               "award_oscar-best-picture",
            "Best Director":                              "award_oscar-best-director",
            "Best Actress":                               "award_oscar-best-actress",
            "Best Actor":                                 "award_oscar-best-actor",
            "Best Supporting Actress":                    "award_oscar-best-supporting-actress",
            "Best Supporting Actor":                      "award_oscar-best-supporting-actor",
            "Best International Feature Film":            "award_oscar-best-intl-film",
            "Best Foreign Language Film":                 "award_oscar-best-intl-film",
            "Best Original Screenplay":                   "award_oscar-best-original-screenplay",
            "Best Adapted Screenplay":                    "award_oscar-best-adapted-screenplay",
            "Best Cinematography":                        "award_oscar-best-cinematography",
            "Best Documentary Feature":                   "award_oscar-best-documentary",
            "Best Animated Feature":                      "award_oscar-best-animated",
            "Best Original Score":                        "award_oscar-best-original-score",
            "Best Film Editing":                          "award_oscar-best-film-editing",
            "Best Sound":                                 "award_oscar-best-sound",
            "Best Production Design":                     "award_oscar-best-production-design",
            # Wikipedia {{Award category}} label variants (modern era)
            "Best Directing":                             "award_oscar-best-director",
            "Best Actor in a Leading Role":               "award_oscar-best-actor",
            "Best Actress in a Leading Role":             "award_oscar-best-actress",
            "Best Actor in a Supporting Role":            "award_oscar-best-supporting-actor",
            "Best Actress in a Supporting Role":          "award_oscar-best-supporting-actress",
            "Best Writing (Original Screenplay)":         "award_oscar-best-original-screenplay",
            "Best Writing (Adapted Screenplay)":          "award_oscar-best-adapted-screenplay",
            "Best Writing, Original Screenplay":          "award_oscar-best-original-screenplay",
            "Best Writing, Adapted Screenplay":           "award_oscar-best-adapted-screenplay",
            "Best Animated Feature Film":                 "award_oscar-best-animated",
            "Best Documentary Feature Film":              "award_oscar-best-documentary",
            "Best Music (Original Score)":                "award_oscar-best-original-score",
            "Best Music (Original Song)":                 "award_oscar-best-original-score",
            "Best Film Editing":                          "award_oscar-best-film-editing",
            "Best Cinematography":                        "award_oscar-best-cinematography",
        },
    },
    "bafta": {
        # 1st BAFTA = 1948 ceremony  (BAFTA was founded 1947, 1st awards 1948)
        "years":      range(1948, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} British Academy Film Awards",
        "start_year": 1948,
        "skip_years": [],
        "awards": {
            "Best Film":                                  "award_bafta-best-film",
            "Best Director":                              "award_bafta-best-director",
            "Best Actress":                               "award_bafta-best-actress",
            "Best Actor":                                 "award_bafta-best-actor",
            "Best Actress in a Leading Role":             "award_bafta-best-actress",
            "Best Actor in a Leading Role":               "award_bafta-best-actor",
            "Best Film Not in the English Language":      "award_bafta-best-intl-film",
            "Best Original Screenplay":                   "award_bafta-best-original-screenplay",
            "Best Adapted Screenplay":                    "award_bafta-best-adapted-screenplay",
            "Best Cinematography":                        "award_bafta-best-cinematography",
            "Best Documentary":                           "award_bafta-best-documentary",
            "Best Animated Film":                         "award_bafta-best-animated",
        },
    },
    "cesar": {
        # 1st César = 1976 ceremony
        "years":      range(1976, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} César Awards",
        "start_year": 1976,
        "skip_years": [],
        "awards": {
            "Best Film":            "award_cesar-best-film",
            "Best Director":        "award_cesar-best-director",
            "Best Actress":         "award_cesar-best-actress",
            "Best Actor":           "award_cesar-best-actor",
            "Best Foreign Film":    "award_cesar-best-intl-film",
            "Best Screenplay":      "award_cesar-best-screenplay",
            "Best Original Screenplay": "award_cesar-best-screenplay",
            "Best Animated Film":   "award_cesar-best-animated",
            "Best Documentary":     "award_cesar-best-documentary",
        },
    },
    "goya": {
        # 1st Goya = 1987 ceremony
        "years":      range(1987, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Goya Awards",
        "start_year": 1987,
        "skip_years": [],
        "awards": {
            "Best Film":                    "award_goya-best-film",
            "Best Director":                "award_goya-best-director",
            "Best Actress":                 "award_goya-best-actress",
            "Best Actor":                   "award_goya-best-actor",
            "Best Ibero-American Film":     "award_goya-best-iberoamerican-film",
            "Best Animated Film":           "award_goya-best-animated",
            "Best Documentary":             "award_goya-best-documentary",
        },
    },
    "san_sebastian": {
        # 1st San Sebastián = 1953 ceremony
        "years":      range(1953, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} San Sebastián International Film Festival",
        "start_year": 1953,
        "skip_years": [],
        "awards": {
            "Golden Shell":                         "award_sansebastian-golden-shell",
            "Silver Shell for Best Director":       "award_sansebastian-silver-director",
            "Silver Shell for Best Actress":        "award_sansebastian-silver-actress",
            "Silver Shell for Best Actor":          "award_sansebastian-silver-actor",
        },
    },
    "locarno": {
        # 1st Locarno = 1946 ceremony
        "years":      range(1946, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Locarno Film Festival",
        "start_year": 1946,
        "skip_years": [],
        "awards": {
            "Golden Leopard":       "award_locarno-golden-leopard",
            "Silver Leopard":       "award_locarno-silver-leopard",
            "Special Jury Prize":   "award_locarno-special-jury",
            "Best Director":        "award_locarno-best-director",
        },
    },
    "ariel": {
        # 1st Ariel = 1947 ceremony  (65th = 2023, so start = 2023-65+1 = 1959? No.)
        # Confirmed: "65th Ariel Awards" = 2023 → start_year = 2023-64 = 1959
        # But Ariel started in 1946 with the 1st ceremony.  After a long hiatus
        # it was relaunched in 1987.  Wikipedia pages exist only for modern era.
        # The 65th Ariel Awards = 2023 means edition = year - 1958
        "years":      range(1987, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Ariel Awards",
        "start_year": 1959,   # calibrated: 2023 - 65 + 1 = 1959
        "skip_years": [],
        "awards": {
            "Best Picture":             "award_ariel-best-film",
            "Best Film":                "award_ariel-best-film",
            "Best Director":            "award_ariel-best-director",
            "Best Actress":             "award_ariel-best-actress",
            "Best Actor":               "award_ariel-best-actor",
            "Best Screenplay":          "award_ariel-best-screenplay",
            "Best Original Screenplay": "award_ariel-best-screenplay",
            "Best Cinematography":      "award_ariel-best-cinematography",
            "Best Editing":             "award_ariel-best-editing",
            "Best Film Editing":        "award_ariel-best-editing",
            "Best Score":               "award_ariel-best-score",
            "Best Animated Film":       "award_ariel-best-animated",
            "Best Documentary":         "award_ariel-best-documentary",
            "Best International Film":  "award_ariel-best-intl-film",
        },
    },
    "ficg": {
        # 1st Guadalajara = 1986 ceremony
        "years":      range(1986, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Guadalajara International Film Festival",
        "start_year": 1986,
        "skip_years": [],
        "awards": {
            "Best Ibero-American Film":     "award_ficg-best-iberoamerican-film",
            "Best Mexican Film":            "award_ficg-best-mexican-film",
            "Best Documentary":             "award_ficg-best-documentary",
        },
    },
    "ficm": {
        # 1st Morelia = 2003 ceremony
        "years":      range(2003, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Morelia International Film Festival",
        "start_year": 2003,
        "skip_years": [],
        "awards": {
            "Best Mexican Film":    "award_ficm-best-mexican-film",
            "Best Documentary":     "award_ficm-best-documentary",
            "Best Short Film":      "award_ficm-best-short",
        },
    },
    "mar_del_plata": {
        # 1st Mar del Plata = 1954 ceremony  (there were gaps; modern era ~1996+)
        "years":      range(1996, 2026),
        "title_type": "ordinal",
        "pattern":    "{ordinal} Mar del Plata International Film Festival",
        "start_year": 1954,
        "skip_years": list(range(1971, 1996)),  # festival suspended 1971-1995
        "awards": {
            "Golden Astor": "award_mar-del-plata-golden-astor",
            "Silver Astor": "award_mar-del-plata-silver-astor",
        },
    },
}


# ─── Ordinal helper ───────────────────────────────────────────────────────────

def ordinal(n: int) -> str:
    """Convert integer to ordinal string: 1→'1st', 2→'2nd', 77→'77th'."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ─── Page title builder ───────────────────────────────────────────────────────

def _compute_edition(festival_key: str, year: int) -> int:
    """
    Compute the edition/ceremony number for a given year.
    Accounts for skip_years (years when festival was not held).
    """
    cfg        = FESTIVAL_PAGES[festival_key]
    start      = cfg.get("start_year", year)
    skip_years = set(cfg.get("skip_years", []))
    # Count active years from start up to and including `year`
    return sum(1 for y in range(start, year + 1) if y not in skip_years)


def build_page_title(festival_key: str, year: int) -> str:
    """Build the Wikipedia page title for a festival ceremony year."""
    cfg        = FESTIVAL_PAGES[festival_key]
    title_type = cfg.get("title_type", "year")
    pattern    = cfg["pattern"]

    if title_type == "year":
        return pattern.format(year=year)
    else:  # "ordinal"
        edition = _compute_edition(festival_key, year)
        return pattern.format(ordinal=ordinal(edition), year=year, edition=edition)


# ─── Title fallbacks ─────────────────────────────────────────────────────────

def _fallback_titles(festival_key: str, year: int) -> list[str]:
    """
    Return alternative Wikipedia page titles to try if the primary one fails.
    Wikipedia often has both year-indexed and ordinal-indexed titles for the same page.
    """
    cfg        = FESTIVAL_PAGES[festival_key]
    title_type = cfg.get("title_type", "year")
    edition    = _compute_edition(festival_key, year)
    fallbacks  = []

    if title_type == "year":
        # Try ordinal variants
        base = cfg["pattern"].split("{year}")[0].strip() + cfg["pattern"].split("{year}")[-1].strip()
        name = cfg["pattern"].replace("{year} ", "").replace(" {year}", "").strip()
        fallbacks.append(f"{ordinal(edition)} {name}")
    else:
        # Try year-based variants
        name = cfg["pattern"].replace("{ordinal} ", "").replace(" {ordinal}", "").strip()
        fallbacks.append(f"{year} {name}")
        fallbacks.append(f"{name} {year}")

    return [t for t in fallbacks if t != build_page_title(festival_key, year)]


# ─── Wikipedia MediaWiki API ──────────────────────────────────────────────────

def get_wikipedia_wikitext(title: str) -> Optional[str]:
    """
    Fetch raw wikitext for a Wikipedia page via the MediaWiki API.
    Returns wikitext string or None if page not found / on error.
    Handles HTTP 429 with exponential backoff.
    """
    params = {
        "action":    "parse",
        "page":      title,
        "prop":      "wikitext",
        "format":    "json",
        "redirects": True,
    }
    backoff = 2.0
    for attempt in range(4):
        try:
            resp = requests.get(
                WIKIPEDIA_API,
                params=params,
                headers=WIKIPEDIA_HEADERS,
                timeout=20,
            )
            if resp.status_code == 429:
                print(f"    [WP] 429 rate-limit — sleeping {backoff:.0f}s")
                time.sleep(backoff)
                backoff *= 2
                continue
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                code = data["error"].get("code", "")
                if code == "missingtitle":
                    return None
                print(f"    [WP] API error for '{title}': {data['error']}")
                return None
            return data["parse"]["wikitext"]["*"]
        except requests.exceptions.Timeout:
            print(f"    [WP] Timeout for '{title}' (attempt {attempt+1})")
            time.sleep(backoff)
            backoff *= 2
        except Exception as e:
            print(f"    [WP] Error for '{title}': {e}")
            return None
    return None


# ─── Wikitext cleaning helpers ────────────────────────────────────────────────

def strip_wiki_markup(text: str) -> str:
    """Remove common wiki markup, returning plain text."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<ref[^/]*/?>", "", text, flags=re.IGNORECASE)
    # Remove templates — three passes for nested braces
    for _ in range(4):
        text = re.sub(r"\{\{[^{}]*\}\}", " ", text)
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'{2,3}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[[a-z0-9 ]{1,4}\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _link_target(raw: str) -> Optional[str]:
    """
    Given the inner text of [[...]], return the link target (before |),
    or None if it's a File/Category/Template link.
    """
    target = raw.split("|")[0].strip()
    if not target or target.startswith("#"):
        return None
    if ":" in target:
        # File:, Category:, Template:, Help:, etc.
        prefix = target.split(":")[0].lower()
        if prefix in ("file", "image", "category", "template", "help",
                      "wikipedia", "wikt", "commons", "special"):
            return None
    return target


def _clean_film_title(raw: str) -> Optional[str]:
    """
    Extract a clean film title from a raw wikilink target like
    'Oppenheimer (film)' → 'Oppenheimer'
    'The Zone of Interest (film)' → 'The Zone of Interest'
    'Monster (2023 Japanese film)' → 'Monster'
    'Anora' → 'Anora'
    Returns None if the title looks like a person, country, award name, etc.
    """
    title = raw.strip()
    # Remove disambiguation suffixes: (film), (2023 film), (2023 Japanese film), etc.
    title = re.sub(
        r"\s*\((?:\d{4}\s+)?(?:\w+\s+)?(?:film|movie|documentary|series|miniseries|"
        r"short film|TV film|television film|animated film|anime)\s*\)\s*$",
        "", title, flags=re.IGNORECASE
    ).strip()
    if not title or len(title) < 2 or len(title) > 120:
        return None
    return title


# ─── Wikitext award section parser ───────────────────────────────────────────

# Regex to detect an {{Award category|...|[[Category Name]]}} template header
_AWARD_CAT_RE = re.compile(
    r"\{\{Award category[^}]*?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
    re.IGNORECASE | re.DOTALL,
)

# Detect a film link inside ''[[Film]]'' (italic wikilink = film title in many formats)
_ITALIC_FILM_RE = re.compile(r"''(?:\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]|([^']+?))''")

# Bold+italic winner: '''''[[Film (film)|Film]]'''''  or  '''[[Film]]'''
_BOLD_ITALIC_FILM_RE = re.compile(
    r"''''?'(?:\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]|([^']{2,80}))''{2,3}"
)

def _normalize_cat(text: str) -> str:
    """Lowercase + collapse whitespace for fuzzy matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


# Synonym pairs for award category vocabulary:  wiki_word → canonical_word
# Applied before comparison so "directing" == "director", etc.
_CAT_SYNONYMS: dict[str, str] = {
    "directing":    "director",
    "direction":    "director",
    "writing":      "screenplay",
    "music":        "score",
    "song":         "score",
    "leading":      "",          # "actor in a leading role" → "actor  role"
    "supporting":   "supporting",
    "feature":      "",          # "documentary feature film" → "documentary  film"
    "animated":     "animated",
    "international": "international",
    "foreign":      "international",
    "documentary":  "documentary",
    "adapted":      "adapted",
    "original":     "original",
    "cinematography": "cinematography",
    "editing":      "editing",
    "production":   "production",
    "sound":        "sound",
    "picture":      "picture",
}


def _normalise_for_match(text: str) -> str:
    """
    Normalise an award category label for fuzzy matching:
    lowercase → remove parens → apply synonym map → collapse spaces.
    """
    t = _normalize_cat(strip_wiki_markup(text))
    # Remove parenthetical qualifiers: (original screenplay) → original screenplay
    t = re.sub(r"[()]", " ", t)
    # Apply synonym substitutions
    words = t.split()
    words = [_CAT_SYNONYMS.get(w, w) for w in words]
    # Remove empty strings from synonym removal
    words = [w for w in words if w]
    return " ".join(words)


def _cat_matches(candidate: str, target: str) -> bool:
    """
    True if `candidate` (from wikitext) matches `target` (our award display name).
    Handles reworded matches like 'Best Directing' == 'Best Director'.

    Deliberately avoids false positives like:
      'Short Film Palme d'Or' matching 'Palme d'Or'
      'Un Certain Regard Best Director' matching 'Best Director'
      'Special Jury Prize' matching 'Jury Prize'
    """
    # ── Exact check ──────────────────────────────────────────────────────────
    c_raw = _normalize_cat(strip_wiki_markup(candidate))
    t_raw = _normalize_cat(target)
    if c_raw == t_raw:
        return True

    # ── Substring match with qualifier guard ─────────────────────────────────
    # Words that, when they prefix a longer string, make it a DIFFERENT award
    _QUALIFIERS = {"short", "special", "honorary", "silver", "golden",
                   "critics", "independent", "student", "cinéfondation",
                   "queer", "parallel",
                   # Cannes section names
                   "un", "certain", "regard",
                   # Festival name prefixes that scope an award to a sub-section
                   "cannes", "berlin", "venice", "sundance", "bafta"}

    def _no_new_qualifier(longer: str, shorter: str) -> bool:
        """True if `longer` has no extra qualifier words not in `shorter`."""
        extra_words = set(longer.split()) - set(shorter.split())
        return not any(w in _QUALIFIERS for w in extra_words)

    c_wc = len(c_raw.split())
    t_wc = len(t_raw.split())
    if abs(c_wc - t_wc) <= 1:
        if t_raw in c_raw:
            longer, shorter = c_raw, t_raw
            if _no_new_qualifier(longer, shorter):
                return True
        elif c_raw in t_raw:
            longer, shorter = t_raw, c_raw
            if _no_new_qualifier(longer, shorter):
                return True

    # ── Normalised synonym check ──────────────────────────────────────────────
    c = _normalise_for_match(candidate)
    t = _normalise_for_match(target)
    if c == t:
        return True
    c_nwc = len(c.split())
    t_nwc = len(t.split())
    if abs(c_nwc - t_nwc) <= 1:
        if t in c:
            longer, shorter = c, t
            if _no_new_qualifier(longer, shorter):
                return True
        elif c in t:
            longer, shorter = t, c
            if _no_new_qualifier(longer, shorter):
                return True

    # ── Keyword overlap on normalised forms ───────────────────────────────────
    stopwords = {"for", "the", "a", "an", "best", "award", "prize", "de", "du",
                 "d", "and", "&", "of", "in", "role"}
    c_words = {w for w in c.split() if w not in stopwords and len(w) > 2}
    t_words = {w for w in t.split() if w not in stopwords and len(w) > 2}
    if t_words and c_words:
        overlap = t_words & c_words
        shorter = t_words if len(t_words) <= len(c_words) else c_words
        longer  = c_words if len(t_words) <= len(c_words) else t_words
        if len(shorter) >= 1 and overlap >= shorter:
            # Reject if the longer set has qualifier words not in the shorter
            extra = longer - shorter
            if not any(w in _QUALIFIERS for w in extra):
                return True
    return False


def _extract_film_from_line(line: str) -> Optional[str]:
    """
    Given a single bullet / table line, return the film title (wikilink target)
    or None. Prefers italic [[wikilinks]] which Wikipedia uses for film titles.

    Handles the Oscar/BAFTA winner format:
      * '''[[Person Name]] – ''[[Film (film)|Film]]'' ‡'''
    where the film is the italic wikilink INSIDE the bold block, after the dash.
    """
    # Priority 0: Oscar-style "Person – ''[[Film]]''" pattern
    # Match: anything – ''[[FilmLink]]''  (the film is always after the em-dash/hyphen)
    _PERSON_DASH_FILM_RE = re.compile(
        r"(?:\[\[[^\]]+\]\]|[^[{'\n]+?)\s*[–—-]\s*''(\[\[[^\]|]+(?:\|[^\]]+)?\]\])''"
    )
    for m in _PERSON_DASH_FILM_RE.finditer(line):
        inner = m.group(1)  # ''[[...]]''
        # Extract link target from [[Target|Display]] or [[Target]]
        link_m = re.match(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", inner)
        if link_m:
            cleaned = _clean_film_title(link_m.group(1))
            if cleaned:
                return cleaned

    # Priority 1: italic *wikilink* only — ''[[Film]]'' or ''[[Target|Display]]''
    # (uses a dedicated wikilink-specific regex to avoid matching plain ''bold-italic'')
    _ITALIC_WIKILINK_RE = re.compile(r"''(\[\[[^\]]+\]\])''")
    for m in _ITALIC_WIKILINK_RE.finditer(line):
        inner = m.group(1)  # [[...]]
        link_m = re.match(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", inner)
        if link_m:
            target = _link_target(link_m.group(1))
            if target:
                cleaned = _clean_film_title(target)
                if cleaned:
                    return cleaned

    # Priority 2: any [[wikilink]] that explicitly looks like a film
    for m in re.finditer(r"\[\[([^\]]+)\]\]", line):
        target = _link_target(m.group(1))
        if not target:
            continue
        # Film links often have "(film)" or year suffix
        if re.search(r"\(.*film.*\)|\(\d{4}", target, re.IGNORECASE):
            cleaned = _clean_film_title(target)
            if cleaned:
                return cleaned

    # Priority 3: italic plain text ''Title'' (no wikilink)
    # Only match AFTER a ':' or '–' separator to avoid matching award-name bold text
    _PLAIN_ITALIC_RE = re.compile(r"[:\–—]\s*''([^'\[\n]{2,80})''")
    for m in _PLAIN_ITALIC_RE.finditer(line):
        t = m.group(1).strip()
        if t and not t.endswith(("–", "—", "-", "‡")):
            return t

    return None


def parse_award_section(wikitext: str, award_name: str) -> list[dict]:
    """
    Extract winner and nominees for a specific award from the full page wikitext.

    Returns list of:
      {"title": str, "result": "win"|"nomination", "persons": []}

    Handles three major Wikipedia formats:
    A) Festival bullet lists  (* [[AwardName]]: ''[[Film]]'' by [[Director]])
    B) Oscar/BAFTA wikitables ({{Award category|...|[[Category]]}}, * '''winner''', ** nominees)
    C) Older simple tables   ({| wikitable ... |})
    """
    results: list[dict] = []
    seen_titles: set[str] = set()

    def add(title: str, result: str) -> None:
        title = title.strip()
        if not title or title in seen_titles or len(title) < 2 or len(title) > 120:
            return
        # Skip obvious non-films: award names, festival section titles, single words
        if re.match(
            r"^(Palme|Golden|Silver|Grand|Jury|Honorary|Special|Best|Award|Prize"
            r"|Camera|Caméra|Bear|Lion|Leopard|Shell|Astor|César|Goya|Ariel"
            r"|BAFTA|Oscar|Academy|Un Certain Regard|Cinéfondation|Queer Palm"
            r"|Critics|Directors|Cannes|Berlin|Venice|Sundance)\b",
            title, re.IGNORECASE
        ):
            return
        # Skip titles that contain "Prize" / "Award" / "Jury" — these are award names
        if re.search(r"\b(Prize|Award|Jury Prize|Palm|Palme)\b", title, re.IGNORECASE):
            return
        seen_titles.add(title)
        results.append({"title": title, "result": result, "persons": []})

    # ══════════════════════════════════════════════════════════════════════════
    # FORMAT B: Oscar/BAFTA wikitable
    # Detect: {{Award category|...|[[Best Picture]]}} inside a wikitable
    # Winner: * '''[[Film]]'''  (bold, depth-1 bullet)
    # Nominee: ** [[Film]]      (depth-2 bullet)
    # ══════════════════════════════════════════════════════════════════════════
    if "{{Award category" in wikitext or "{{award category" in wikitext:
        # Split the wikitext into "cells" separated by {{Award category...}} headers
        cat_positions = [(m.start(), m.group(1), m.group(2)) for m in _AWARD_CAT_RE.finditer(wikitext)]

        for idx, (pos, link_target_raw, link_display) in enumerate(cat_positions):
            cat_label = link_display or link_target_raw  # prefer display text
            if not _cat_matches(cat_label, award_name):
                continue

            # Grab the cell content: from this position to the next category header
            next_pos = cat_positions[idx + 1][0] if idx + 1 < len(cat_positions) else len(wikitext)
            cell_text = wikitext[pos:next_pos]

            # Parse bullet lines in this cell
            for line in cell_text.splitlines():
                line = line.strip()
                if not line.startswith("*"):
                    continue
                depth = len(line) - len(line.lstrip("*"))
                film = _extract_film_from_line(line)
                if film:
                    result_type = "win" if depth == 1 else "nomination"
                    add(film, result_type)

            if results:
                return results

    # ══════════════════════════════════════════════════════════════════════════
    # FORMAT A: Festival bullet lists (Cannes, Berlin, Venice, etc.)
    # Pattern: * [[AwardName]]: ''[[Film]]'' by [[Director]]
    # or:      * '''AwardName''': ''[[Film]]'' by [[Director]]
    # Awards section is often a flat list of bullet points, one award per line.
    # ══════════════════════════════════════════════════════════════════════════

    # Find the "Official awards" / "Awards" section — must be a real section header,
    # not the infobox (which uses | key = value syntax and appears before ==Sections==)
    awards_section_re = re.compile(
        r"==+\s*(?:Official\s+)?[Aa]wards?\s*==+|"
        r"==+\s*[Pp]rizes?\s*==+|"
        r"==+\s*[Ww]inners?\s+(?:and\s+)?(?:[Nn]ominees?)?\s*==+",
        re.IGNORECASE,
    )
    section_start = None
    for m in awards_section_re.finditer(wikitext):
        section_start = m.start()
        break  # take first match only
    # Fall back to first == section (skip infobox at start of page)
    if section_start is None:
        first_section = re.search(r"^==[^=]", wikitext, re.MULTILINE)
        section_start = first_section.start() if first_section else len(wikitext)
    # Go to end of wikitext or next top-level == section after this one
    section_end = len(wikitext)
    for m2 in re.finditer(r"^==\s*[^=]", wikitext[section_start + 10:], re.MULTILINE):
        section_end = section_start + 10 + m2.start()
        break
    awards_text = wikitext[section_start:section_end]

    # Scan every bullet line in the awards section
    for line in awards_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("*"):
            continue

        # Extract just the award label portion of the line (before ':' or '–')
        # to match against award_name — avoids false positives from person/film names
        label_part = stripped
        # The award label is the [[wikilink|display]] or '''bold''' text at the start
        # Extract display text of the first wikilink on the line
        first_link = re.match(r"^\*+\s*(?:'{2,3})?\[\[([^\]]+)\]\]", stripped)
        if first_link:
            inner = first_link.group(1)
            # Use display text if piped, else the target
            label_part = inner.split("|")[-1]
        else:
            # Fall back to text before the first ':' 
            colon_idx = stripped.find(":")
            if colon_idx > 0:
                label_part = stripped[:colon_idx]
            # Strip leading '* and whitespace
            label_part = label_part.lstrip("*' \t")

        # Does this label match our award?
        if not _cat_matches(label_part, award_name):
            continue

        # This line is about our award — extract the film
        film = _extract_film_from_line(stripped)
        if film:
            add(film, "win")

    # ══════════════════════════════════════════════════════════════════════════
    # FORMAT C: Per-award sub-sections (common for newer Cannes/Venice pages)
    # ==Awards==
    # ===In Competition===
    # * [[Palme d'Or]]: ''[[Film]]''
    # ══════════════════════════════════════════════════════════════════════════
    if not results:
        # Find any sub-section whose header matches the award name
        section_re = re.compile(r"^={2,4}\s*(.+?)\s*={2,4}", re.MULTILINE)
        all_sections = list(section_re.finditer(wikitext))
        for i, sec in enumerate(all_sections):
            heading_plain = strip_wiki_markup(sec.group(1))
            if not _cat_matches(heading_plain, award_name):
                continue
            sec_start = sec.end()
            sec_end = all_sections[i + 1].start() if i + 1 < len(all_sections) else len(wikitext)
            sec_text = wikitext[sec_start:sec_end]
            for line in sec_text.splitlines():
                stripped = line.strip()
                if not stripped.startswith("*"):
                    continue
                depth = len(stripped) - len(stripped.lstrip("*"))
                film = _extract_film_from_line(stripped)
                if film:
                    add(film, "win" if depth == 1 else "nomination")
            if results:
                return results

    # ══════════════════════════════════════════════════════════════════════════
    # FORMAT D: Old-style wikitables ({| wikitable ... |})
    # Used by older ceremony pages (pre-2000).
    # ══════════════════════════════════════════════════════════════════════════
    if not results:
        table_re = re.compile(r"\{\|.*?\|\}", re.DOTALL)
        for table in table_re.finditer(wikitext):
            table_text = table.group(0)
            if not _cat_matches(table_text, award_name):
                continue
            rows = re.split(r"^\s*\|\-", table_text, flags=re.MULTILINE)
            first = True
            for row in rows:
                film = _extract_film_from_line(row)
                if film:
                    add(film, "win" if first else "nomination")
                    first = False

    # ══════════════════════════════════════════════════════════════════════════
    # FALLBACK: scan the full page for any ''[[Film]]'' near the award name
    # ══════════════════════════════════════════════════════════════════════════
    if not results:
        award_short = re.escape(award_name.split()[-1])  # last keyword
        for m in re.finditer(award_short, wikitext, re.IGNORECASE):
            context = wikitext[max(0, m.start() - 50): m.end() + 400]
            for im in _ITALIC_FILM_RE.finditer(context):
                t = im.group(1) or im.group(2)
                if t:
                    cleaned = _clean_film_title(t.split("|")[0])
                    if cleaned:
                        add(cleaned, "win")
            if results:
                break

    return results


# ─── TMDB search ──────────────────────────────────────────────────────────────

# Title cleanup: remove leading articles for fallback searches
_LEADING_ARTICLES = re.compile(
    r"^(The|A|An|El|La|Los|Las|Le|Les|L'|Der|Die|Das|Il|Lo|Gli|Le|Os|As)\s+",
    re.IGNORECASE,
)


def tmdb_search_by_title(
    title: str,
    year: int,
    cache: dict,
) -> Optional[dict]:
    """
    Search TMDB by title and year, with three fallback strategies.
    Returns {tmdb_id, title, original_title, year} or None.
    Uses in-memory cache keyed by (title_lower, year).
    """
    if not TMDB_KEY:
        return None

    cache_key = (title.lower().strip(), year)
    if cache_key in cache:
        return cache[cache_key]

    def _search(
        query: str,
        search_year: Optional[int],
        max_year_delta: int = 3,
    ) -> Optional[dict]:
        """
        Search TMDB. If max_year_delta is set, reject results whose release year
        differs from `year` (the ceremony year) by more than that amount.
        Pass max_year_delta=999 to disable the guard (Strategy 4 uses a tighter
        explicit check instead).
        """
        params: dict = {
            "api_key":       TMDB_KEY,
            "query":         query,
            "include_adult": False,
            "language":      "en-US",
        }
        if search_year:
            params["year"] = search_year
        backoff = 2.0
        for attempt in range(3):
            try:
                r = requests.get(
                    f"{TMDB_API}/search/movie",
                    params=params,
                    timeout=10,
                )
                if r.status_code == 429:
                    print(f"    [TMDB] 429 — sleeping {backoff:.0f}s")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                r.raise_for_status()
                results = r.json().get("results", [])
                for m in results:
                    yr_str = (m.get("release_date") or "")[:4]
                    yr = int(yr_str) if yr_str.isdigit() else None
                    # Reject results too far from the ceremony year
                    if yr and abs(yr - year) > max_year_delta:
                        continue
                    return {
                        "tmdb_id":        m["id"],
                        "title":          m.get("title") or query,
                        "original_title": m.get("original_title"),
                        "year":           yr,
                    }
                return None
            except Exception as e:
                if attempt == 2:
                    print(f"    [TMDB] Error searching '{query}': {e}")
                time.sleep(backoff)
                backoff *= 2
        return None

    # Strategy 1: exact title + ceremony year (±0)
    result = _search(title, year, max_year_delta=1)
    time.sleep(TMDB_SLEEP)

    # Strategy 2: title without leading article + ceremony year
    if not result:
        stripped = _LEADING_ARTICLES.sub("", title).strip()
        if stripped != title and stripped:
            result = _search(stripped, year, max_year_delta=1)
            time.sleep(TMDB_SLEEP)

    # Strategy 3: title + year ± 2 (wider window, no TMDB year filter)
    if not result:
        result = _search(title, None, max_year_delta=2)
        time.sleep(TMDB_SLEEP)

    # Strategy 4: first 3 words (loose match), still year-guarded
    if not result:
        words = title.split()
        if len(words) >= 3:
            short = " ".join(words[:3])
            result = _search(short, None, max_year_delta=2)
            time.sleep(TMDB_SLEEP)

    cache[cache_key] = result
    return result


# ─── Checkpoint helpers ───────────────────────────────────────────────────────

def load_checkpoint(festival_key: str) -> dict:
    path = CHECKPOINT_DIR / f"{festival_key}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"last_year": None, "total_found": 0, "total_inserted": 0, "gaps": []}


def save_checkpoint(festival_key: str, data: dict) -> None:
    path = CHECKPOINT_DIR / f"{festival_key}.json"
    path.write_text(json.dumps(data, indent=2))


# ─── Score computation ────────────────────────────────────────────────────────

def compute_score(
    festival_key: str,
    award_id: str,          # e.g. "award_cannes-palme-dor"
    result: str,            # "win" | "nomination"
    scoring_map: dict,
) -> float:
    """Compute PRISMA score contribution for one award result."""
    pts        = scoring_map.get(award_id) or scoring_map.get(award_id.removeprefix("award_")) or 0
    fest_key   = festival_key.replace("_", "-")  # san_sebastian → san-sebastian
    fest_w     = FESTIVAL_TIER_WEIGHT.get(fest_key, DEFAULT_FESTIVAL_WEIGHT)
    cat_key    = award_id.removeprefix("award_")  # e.g. "cannes-palme-dor"
    cat_mult   = CATEGORY_FILM_MULTIPLIER.get(cat_key, DEFAULT_CATEGORY_MULTIPLIER)
    if cat_mult == 0.0:
        return 0.0
    base = pts * fest_w * cat_mult
    return base if result == "win" else base * 0.4


# ─── Core scraper: one festival year ─────────────────────────────────────────

def scrape_festival_year(
    festival_key: str,
    year: int,
    db,
    scoring_map: dict,
    dry_run: bool = False,
    tmdb_cache: dict = None,
) -> dict:
    """
    Scrape one ceremony year for a festival.
    Returns stats dict: {found, resolved, inserted, updated, skipped, gap}
    """
    if tmdb_cache is None:
        tmdb_cache = {}

    cfg         = FESTIVAL_PAGES[festival_key]
    page_title  = build_page_title(festival_key, year)
    award_map   = cfg["awards"]  # display_name → award_id

    print(f"  [{year}] {page_title}")

    wikitext = get_wikipedia_wikitext(page_title)
    time.sleep(WIKIPEDIA_SLEEP)

    # Try fallback titles if primary not found
    if wikitext is None:
        for alt_title in _fallback_titles(festival_key, year):
            print(f"    → trying fallback: {alt_title!r}")
            wikitext = get_wikipedia_wikitext(alt_title)
            time.sleep(WIKIPEDIA_SLEEP)
            if wikitext is not None:
                print(f"    ✓ Found via fallback")
                break

    if wikitext is None:
        print(f"    ✗ Page not found — gap")
        return {"found": 0, "resolved": 0, "inserted": 0, "updated": 0, "skipped": 0, "gap": True}

    # Accumulate per-film data across all award categories
    film_data: dict[str, dict] = {}  # title_lower → {...}
    seen_award_ids: set[str] = set()  # prevent double-counting when aliases share an award_id

    for award_display, award_id in award_map.items():
        entries = parse_award_section(wikitext, award_display)
        if not entries:
            continue
        # Skip this alias if we already processed a different alias for the same award_id
        # (prevents double-counting when e.g. "Camera d'Or" and "Caméra d'Or" both succeed)
        if award_id in seen_award_ids:
            continue
        seen_award_ids.add(award_id)

        pts_base = scoring_map.get(award_id) or scoring_map.get(award_id.removeprefix("award_")) or 0

        for entry in entries:
            raw_title = entry["title"]
            result    = entry["result"]  # "win" | "nomination"

            score_contrib = compute_score(festival_key, award_id, result, scoring_map)

            key = raw_title.lower().strip()
            if key not in film_data:
                film_data[key] = {
                    "raw_title":    raw_title,
                    "year":         year,
                    "prisma_score": 0.0,
                    "win_count":    0,
                    "nom_count":    0,
                    "awards":       [],
                }
            fd = film_data[key]
            fd["prisma_score"] += score_contrib
            if result == "win":
                fd["win_count"] += 1
            else:
                fd["nom_count"] += 1
            fd["awards"].append({
                "award_id":  award_id,
                "result":    result,
                "pts":       pts_base,
                "contrib":   round(score_contrib, 3),
            })

    found = len(film_data)
    print(f"    Films extracted: {found}")

    if found == 0:
        return {"found": 0, "resolved": 0, "inserted": 0, "updated": 0, "skipped": 0, "gap": False}

    # Resolve each film via TMDB
    candidates: list[dict] = []
    resolved   = 0
    skipped    = 0

    for key, fd in film_data.items():
        raw_title = fd["raw_title"]
        tmdb_info = tmdb_search_by_title(raw_title, year, tmdb_cache)

        if not tmdb_info:
            skipped += 1
            continue

        resolved += 1
        candidates.append({
            "tmdb_id":        tmdb_info["tmdb_id"],
            "imdb_id":        None,
            "title":          tmdb_info["title"],
            "original_title": tmdb_info.get("original_title"),
            "year":           tmdb_info.get("year") or year,
            "prisma_score":   round(fd["prisma_score"], 2),
            "award_count":    fd["win_count"] + fd["nom_count"],
            "win_count":      fd["win_count"],
            "nom_count":      fd["nom_count"],
            "awards_json":    fd["awards"],
            "source":         festival_key,
            "status":         "pending",
        })

    print(f"    TMDB resolved: {resolved}/{found}  ({skipped} unresolved)")

    if dry_run:
        if candidates:
            top = sorted(candidates, key=lambda x: -x["prisma_score"])[:5]
            for c in top:
                print(f"    [DRY] {c['prisma_score']:6.1f}  {c['title']} ({c['year']})")
        return {
            "found":    found,
            "resolved": resolved,
            "inserted": len(candidates),
            "updated":  0,
            "skipped":  skipped,
            "gap":      False,
        }

    result = upsert_candidates(db, candidates, dry_run=False)
    return {
        "found":    found,
        "resolved": resolved,
        "inserted": result.get("inserted", 0),
        "updated":  result.get("updated", 0),
        "skipped":  skipped,
        "gap":      False,
    }


# ─── Festival scraper (all years with checkpoint support) ─────────────────────

def scrape_festival(
    festival_key: str,
    from_year: int   = None,
    to_year: int     = None,
    specific_year: int = None,
    db               = None,
    scoring_map: dict = None,
    dry_run: bool    = False,
) -> dict:
    """
    Scrape all (or a range of) years for a festival.
    Supports checkpoint resume.  Saves checkpoint every 5 years.
    """
    cfg = FESTIVAL_PAGES.get(festival_key)
    if not cfg:
        print(f"✗ Unknown festival key: {festival_key}")
        return {}

    checkpoint = load_checkpoint(festival_key)

    if specific_year is not None:
        years_to_scrape = [specific_year]
    else:
        all_years = list(cfg["years"])
        if from_year is not None:
            start = from_year
        elif checkpoint.get("last_year"):
            start = checkpoint["last_year"] + 1
            print(f"  Resuming from checkpoint: year {start} (last done: {checkpoint['last_year']})")
        else:
            start = cfg.get("start_year", all_years[0])

        years_to_scrape = [y for y in all_years if y >= start]
        if to_year is not None:
            years_to_scrape = [y for y in years_to_scrape if y <= to_year]

    if not years_to_scrape:
        print(f"  Nothing to scrape for {festival_key} — checkpoint up to date.")
        return checkpoint

    totals = defaultdict(int)
    gaps: list[int] = list(checkpoint.get("gaps") or [])
    tmdb_cache: dict = {}

    print(f"\n{'═'*60}")
    print(f"  Festival: {festival_key.upper()}  ({len(years_to_scrape)} ceremonies)")
    print(f"{'═'*60}")

    for batch_start in range(0, len(years_to_scrape), 1):
        year = years_to_scrape[batch_start]
        stats = scrape_festival_year(
            festival_key, year, db, scoring_map,
            dry_run=dry_run, tmdb_cache=tmdb_cache,
        )
        for k in ("found", "resolved", "inserted", "updated", "skipped"):
            totals[k] += stats.get(k, 0)
        if stats.get("gap"):
            gaps.append(year)

        # Save checkpoint every 5 years
        if (batch_start + 1) % 5 == 0 and specific_year is None:
            checkpoint.update({
                "last_year":      year,
                "total_found":    checkpoint.get("total_found", 0)    + totals["found"],
                "total_inserted": checkpoint.get("total_inserted", 0) + totals["inserted"],
                "gaps":           gaps,
            })
            if not dry_run:
                save_checkpoint(festival_key, checkpoint)

    # Final checkpoint update
    if specific_year is None:
        last_done = years_to_scrape[-1]
        checkpoint.update({
            "last_year":      last_done,
            "total_found":    checkpoint.get("total_found", 0)    + totals["found"],
            "total_inserted": checkpoint.get("total_inserted", 0) + totals["inserted"],
            "gaps":           gaps,
        })
        if not dry_run:
            save_checkpoint(festival_key, checkpoint)

    # ── Coverage report ───────────────────────────────────────────────────────
    n_years  = len(years_to_scrape)
    found    = totals["found"]
    resolved = totals["resolved"]
    pct      = f"{100 * resolved / found:.1f}%" if found else "n/a"
    gap_str  = (", ".join(str(g) for g in sorted(gaps)[:10])
                + (" ..." if len(gaps) > 10 else "")) if gaps else "none"

    print(f"\n  ─── {festival_key.upper()} SUMMARY ───")
    print(f"  Years scraped    : {years_to_scrape[0]}–{years_to_scrape[-1]} ({n_years} ceremonies)")
    print(f"  Films found      : {found:,}")
    print(f"  TMDB resolved    : {resolved:,} ({pct})")
    if not dry_run:
        print(f"  New candidates   : {totals['inserted']:,}")
        print(f"  Scores updated   : {totals['updated']:,}")
    print(f"  Coverage gaps    : {gap_str}")

    return dict(totals)


# ─── Report ───────────────────────────────────────────────────────────────────

def print_report(db) -> None:
    """Print a coverage report from the candidates table and checkpoint files."""
    print(f"\n{'═'*60}")
    print("  PRISMA — Wikipedia Awards Coverage Report")
    print(f"{'═'*60}\n")

    # Candidates summary
    try:
        r = db.table("candidates").select("status", count="exact").execute()
        total = r.count or 0
        from collections import Counter
        by_status = Counter(x["status"] for x in (r.data or []))
        print(f"  Total candidates: {total:,}")
        for status, cnt in sorted(by_status.items()):
            print(f"    {status:<15} {cnt:,}")
        print()
    except Exception as e:
        print(f"  [DB] Could not query candidates: {e}\n")

    # Per-festival checkpoint summaries
    print(f"  {'Festival':<18} {'Last year':<12} {'Found':<10} {'Inserted':<10} {'Gaps'}")
    print(f"  {'─'*18}  {'─'*10}  {'─'*8}  {'─'*8}  {'─'*20}")
    for festival_key in sorted(FESTIVAL_PAGES.keys()):
        cp = load_checkpoint(festival_key)
        last  = cp.get("last_year") or "—"
        found = cp.get("total_found", 0)
        ins   = cp.get("total_inserted", 0)
        gaps  = cp.get("gaps", [])
        gap_s = f"{len(gaps)} gap(s)" if gaps else "none"
        print(f"  {festival_key:<18}  {str(last):<10}  {found:<8,}  {ins:<8,}  {gap_s}")

    print()

    # Top 10 pending films by score
    try:
        top = (db.table("candidates")
                 .select("title, year, prisma_score, source, status")
                 .eq("status", "pending")
                 .order("prisma_score", desc=True)
                 .limit(10)
                 .execute())
        if top.data:
            print(f"  Top 10 pending by PRISMA score:")
            for x in top.data:
                score = float(x.get("prisma_score") or 0)
                print(f"    {score:8.1f}  {x.get('title', '?')} ({x.get('year', '?')})  [{x.get('source', '?')}]")
    except Exception as e:
        print(f"  [DB] Could not query top pending: {e}")

    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape Wikipedia award pages → candidates table",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--festival", "-f", default=None,
        help="Festival key: cannes, berlin, venice, oscar, bafta, ...")
    parser.add_argument("--all", action="store_true",
        help="Scrape all festivals")
    parser.add_argument("--year", type=int, default=None,
        help="Scrape only this specific year")
    parser.add_argument("--from-year", type=int, default=None,
        help="Start from this year (overrides checkpoint)")
    parser.add_argument("--to-year", type=int, default=None,
        help="Stop at this year (inclusive)")
    parser.add_argument("--dry-run", action="store_true",
        help="Parse and resolve but do NOT write to DB")
    parser.add_argument("--report", action="store_true",
        help="Print coverage report and exit")
    parser.add_argument("--list-festivals", action="store_true",
        help="List all supported festival keys and exit")
    args = parser.parse_args()

    if args.list_festivals:
        print("Supported festival keys:")
        for key in sorted(FESTIVAL_PAGES.keys()):
            cfg = FESTIVAL_PAGES[key]
            years = list(cfg["years"])
            print(f"  {key:<20} {years[0]}–{years[-1]}  ({len(cfg['awards'])} award categories)")
        return

    # Initialise DB + scoring
    try:
        db = create_client(
            os.environ["PUBLIC_SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"],
        )
    except KeyError as e:
        print(f"✗ Missing environment variable: {e}")
        print("  Make sure .env.local contains PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_KEY")
        sys.exit(1)

    if args.report:
        print_report(db)
        return

    scoring_map = get_scoring_map(db)
    print(f"Loaded {len(scoring_map)} scoring entries from awards table")

    if args.all:
        festivals = sorted(FESTIVAL_PAGES.keys())
    elif args.festival:
        if args.festival not in FESTIVAL_PAGES:
            print(f"✗ Unknown festival: {args.festival!r}")
            print(f"  Run --list-festivals to see valid keys.")
            sys.exit(1)
        festivals = [args.festival]
    else:
        parser.print_help()
        sys.exit(0)

    grand_totals: dict[str, int] = defaultdict(int)

    for festival_key in festivals:
        stats = scrape_festival(
            festival_key,
            from_year=args.from_year,
            to_year=args.to_year,
            specific_year=args.year,
            db=db,
            scoring_map=scoring_map,
            dry_run=args.dry_run,
        )
        for k, v in stats.items():
            if isinstance(v, int):
                grand_totals[k] += v

    if len(festivals) > 1:
        print(f"\n{'═'*60}")
        print("  GRAND TOTAL")
        print(f"{'═'*60}")
        for k, v in sorted(grand_totals.items()):
            print(f"  {k:<20} {v:,}")

    if args.dry_run:
        print("\n  [DRY RUN — no changes written to DB]")


if __name__ == "__main__":
    main()
