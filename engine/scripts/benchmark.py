from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from techdoc_engine.adapters import DoclingAdapter  # noqa:E402
from techdoc_engine.core import TableKind, classify_table, extract_periodicity_rows, normalize_name  # noqa:E402
from techdoc_engine.extract import extract_operation_candidates, extract_prose_operation_candidates  # noqa:E402
from techdoc_engine.pipeline import MaintenancePipeline  # noqa:E402


def load_expected(folder: Path, stem: str) -> dict:
    p=folder/f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _contains(haystack: str, needle: str) -> bool:
    return normalize_name(needle) in normalize_name(haystack)


def _find_operation(found, expected: dict):
    needle=expected.get("name") or expected.get("contains") or ""
    for op in found:
        if _contains(op.operation_name,needle) or _contains(needle,op.operation_name):
            if expected.get("supplier_component_contains") and not _contains(op.supplier_component_name or "",expected["supplier_component_contains"]):
                continue
            if expected.get("regulating_document_contains") and not _contains(op.regulating_document or "",expected["regulating_document_contains"]):
                continue
            if expected.get("source_point_contains") and not _contains(op.source.section or "",expected["source_point_contains"]):
                continue
            return op
    return None


def _validate_operation(op, expected: dict) -> list[str]:
    errors=[]
    if "marks" in expected:
        got=set(op.marks.enabled()); want=set(expected["marks"])
        if got!=want: errors.append(f"marks want={sorted(want)} got={sorted(got)}")
    if "interval" in expected:
        want=expected["interval"]; got=op.interval
        if not got: errors.append("interval missing")
        else:
            for key in ("value","unit","qualifier","tolerance_percent"):
                if key in want and getattr(got,key)!=want[key]: errors.append(f"interval.{key} want={want[key]} got={getattr(got,key)}")
    return errors


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--expected",type=Path,required=True); ap.add_argument("--models",type=Path,default=None); args=ap.parse_args()
    pdfs=sorted(args.input.glob("*.pdf"))
    if not pdfs:
        print("No local PDF benchmark inputs found; nothing was sent anywhere."); return 2
    scanner=MaintenancePipeline(); parser=DoclingAdapter(artifacts_path=args.models,enable_ocr=False)
    total_interval_e=total_interval_f=total_interval_c=0
    total_ops_e=total_ops_c=0; total_prose_e=total_prose_c=0; validation_errors=[]
    for pdf in pdfs:
        expected=load_expected(args.expected,pdf.stem); scan=scanner.scan_pdf(pdf); found_intervals={}; kinds={}; table_pages=[]; found_ops=[]; found_prose=[]
        for start,end in scan.ranges:
            parsed=parser.parse_range(pdf,start,end)
            for table in parsed.tables:
                kind=classify_table(table.rows); kname=str(kind); kinds[kname]=kinds.get(kname,0)+1; table_pages.append((table.table_index,table.page_no,kname))
                if kind==TableKind.PERIODICITY:
                    for k,v in extract_periodicity_rows(table.rows).items():
                        if v.value is not None: found_intervals[k]=v.value
                if kind in {TableKind.OPERATION_MATRIX,TableKind.OPERATION_LIST}:
                    found_ops.extend(extract_operation_candidates(table.rows,document_code=expected.get("document_code",pdf.stem),page=table.page_no or start,table_name=f"table-{table.table_index}"))
            for block in parsed.text_blocks:
                found_prose.extend(extract_prose_operation_candidates(block.text,document_code=expected.get("document_code",pdf.stem),page=block.page_no or start,label=block.label))

        exp_int=expected.get("intervals",{}); int_correct=sum(1 for k,v in exp_int.items() if found_intervals.get(k)==float(v))
        total_interval_e+=len(exp_int); total_interval_f+=len(found_intervals); total_interval_c+=int_correct
        int_recall=int_correct/len(exp_int) if exp_int else 1.0; int_precision=int_correct/len(found_intervals) if found_intervals else (1.0 if not exp_int else 0.0)

        exp_ops=expected.get("operations",[]); op_correct=0
        for e in exp_ops:
            op=_find_operation(found_ops,e)
            if op:
                errors=_validate_operation(op,e)
                if not errors: op_correct+=1
                else: validation_errors.append((pdf.name,e.get("name") or e.get("contains"),errors))
        total_ops_e+=len(exp_ops); total_ops_c+=op_correct

        exp_prose=expected.get("prose_operations",[]); prose_correct=0
        for e in exp_prose:
            op=_find_operation(found_prose,e)
            if op:
                errors=_validate_operation(op,e)
                if not errors: prose_correct+=1
                else: validation_errors.append((pdf.name,e.get("contains"),errors))
        total_prose_e+=len(exp_prose); total_prose_c+=prose_correct

        print(f"\n{pdf.name}\n  selected pages: {scan.candidate_pages}\n  ranges: {scan.ranges}\n  tables: {kinds}\n  table provenance: {table_pages}")
        print(f"  source intervals expected/found/correct: {len(exp_int)}/{len(found_intervals)}/{int_correct}; recall={int_recall:.3f}; precision={int_precision:.3f}")
        if exp_ops: print(f"  table operations expected/found/correct: {len(exp_ops)}/{len(found_ops)}/{op_correct}; recall={op_correct/len(exp_ops):.3f}")
        if exp_prose: print(f"  prose operations expected/found/correct: {len(exp_prose)}/{len(found_prose)}/{prose_correct}; recall={prose_correct/len(exp_prose):.3f}")
        missing_int=sorted(set(exp_int)-set(found_intervals)); wrong_int={k:(exp_int[k],found_intervals[k]) for k in exp_int.keys()&found_intervals.keys() if float(exp_int[k])!=found_intervals[k]}
        if missing_int: print("  interval missing:",missing_int)
        if wrong_int: print("  interval wrong:",wrong_int)
        missing_ops=[e.get("name") or e.get("contains") for e in exp_ops if not _find_operation(found_ops,e)]
        missing_prose=[e.get("contains") for e in exp_prose if not _find_operation(found_prose,e)]
        if missing_ops: print("  table operation missing:",missing_ops)
        if missing_prose: print("  prose operation missing:",missing_prose)

    int_recall=total_interval_c/total_interval_e if total_interval_e else 1.0
    int_precision=total_interval_c/total_interval_f if total_interval_f else 1.0
    op_recall=total_ops_c/total_ops_e if total_ops_e else 1.0
    prose_recall=total_prose_c/total_prose_e if total_prose_e else 1.0
    print(f"\nOVERALL interval recall={int_recall:.3f} precision={int_precision:.3f}; table-op recall={op_recall:.3f}; prose-op recall={prose_recall:.3f}")
    for item in validation_errors: print("VALIDATION:",item)
    # Precision for operation candidates is intentionally reviewed manually in this phase; recall and exact expected fields are hard gates.
    return 0 if int_recall>=0.95 and int_precision>=0.95 and op_recall>=0.95 and prose_recall>=0.90 and not validation_errors else 1

if __name__=="__main__": raise SystemExit(main())
