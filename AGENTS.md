# AGENTS.md — TechDoc engine

## Scope
Build only the maintenance-data extraction engine under `engine/`. Do not redesign the Streamlit demo in root `app.py` unless explicitly asked.

## Product goal
Convert supplier PDF/Excel documents into verified structured maintenance facts for the user's Plan ТО database. This is an internal extraction tool, not a document-reproduction system and not a generic RAG app.

## Hard rules
1. Real supplier documents must never be committed to Git.
2. No external AI/API/cloud calls. Real documents must be processable locally/offline.
3. Do not persist full supplier-document text in the production SQLite database. Persist structured facts plus source locator/hash. Temporary snippets/raw parser output must be deletable after ingest.
4. Never invent an operation, interval, criterion, material, component link, or IS mapping. Uncertain records become `NEED_REVIEW` or `UNRESOLVED`.
5. Supplier periodicity and the user's IS matrix are separate. Only write an IS `+` when it is explicit in the source or separately approved.
6. Required maintenance columns: `IS100, IS200, IS510, IS520, IS530, IS540, IS600, IS700, C, E, P, T`.
7. Every approved fact must carry source document ID and page; table/section/row when available.
8. Re-ingest of identical SHA-256 is a duplicate. A new SHA for the same document code is a new revision and must not silently overwrite approved facts.
9. Prefer standard library/simple dependencies. Do not add vector DBs, ORMs, queues, containers, web frameworks, LLM frameworks, or cloud services unless acceptance tests prove they are needed.
10. Replacement-card processing is deferred.

## Selected OSS building blocks
- Docling Slim — deep PDF/table parsing, local only.
- pypdf — cheap first-pass page scan and independent text-coverage check.
- Pydantic — strict data contracts.
- RapidFuzz — component/alias matching.
- python-calamine — read xls/xlsx/xlsm/xlsb/ods.
- openpyxl — write Plan ТО xlsx.
- Python sqlite3 — one portable database file.

## Expected workflow
PDF -> SHA/check duplicate -> pypdf page scan -> select maintenance-related page ranges -> Docling deep parse only those ranges -> classify tables -> extract candidate facts -> parse intervals -> resolve component -> review uncertain facts -> SQLite -> export Plan ТО xlsx -> delete temporary source/raw artifacts.

## Codex work style
Read `engine/docs/CODEX_TASK.md` first. Do not repeat architecture research. Run tests before modifying behavior. Make the smallest changes needed for acceptance. Prefer deterministic extraction. Report benchmark numbers and unresolved cases, not subjective claims.
