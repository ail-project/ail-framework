# Phash PR - Files to Include (post–Terrtia review)

## New Files (to be added)

1. `bin/lib/objects/Phashs.py` – Phash object, Phashs collection, all phash logic (calculate, compare, get from correlation)
2. `bin/modules/ImagePhash.py` – Uses Phashs for calculation; no phash on image
3. `bin/modules/PhashCorrelation.py` – Uses Phashs.compare_phash
4. `var/www/blueprints/objects_phash.py`
5. `var/www/templates/objects/phash/PhashDaterange.html`
6. `tests/test_objects_phashes.py`
7. `tests/test_objects_images_and_screenshots.py` – Image/Screenshot tests (no phash methods)

## Modified Files (to be committed)

1. `bin/lib/objects/Images.py` – No phash methods; get_content(bytes)→BytesIO; get_description_models bytes/str
2. `bin/lib/objects/Screenshots.py` – No phash methods; get_description_models bytes/str
3. `bin/lib/correlations_engine.py` – phash correlation type
4. `bin/lib/objects/ail_objects.py` – Phash registered
5. `bin/lib/ail_core.py` – phash in AIL_OBJECTS
6. `configs/modules.cfg` – ImagePhash, PhashCorrelation
7. `bin/LAUNCH.sh` – ImagePhash, PhashCorrelation
8. `configs/core.cfg.sample` – phash_max_hamming_distance
9. `var/www/Flask_server.py` – objects_phash blueprint
10. `var/www/blueprints/correlation.py` – image_phash via Phashs.get_phash_from_correlation(img)
11. `tests/test_modules.py` – Phash module tests; patch Phashs; mock imports

## Optional / Exclude per preference

- `tools/backfill_phash.py`, `tools/trigger_phash_correlation.py` – use Phashs; include if you want script support in repo
- `docs/`, `PR_*.md` – optional
- `.ail-api-key`, secrets – exclude

## Before pushing

1. All 114 tests pass (`python3 -m nose2 --start-dir tests -v`).
2. Stage only intended files; exclude any local-only or secret files.
