# TechDoc Engine

This branch contains the prebuilt foundation for the real internal extractor. Root `app.py` remains the visual demo and is intentionally untouched.

## Purpose
Extract only maintenance-related structured facts from supplier documents: operations, periodicities, explicit maintenance-matrix marks, materials/consumables, criteria/limits, source links, and component links. Do not recreate whole manuals.

## Quick verification for Codex
```bash
cd engine
python -m pip install -e '.[dev]'
python -m pytest -q
```

Then place the four real benchmark PDFs locally under `engine/golden/input/` (they are ignored by Git) and run:
```bash
python scripts/benchmark.py --input golden/input --expected golden/expected --models <local-docling-model-folder>
```

Read `docs/FOUNDATION.md` for architecture and acceptance gates, then `docs/CODEX_TASK.md` for the intentionally small remaining task.

## Important
No real supplier PDF, real database, parser raw dump, or working spreadsheet is to be committed. Real processing is designed to stay local/offline.
