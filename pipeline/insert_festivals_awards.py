"""
pipeline/insert_festivals_awards.py
─────────────────────────────────────
Run AFTER executing the DDL in Supabase SQL editor:

  1. Go to: https://supabase.com/dashboard/project/porqyokkphflvqfclvkj/sql
  2. Run the SQL in pipeline/create_festivals_schema.sql
  3. Then: python3 pipeline/insert_festivals_awards.py
"""

import os
from dotenv import load_dotenv
load_dotenv('.env.local')
from supabase import create_client

db = create_client(os.environ['PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SERVICE_KEY'])

# ─── Step 2: Insert 35 festivals ─────────────────────────────────────────────

festivals = [
  # TIER A — Grand international festivals
  {'id': 'festival_academy-awards', 'name': 'Academy Awards', 'name_local': 'Oscar', 'country': 'US', 'city': 'Los Angeles', 'founded_year': 1929, 'tier': 'A', 'wikidata_id': 'Q19020', 'website': 'https://www.oscars.org', 'description': 'The most prestigious film awards in the world, presented annually by the Academy of Motion Picture Arts and Sciences.'},
  {'id': 'festival_cannes', 'name': 'Cannes Film Festival', 'name_local': 'Festival de Cannes', 'country': 'FR', 'city': 'Cannes', 'founded_year': 1946, 'tier': 'A', 'wikidata_id': 'Q180551', 'website': 'https://www.festival-cannes.com', 'description': "The world's most prestigious film festival, awarding the Palme d'Or to the best feature film."},
  {'id': 'festival_berlin', 'name': 'Berlin International Film Festival', 'name_local': 'Berlinale', 'country': 'DE', 'city': 'Berlin', 'founded_year': 1951, 'tier': 'A', 'wikidata_id': 'Q193565', 'website': 'https://www.berlinale.de', 'description': "One of the world's leading film festivals, awarding the Golden Bear to the best film."},
  {'id': 'festival_venice', 'name': 'Venice Film Festival', 'name_local': "Mostra Internazionale d'Arte Cinematografica", 'country': 'IT', 'city': 'Venice', 'founded_year': 1932, 'tier': 'A', 'wikidata_id': 'Q219521', 'website': 'https://www.labiennale.org/en/cinema', 'description': "The world's oldest film festival, awarding the Golden Lion to the best film."},
  {'id': 'festival_bafta', 'name': 'BAFTA Film Awards', 'name_local': 'BAFTA', 'country': 'GB', 'city': 'London', 'founded_year': 1948, 'tier': 'A', 'wikidata_id': 'Q637179', 'website': 'https://www.bafta.org', 'description': 'The British Academy of Film and Television Arts awards, considered the British equivalent of the Oscars.'},
  {'id': 'festival_toronto', 'name': 'Toronto International Film Festival', 'name_local': 'TIFF', 'country': 'CA', 'city': 'Toronto', 'founded_year': 1976, 'tier': 'A', 'wikidata_id': 'Q110063', 'website': 'https://www.tiff.net', 'description': 'One of the most influential film festivals in the world, often a launching pad for Oscar contenders.'},
  {'id': 'festival_sundance', 'name': 'Sundance Film Festival', 'country': 'US', 'city': 'Park City', 'founded_year': 1978, 'tier': 'A', 'wikidata_id': 'Q210656', 'website': 'https://www.sundance.org/festivals/sundance-film-festival', 'description': 'The premier American independent film festival, founded by Robert Redford.'},

  # TIER B — Major auteur festivals
  {'id': 'festival_locarno', 'name': 'Locarno Film Festival', 'name_local': 'Festival del film Locarno', 'country': 'CH', 'city': 'Locarno', 'founded_year': 1946, 'tier': 'B', 'wikidata_id': 'Q271818', 'website': 'https://www.locarnofestival.ch', 'description': 'One of the oldest film festivals in the world, known for its dedication to auteur and independent cinema.'},
  {'id': 'festival_san-sebastian', 'name': 'San Sebastián International Film Festival', 'name_local': 'Festival Internacional de Cine de San Sebastián', 'country': 'ES', 'city': 'San Sebastián', 'founded_year': 1953, 'tier': 'B', 'wikidata_id': 'Q1353192', 'website': 'https://www.sansebastianfestival.com', 'description': 'The most important film festival in Spain, awarding the Golden Shell to the best film.'},
  {'id': 'festival_rotterdam', 'name': 'International Film Festival Rotterdam', 'name_local': 'IFFR', 'country': 'NL', 'city': 'Rotterdam', 'founded_year': 1972, 'tier': 'B', 'wikidata_id': 'Q841150', 'website': 'https://iffr.com', 'description': "One of the world's largest public film festivals, known for its focus on innovative and independent cinema."},
  {'id': 'festival_new-york', 'name': 'New York Film Festival', 'name_local': 'NYFF', 'country': 'US', 'city': 'New York', 'founded_year': 1963, 'tier': 'B', 'wikidata_id': 'Q1135762', 'website': 'https://www.filmlinc.org/nyff', 'description': 'A prestigious non-competitive festival presented by the Film Society of Lincoln Center.'},
  {'id': 'festival_telluride', 'name': 'Telluride Film Festival', 'country': 'US', 'city': 'Telluride', 'founded_year': 1974, 'tier': 'B', 'wikidata_id': 'Q1361235', 'website': 'https://telluridefilmfestival.org', 'description': 'An intimate, curated festival known for world premieres of major awards contenders.'},
  {'id': 'festival_mar-del-plata', 'name': 'Mar del Plata International Film Festival', 'name_local': 'Festival Internacional de Cine de Mar del Plata', 'country': 'AR', 'city': 'Mar del Plata', 'founded_year': 1954, 'tier': 'B', 'wikidata_id': 'Q1379239', 'website': 'https://www.mardelplatafilmfest.com', 'description': 'The oldest and most prestigious film festival in Latin America, Category A recognized by FIAPF.'},
  {'id': 'festival_tribeca', 'name': 'Tribeca Film Festival', 'country': 'US', 'city': 'New York', 'founded_year': 2002, 'tier': 'B', 'wikidata_id': 'Q1362735', 'website': 'https://tribecafilm.com/festival', 'description': 'Founded by Robert De Niro after 9/11, one of the most important independent film festivals in the US.'},

  # TIER B — Latin America
  {'id': 'festival_morelia', 'name': 'Morelia International Film Festival', 'name_local': 'Festival Internacional de Cine de Morelia', 'country': 'MX', 'city': 'Morelia', 'founded_year': 2003, 'tier': 'B', 'wikidata_id': 'Q1352418', 'website': 'https://moreliafilmfest.com', 'description': 'The most important film festival in Mexico, focused on Mexican and Ibero-American cinema.'},
  {'id': 'festival_guadalajara', 'name': 'Guadalajara International Film Festival', 'name_local': 'Festival Internacional de Cine de Guadalajara', 'country': 'MX', 'city': 'Guadalajara', 'founded_year': 1986, 'tier': 'B', 'wikidata_id': 'Q1141310', 'website': 'https://www.ficg.mx', 'description': 'The largest Ibero-American film festival, a key platform for Spanish and Portuguese language cinema.'},
  {'id': 'festival_bafici', 'name': 'Buenos Aires International Festival of Independent Cinema', 'name_local': 'BAFICI', 'country': 'AR', 'city': 'Buenos Aires', 'founded_year': 1999, 'tier': 'B', 'wikidata_id': 'Q4836838', 'website': 'https://festivales.buenosaires.gob.ar/bafici', 'description': 'The most important independent film festival in Latin America, focused on auteur and experimental cinema.'},
  {'id': 'festival_lima', 'name': 'Lima Film Festival', 'name_local': 'Festival de Cine de Lima', 'country': 'PE', 'city': 'Lima', 'founded_year': 1997, 'tier': 'C', 'website': 'https://festivaldelima.com', 'description': 'The most important film festival in Peru, focused on Ibero-American cinema.'},
  {'id': 'festival_cartagena', 'name': 'Cartagena International Film Festival', 'name_local': 'Festival Internacional de Cine de Cartagena', 'country': 'CO', 'city': 'Cartagena', 'founded_year': 1960, 'tier': 'C', 'wikidata_id': 'Q2510271', 'website': 'https://www.ficcifestival.com', 'description': 'The oldest film festival in Latin America and one of the oldest in the world.'},
  {'id': 'festival_valdivia', 'name': 'Valdivia International Film Festival', 'name_local': 'Festival Internacional de Cine de Valdivia', 'country': 'CL', 'city': 'Valdivia', 'founded_year': 1993, 'tier': 'C', 'website': 'https://www.ficvaldivia.cl', 'description': 'The most important film festival in Chile, known for its focus on independent and auteur cinema.'},

  # TIER B — National awards
  {'id': 'festival_cesar', 'name': 'César Awards', 'name_local': 'Les César du Cinéma', 'country': 'FR', 'city': 'Paris', 'founded_year': 1976, 'tier': 'B', 'wikidata_id': 'Q191067', 'website': 'https://www.academiedesarts-et-techniques-du-cinema.fr', 'description': 'The most prestigious French film awards, considered the French equivalent of the Oscars.'},
  {'id': 'festival_goya', 'name': 'Goya Awards', 'name_local': 'Premios Goya', 'country': 'ES', 'city': 'Madrid', 'founded_year': 1987, 'tier': 'B', 'wikidata_id': 'Q192756', 'website': 'https://www.academiadecine.com', 'description': 'The most prestigious Spanish film awards, presented by the Spanish Film Academy.'},
  {'id': 'festival_ariel', 'name': 'Ariel Awards', 'name_local': 'Premios Ariel', 'country': 'MX', 'city': 'Mexico City', 'founded_year': 1946, 'tier': 'B', 'wikidata_id': 'Q1142242', 'website': 'https://www.academiadecine.org.mx', 'description': 'The most prestigious Mexican film awards, presented by the Mexican Academy of Cinematographic Arts and Sciences.'},

  # TIER C — Specialized and regional
  {'id': 'festival_david-di-donatello', 'name': 'David di Donatello Awards', 'country': 'IT', 'city': 'Rome', 'founded_year': 1956, 'tier': 'C', 'wikidata_id': 'Q1192655', 'website': 'https://www.daviddidonatello.it', 'description': 'The most prestigious Italian film awards.'},
  {'id': 'festival_japanese-academy', 'name': 'Japan Academy Film Prize', 'name_local': '日本アカデミー賞', 'country': 'JP', 'city': 'Tokyo', 'founded_year': 1978, 'tier': 'C', 'wikidata_id': 'Q609911', 'website': 'https://www.japan-academy-prize.jp', 'description': 'The most prestigious film awards in Japan.'},
  {'id': 'festival_korean-film-awards', 'name': 'Grand Bell Awards', 'name_local': '대종상 영화제', 'country': 'KR', 'city': 'Seoul', 'founded_year': 1962, 'tier': 'C', 'wikidata_id': 'Q726903', 'description': 'The most prestigious film awards in South Korea.'},
  {'id': 'festival_bodil', 'name': 'Bodil Awards', 'name_local': 'Bodil', 'country': 'DK', 'city': 'Copenhagen', 'founded_year': 1948, 'tier': 'C', 'wikidata_id': 'Q1768103', 'description': 'The oldest and most prestigious film awards in Denmark.'},
  {'id': 'festival_golden-globe', 'name': 'Golden Globe Awards', 'country': 'US', 'city': 'Beverly Hills', 'founded_year': 1944, 'tier': 'B', 'wikidata_id': 'Q106291', 'website': 'https://goldenglobes.com', 'description': 'Awarded by the Hollywood Foreign Press Association, considered a major awards season bellwether.'},
  {'id': 'festival_spirit-awards', 'name': 'Film Independent Spirit Awards', 'country': 'US', 'city': 'Los Angeles', 'founded_year': 1986, 'tier': 'C', 'wikidata_id': 'Q1399530', 'website': 'https://www.filmindependent.org/spirit-awards', 'description': 'Celebrates the best in American independent film.'},
  {'id': 'festival_sitges', 'name': 'Sitges Film Festival', 'name_local': 'Festival Internacional de Cinema Fantàstic de Catalunya', 'country': 'ES', 'city': 'Sitges', 'founded_year': 1968, 'tier': 'C', 'wikidata_id': 'Q1143116', 'website': 'https://www.sitgesfilmfestival.com', 'description': 'The most important genre film festival in the world.'},
  {'id': 'festival_sxsw', 'name': 'SXSW Film Festival', 'country': 'US', 'city': 'Austin', 'founded_year': 1987, 'tier': 'C', 'wikidata_id': 'Q1143147', 'website': 'https://www.sxsw.com/film', 'description': 'Part of the larger South by Southwest festival, a key platform for emerging filmmakers.'},
  {'id': 'festival_hot-docs', 'name': 'Hot Docs Canadian International Documentary Festival', 'country': 'CA', 'city': 'Toronto', 'founded_year': 1993, 'tier': 'C', 'wikidata_id': 'Q1143148', 'website': 'https://hotdocs.ca', 'description': "North America's largest documentary festival."},
  {'id': 'festival_idfa', 'name': 'International Documentary Film Festival Amsterdam', 'name_local': 'IDFA', 'country': 'NL', 'city': 'Amsterdam', 'founded_year': 1988, 'tier': 'C', 'wikidata_id': 'Q1068518', 'website': 'https://www.idfa.nl', 'description': "The world's largest documentary film festival."},
  {'id': 'festival_fipresci', 'name': 'FIPRESCI Prize', 'country': 'DE', 'city': 'Munich', 'founded_year': 1930, 'tier': 'C', 'wikidata_id': 'Q651176', 'website': 'https://www.fipresci.org', 'description': 'International Federation of Film Critics award, given at major festivals worldwide.'},
]

