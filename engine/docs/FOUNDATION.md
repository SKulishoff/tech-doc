# TechDoc Engine — frozen foundation

## What we are building
A narrow internal extractor for maintenance data. It does not recreate supplier manuals, does not publish supplier procedures, and does not need generic RAG in MVP.

## Document workflow
| Stage | Input | Action | Output |
|---|---|---|---|
| Upload | PDF | make local temporary copy and SHA-256 | job + hash |
| Duplicate/revision check | document code + hash | identical hash is skipped; changed hash is a new revision | status |
| Fast scan | whole PDF | pypdf extracts page text and scores maintenance relevance | candidate pages + OCR warning |
| Range build | candidate pages | add neighbors and merge consecutive pages | page ranges |
| Deep parse | selected ranges only | Docling parses layout/tables locally | temporary structured parse |
| Extract | tables/text | read periodicities, operations, explicit matrix marks, materials, criteria | candidate facts |
| Link | candidate + SNS/reference data | exact code/name/alias then RapidFuzz | component link or review flag |
| Review | uncertain candidates only | approve/edit/reject | approved facts |
| Store | approved facts | transaction to SQLite | one portable DB file |
| Export | DB | generate Plan ТО columns/reports | xlsx/csv |
| Cleanup | temporary PDF/raw parser output | delete | source document not retained |

## Selected OSS
- `docling-project/docling` / Docling Slim 2.126.0 — deep PDF/table parsing; MIT; local models; selected page ranges; images/RAG extras are unnecessary.
- `py-pdf/pypdf` 6.18.1 — cheap whole-document scan and independent text-coverage signal; BSD-3-Clause.
- `pydantic/pydantic` 2.13.5 — strict contracts; MIT.
- `rapidfuzz/RapidFuzz` 3.14.6 — deterministic component matching; MIT.
- `python-calamine` 0.8.2 — reads xls/xlsx/xlsm/xlsb/ods; MIT.
- `openpyxl` 3.1.5 — writes Plan ТО xlsx; MIT.
- Python `sqlite3` — one portable DB, no server.

## Deferred after research
No vector DB/RAG, NuExtract, GLiNER, MinerU, Marker, Unstructured, PostgreSQL, Elasticsearch, image understanding, replacement-card workflow. They add weight before a measured need exists.

## Permanent data
Document identity/revision/hash; component and aliases; concise operation; supplier periodicity; explicit IS marks; material/quantity/unit when stated; criterion/limit when stated; source document/page/section/table/row; confidence/review status. Do not persist complete supplier prose.

## Critical distinction
Supplier periodicity is source truth. User Plan ТО IS marks are another layer. If the document says `1000 cycles`, store `1000 cycles`; do not invent an IS mark. If a table explicitly places a `+`/`Х` under IS530, that mark may be stored as explicit source truth.

## Plan ТО export columns
`Код подгруппы/компонента | Подгруппа | Компонент | Код операции | Наименование операции | Тип операции | Предельный интервал обслуживания | IS100 | IS200 | IS510 | IS520 | IS530 | IS540 | IS600 | IS700 | C | E | P | T | Наименование документа регламентирующего ТО`

## Real benchmark cases (documents stay local, never Git)
1. `ПРС.107.10.000 РЭ проект 10.09.2026.pdf`: explicit periodicity table IS100..IS700 including IS540; maintenance/material sections.
2. `РТГН.09.64025.03 РЭ ЭВС.pdf`: explicit interval table; spacing variants `IS 100`; different tolerance for IS100.
3. `9.7 СТНР.661172.701 РЭ3...pdf`: complex multi-page table with element, ED document/point, maintenance work and maintenance/repair columns.
4. `ЭС104.0.00.000.000 РЭ8...pdf`: criteria/actions mixed with prose/tables.

## Acceptance
- every approved fact has document + page locator;
- all explicit IS intervals in the two simple benchmark tables are recovered;
- >=95% operation-table recall on manually prepared golden rows;
- ambiguous component matches and non-explicit IS mappings are never auto-approved;
- exact Plan ТО export schema including IS540;
- same SHA causes no duplicate facts;
- changed SHA for same document code is a revision, not overwrite;
- temporary source/raw files are removed after successful ingest;
- repeated benchmark produces deterministic results;
- after local model artifacts are installed, real document processing works with network disabled.
