from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from techdoc_engine.adapters import DoclingAdapter  # noqa:E402
from techdoc_engine.core import classify_table, extract_periodicity_rows  # noqa:E402
from techdoc_engine.pipeline import MaintenancePipeline  # noqa:E402


def load_expected(folder: Path, stem: str) -> dict:
    p=folder/f"{stem}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--expected",type=Path,required=True); ap.add_argument("--models",type=Path,default=None); args=ap.parse_args()
    pdfs=sorted(args.input.glob("*.pdf"))
    if not pdfs:
        print("No local PDF benchmark inputs found; nothing was sent anywhere."); return 2
    scanner=MaintenancePipeline(); parser=DoclingAdapter(artifacts_path=args.models,enable_ocr=False)
    total_e=total_f=total_c=0
    for pdf in pdfs:
        expected=load_expected(args.expected,pdf.stem); scan=scanner.scan_pdf(pdf); found={}; kinds={}; table_pages=[]
        for start,end in scan.ranges:
            parsed=parser.parse_range(pdf,start,end)
            for table in parsed.tables:
                kind=str(classify_table(table.rows)); kinds[kind]=kinds.get(kind,0)+1; table_pages.append((table.table_index,table.page_no,kind))
                for k,v in extract_periodicity_rows(table.rows).items():
                    if v.value is not None: found[k]=v.value
        exp=expected.get("intervals",{}); correct=sum(1 for k,v in exp.items() if found.get(k)==float(v))
        total_e+=len(exp); total_f+=len(found); total_c+=correct
        recall=correct/len(exp) if exp else 1.0; precision=correct/len(found) if found else (1.0 if not exp else 0.0)
        print(f"\n{pdf.name}\n  selected pages: {scan.candidate_pages}\n  ranges: {scan.ranges}\n  tables: {kinds}\n  table provenance: {table_pages}")
        print(f"  intervals expected/found/correct: {len(exp)}/{len(found)}/{correct}; recall={recall:.3f}; precision={precision:.3f}")
        missing=sorted(set(exp)-set(found)); wrong={k:(exp[k],found[k]) for k in exp.keys()&found.keys() if float(exp[k])!=found[k]}
        if missing: print("  missing:",missing)
        if wrong: print("  wrong:",wrong)
    recall=total_c/total_e if total_e else 1.0; precision=total_c/total_f if total_f else 0.0
    print(f"\nOVERALL interval recall={recall:.3f} precision={precision:.3f}")
    return 0 if recall>=0.95 and precision>=0.95 else 1

if __name__=="__main__": raise SystemExit(main())