print('=== INSERTING FESTIVALS ===')
ok = fail = 0
for f in festivals:
    try:
        db.table('festivals').upsert(f, on_conflict='id').execute()
        print(f'  OK  [{f["tier"]}] {f["name"]}')
        ok += 1
    except Exception as e:
        print(f'  FAIL {f["name"]}: {e}')
        fail += 1
print(f'Festivals: {ok} OK, {fail} FAIL\n')

# ─── Step 3: Upsert awards with festival_id links ────────────────────────────

awards = [
  # Cannes
  {'id': 'award_cannes-palme-dor', 'name': "Palme d'Or", 'organization': 'Festival de Cannes', 'festival_id': 'festival_cannes', 'type': 'festival', 'tier': 'A', 'country': 'FR', 'is_grand_prize': True, 'scoring_points': 100},
  {'id': 'award_cannes-grand-prix', 'name': 'Grand Prix', 'organization': 'Festival de Cannes', 'festival_id': 'festival_cannes', 'type': 'festival', 'tier': 'A', 'country': 'FR', 'scoring_points': 70},
  {'id': 'award_cannes-jury-prize', 'name': 'Jury Prize', 'organization': 'Festival de Cannes', 'festival_id': 'festival_cannes', 'type': 'festival', 'tier': 'A', 'country': 'FR', 'scoring_points': 55},
  {'id': 'award_cannes-best-director', 'name': 'Best Director', 'organization': 'Festival de Cannes', 'festival_id': 'festival_cannes', 'type': 'festival', 'tier': 'A', 'country': 'FR', 'scoring_points': 60},
  {'id': 'award_cannes-camera-dor', 'name': "Caméra d'Or", 'organization': 'Festival de Cannes', 'festival_id': 'festival_cannes', 'type': 'festival', 'tier': 'B', 'country': 'FR', 'scoring_points': 40},
  # Berlin
  {'id': 'award_berlin-golden-bear', 'name': 'Golden Bear', 'organization': 'Berlinale', 'festival_id': 'festival_berlin', 'type': 'festival', 'tier': 'A', 'country': 'DE', 'is_grand_prize': True, 'scoring_points': 100},
  {'id': 'award_berlin-silver-bear-director', 'name': 'Silver Bear for Best Director', 'organization': 'Berlinale', 'festival_id': 'festival_berlin', 'type': 'festival', 'tier': 'A', 'country': 'DE', 'scoring_points': 60},
  {'id': 'award_berlin-silver-bear-jury', 'name': 'Silver Bear Grand Jury Prize', 'organization': 'Berlinale', 'festival_id': 'festival_berlin', 'type': 'festival', 'tier': 'A', 'country': 'DE', 'scoring_points': 70},
  # Venice
  {'id': 'award_venice-golden-lion', 'name': 'Golden Lion', 'organization': 'Venice Film Festival', 'festival_id': 'festival_venice', 'type': 'festival', 'tier': 'A', 'country': 'IT', 'is_grand_prize': True, 'scoring_points': 100},
  {'id': 'award_venice-silver-lion-director', 'name': 'Silver Lion for Best Director', 'organization': 'Venice Film Festival', 'festival_id': 'festival_venice', 'type': 'festival', 'tier': 'A', 'country': 'IT', 'scoring_points': 60},
  {'id': 'award_venice-grand-jury', 'name': 'Grand Jury Prize', 'organization': 'Venice Film Festival', 'festival_id': 'festival_venice', 'type': 'festival', 'tier': 'A', 'country': 'IT', 'scoring_points': 70},
  # Oscar
  {'id': 'award_oscar-best-picture', 'name': 'Best Picture', 'organization': 'Academy of Motion Picture Arts and Sciences', 'festival_id': 'festival_academy-awards', 'type': 'academy', 'tier': 'A', 'country': 'US', 'is_grand_prize': True, 'scoring_points': 100},
  {'id': 'award_oscar-best-director', 'name': 'Best Director', 'organization': 'Academy of Motion Picture Arts and Sciences', 'festival_id': 'festival_academy-awards', 'type': 'academy', 'tier': 'A', 'country': 'US', 'scoring_points': 70},
  {'id': 'award_oscar-best-intl-film', 'name': 'Best International Feature Film', 'organization': 'Academy of Motion Picture Arts and Sciences', 'festival_id': 'festival_academy-awards', 'type': 'academy', 'tier': 'A', 'country': 'US', 'scoring_points': 80},
  {'id': 'award_oscar-best-cinematography', 'name': 'Best Cinematography', 'organization': 'Academy of Motion Picture Arts and Sciences', 'festival_id': 'festival_academy-awards', 'type': 'academy', 'tier': 'A', 'country': 'US', 'scoring_points': 55},
  {'id': 'award_oscar-best-actress', 'name': 'Best Actress', 'organization': 'Academy of Motion Picture Arts and Sciences', 'festival_id': 'festival_academy-awards', 'type': 'academy', 'tier': 'A', 'country': 'US', 'scoring_points': 60},
  {'id': 'award_oscar-best-actor', 'name': 'Best Actor', 'organization': 'Academy of Motion Picture Arts and Sciences', 'festival_id': 'festival_academy-awards', 'type': 'academy', 'tier': 'A', 'country': 'US', 'scoring_points': 60},
  # BAFTA
  {'id': 'award_bafta-best-film', 'name': 'Best Film', 'organization': 'BAFTA', 'festival_id': 'festival_bafta', 'type': 'academy', 'tier': 'A', 'country': 'GB', 'is_grand_prize': True, 'scoring_points': 70},
  {'id': 'award_bafta-best-director', 'name': 'Best Director', 'organization': 'BAFTA', 'festival_id': 'festival_bafta', 'type': 'academy', 'tier': 'A', 'country': 'GB', 'scoring_points': 50},
  # Golden Globe
  {'id': 'award_gg-best-film-drama', 'name': 'Best Motion Picture — Drama', 'organization': 'Hollywood Foreign Press Association', 'festival_id': 'festival_golden-globe', 'type': 'academy', 'tier': 'B', 'country': 'US', 'scoring_points': 50},
  {'id': 'award_gg-best-director', 'name': 'Best Director', 'organization': 'Hollywood Foreign Press Association', 'festival_id': 'festival_golden-globe', 'type': 'academy', 'tier': 'B', 'country': 'US', 'scoring_points': 35},
  {'id': 'award_gg-best-intl-film', 'name': 'Best Non-English Language Film', 'organization': 'Hollywood Foreign Press Association', 'festival_id': 'festival_golden-globe', 'type': 'academy', 'tier': 'B', 'country': 'US', 'scoring_points': 40},
  # César
  {'id': 'award_cesar-best-film', 'name': 'Best Film', 'organization': 'Académie des Arts et Techniques du Cinéma', 'festival_id': 'festival_cesar', 'type': 'academy', 'tier': 'B', 'country': 'FR', 'is_grand_prize': True, 'scoring_points': 50},
  {'id': 'award_cesar-best-director', 'name': 'Best Director', 'organization': 'Académie des Arts et Techniques du Cinéma', 'festival_id': 'festival_cesar', 'type': 'academy', 'tier': 'B', 'country': 'FR', 'scoring_points': 35},
  # Ariel
  {'id': 'award_ariel-best-film', 'name': 'Best Film', 'organization': 'Academia Mexicana de Artes y Ciencias Cinematográficas', 'festival_id': 'festival_ariel', 'type': 'academy', 'tier': 'B', 'country': 'MX', 'is_grand_prize': True, 'scoring_points': 40},
  {'id': 'award_ariel-best-director', 'name': 'Best Director', 'organization': 'Academia Mexicana de Artes y Ciencias Cinematográficas', 'festival_id': 'festival_ariel', 'type': 'academy', 'tier': 'B', 'country': 'MX', 'scoring_points': 28},
  # Goya
  {'id': 'award_goya-best-film', 'name': 'Best Film', 'organization': 'Academia de las Artes y las Ciencias Cinematográficas de España', 'festival_id': 'festival_goya', 'type': 'academy', 'tier': 'B', 'country': 'ES', 'is_grand_prize': True, 'scoring_points': 45},
  {'id': 'award_goya-best-director', 'name': 'Best Director', 'organization': 'Academia de las Artes y las Ciencias Cinematográficas de España', 'festival_id': 'festival_goya', 'type': 'academy', 'tier': 'B', 'country': 'ES', 'scoring_points': 32},
  # Locarno
  {'id': 'award_locarno-golden-leopard', 'name': 'Golden Leopard', 'organization': 'Locarno Film Festival', 'festival_id': 'festival_locarno', 'type': 'festival', 'tier': 'B', 'country': 'CH', 'is_grand_prize': True, 'scoring_points': 55},
  # San Sebastián
  {'id': 'award_sansebastian-golden-shell', 'name': 'Golden Shell', 'organization': 'San Sebastián International Film Festival', 'festival_id': 'festival_san-sebastian', 'type': 'festival', 'tier': 'B', 'country': 'ES', 'is_grand_prize': True, 'scoring_points': 55},
  # Toronto
  {'id': 'award_toronto-peoples-choice', 'name': "People's Choice Award", 'organization': 'Toronto International Film Festival', 'festival_id': 'festival_toronto', 'type': 'festival', 'tier': 'A', 'country': 'CA', 'scoring_points': 60},
  # Sundance
  {'id': 'award_sundance-grand-jury-drama', 'name': 'Grand Jury Prize — Drama', 'organization': 'Sundance Film Festival', 'festival_id': 'festival_sundance', 'type': 'festival', 'tier': 'A', 'country': 'US', 'scoring_points': 55},
  {'id': 'award_sundance-world-cinema-drama', 'name': 'World Cinema Grand Jury Prize — Drama', 'organization': 'Sundance Film Festival', 'festival_id': 'festival_sundance', 'type': 'festival', 'tier': 'A', 'country': 'US', 'scoring_points': 45},
  # FIPRESCI
  {'id': 'award_fipresci', 'name': 'FIPRESCI Prize', 'organization': 'International Federation of Film Critics', 'festival_id': 'festival_fipresci', 'type': 'guild', 'tier': 'C', 'country': 'DE', 'scoring_points': 20},
]

