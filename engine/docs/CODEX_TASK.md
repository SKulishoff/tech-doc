# Codex task — do not redesign

The architecture and OSS selection are frozen in `FOUNDATION.md`. Your job is integration and measured correction, not research.

## A. Expand/inspect the supplied engine files
Install `engine/` editable with dev extras. Run unit tests before any behavior change.

## B. Verify pinned OSS APIs
1. Verify `DoclingAdapter` against Docling Slim 2.126.0. Correct only real API mismatches.
2. Verify `ExcelAdapter` against python-calamine 0.8.2.
3. Keep Docling local: remote services false, external plugins false, pictures/page images false, table structure true. OCR is fallback only.

## C. Run the real local benchmark
Supplier documents must not be committed. Place local copies in `engine/golden/input/` and use the four cases listed in `FOUNDATION.md`.

For each document report:
- pages selected by fast scan;
- tables classified;
- expected facts / found facts / correct facts;
- recall and precision;
- exact misses/false positives.

## D. Fix only measured misses
Prefer small additions to header aliases, table normalization or regex rules. Do not add an LLM or another document parser merely because a row is difficult. If deterministic extraction remains below acceptance for a recurring pattern, document that pattern first before proposing another model.

## E. Invariants to verify
- no source locator -> cannot approve;
- no inferred IS `+` written as explicit source fact;
- identical SHA is duplicate;
- new SHA under same document code creates revision;
- source PDF and temporary Docling raw output are deleted after successful ingest;
- output xlsx has exact Plan ТО schema including IS540;
- second run gives same result.

## Stop condition
Stop when `FOUNDATION.md` acceptance gates pass. Return only: tests, per-document benchmark metrics, unresolved cases, exact files changed, and any pinned-library API mismatch. Do not build UI/RAG/vector DB/replacement cards/cloud deployment in this task.