# Also patch existing legacy awards with festival_id where we can match them
legacy_patches = [
  {'id': 'award_palme_dor',        'festival_id': 'festival_cannes',          'is_grand_prize': True},
  {'id': 'award_cannes_grand_prix','festival_id': 'festival_cannes',          'is_grand_prize': False},
  {'id': 'award_cannes_best_director', 'festival_id': 'festival_cannes',      'is_grand_prize': False},
  {'id': 'award_golden_lion',      'festival_id': 'festival_venice',          'is_grand_prize': True},
  {'id': 'award_venice_silver_lion', 'festival_id': 'festival_venice',        'is_grand_prize': False},
  {'id': 'award_golden_bear',      'festival_id': 'festival_berlin',          'is_grand_prize': True},
  {'id': 'award_berlin_silver_bear', 'festival_id': 'festival_berlin',        'is_grand_prize': False},
  {'id': 'award_sundance_grand_jury', 'festival_id': 'festival_sundance',     'is_grand_prize': True},
  {'id': 'award_tiff_platform',    'festival_id': 'festival_toronto',         'is_grand_prize': False},
  {'id': 'award_oscar_picture',    'festival_id': 'festival_academy-awards',  'is_grand_prize': True},
  {'id': 'award_oscar_director',   'festival_id': 'festival_academy-awards',  'is_grand_prize': False},
  {'id': 'award_oscar_cinematography', 'festival_id': 'festival_academy-awards', 'is_grand_prize': False},
  {'id': 'award_oscar_cin_nom',    'festival_id': 'festival_academy-awards',  'is_grand_prize': False},
  {'id': 'award_bafta_film',       'festival_id': 'festival_bafta',           'is_grand_prize': True},
  {'id': 'award_bafta_cinematography', 'festival_id': 'festival_bafta',       'is_grand_prize': False},
]

print('=== INSERTING NEW AWARDS ===')
ok = fail = 0
for a in awards:
    try:
        db.table('awards').upsert(a, on_conflict='id').execute()
        print(f'  OK  [{a["tier"]}] {a["name"]} ({a["id"]})')
        ok += 1
    except Exception as e:
        print(f'  FAIL {a["name"]}: {e}')
        fail += 1
print(f'New awards: {ok} OK, {fail} FAIL\n')

print('=== PATCHING LEGACY AWARDS (festival_id + is_grand_prize) ===')
ok = fail = 0
for patch in legacy_patches:
    try:
        db.table('awards').update({k: v for k, v in patch.items() if k != 'id'}).eq('id', patch['id']).execute()
        print(f'  PATCHED {patch["id"]}')
        ok += 1
    except Exception as e:
        print(f'  FAIL {patch["id"]}: {e}')
        fail += 1
print(f'Legacy patches: {ok} OK, {fail} FAIL\n')

# ─── Step 5: Verification ─────────────────────────────────────────────────────
from collections import Counter

print('=== VERIFICATION ===')
festivals_res = db.table('festivals').select('id, name, tier').order('tier').execute()
print(f'FESTIVALS: {len(festivals_res.data)} total')
for f in festivals_res.data:
    print(f'  [{f["tier"]}] {f["name"]}')

awards_res = db.table('awards').select('id, name, festival_id, is_grand_prize').execute()
print(f'\nAWARDS: {len(awards_res.data)} total')
with_festival = sum(1 for a in awards_res.data if a.get('festival_id'))
grand_prizes = sum(1 for a in awards_res.data if a.get('is_grand_prize'))
print(f'  With festival_id: {with_festival}')
print(f'  Grand prizes: {grand_prizes}')

tiers = Counter(f['tier'] for f in festivals_res.data)
print(f'\nFestival tier distribution: {dict(tiers)}')
