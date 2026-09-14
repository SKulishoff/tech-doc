from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .core import ComponentRecord, ReviewStatus, TableKind, classify_table, extract_periodicity_rows, match_component
from .extract import (
    extract_criterion_facts, extract_material_facts, extract_operation_candidates,
    extract_prose_criterion_facts, extract_prose_operation_candidates,
)
from .pipeline import MaintenancePipeline, secure_temp_copy
from .storage import connect, create_ingest_run, insert_criterion, insert_material, insert_operation, register_document


@dataclass
class IngestOutcome:
    document_id: int | None
    document_state: str
    selected_pages: list[int] = field(default_factory=list)
    ranges: list[tuple[int,int]] = field(default_factory=list)
    operations: int = 0
    prose_operations: int = 0
    materials: int = 0
    criteria: int = 0
    periodicities: int = 0
    needs_ocr: bool = False
    notes: list[str] = field(default_factory=list)


def _ensure_periodicity_table(con: sqlite3.Connection) -> None:
    con.execute("""CREATE TABLE IF NOT EXISTS source_periodicities(
        id INTEGER PRIMARY KEY,
        source_document_id INTEGER NOT NULL REFERENCES documents(id),
        maintenance_type TEXT NOT NULL,
        verbatim TEXT NOT NULL,
        value REAL,
        value_max REAL,
        unit TEXT NOT NULL,
        qualifier TEXT NOT NULL,
        tolerance_percent REAL,
        source_page INTEGER NOT NULL,
        source_table TEXT,
        source_hash TEXT,
        UNIQUE(source_document_id,maintenance_type,source_page,source_table)
    )"""); con.commit()


def _aliases(con: sqlite3.Connection) -> dict[str,str]:
    try:
        return {r["alias_norm"]:r["component_code"] for r in con.execute("SELECT alias_norm,component_code FROM component_aliases WHERE confirmed=1")}
    except sqlite3.OperationalError:
        return {}


def _completed_same_hash(con: sqlite3.Connection, sha256: str) -> int | None:
    row=con.execute("""SELECT d.id FROM documents d JOIN ingest_runs r ON r.document_id=d.id
        WHERE d.sha256=? AND r.status='COMPLETED' ORDER BY r.id DESC LIMIT 1""",(sha256,)).fetchone()
    return int(row["id"]) if row else None


def _apply_component_match(op, components: list[ComponentRecord], aliases: dict[str,str]):
    if not op.supplier_component_name or not components:
        return op
    match=match_component(op.supplier_component_name,components,aliases)
    if match.code:
        op=op.model_copy(update={"component_code":match.code,"component_name":match.name,"confidence":min(0.99,max(op.confidence,match.score/100))})
    if match.needs_review:
        op=op.model_copy(update={"review_status":ReviewStatus.NEED_REVIEW})
    return op


def ingest_pdf(
    source_path: str|Path,
    *,
    document_code: str,
    db_path: str|Path,
    components: list[ComponentRecord] | None = None,
    title: str | None = None,
    revision: str | None = None,
    docling_models: str|Path|None = None,
) -> IngestOutcome:
    """Run the local two-pass ingest. Supplier PDF is temporary and not serialized to DB."""
    components=components or []
    pipeline=MaintenancePipeline()
    con=connect(db_path); _ensure_periodicity_table(con)
    try:
        with secure_temp_copy(source_path) as temp_pdf:
            scan=pipeline.scan_pdf(temp_pdf)
            completed=_completed_same_hash(con,scan.sha256)
            if completed:
                return IngestOutcome(document_id=completed,document_state="duplicate",notes=["identical completed SHA already ingested"])
            existing=con.execute("SELECT id FROM documents WHERE sha256=?",(scan.sha256,)).fetchone()
            if existing:
                document_id=int(existing["id"]); state="retry"
            else:
                document_id,state=register_document(con,code=document_code,sha256=scan.sha256,filename=Path(source_path).name,title=title,revision=revision)
            run_id=create_ingest_run(con,document_id,"STARTED",scan.candidate_pages)
            selected_set=set(scan.candidate_pages)
            needs_ocr=any(s.needs_ocr and s.page in selected_set for s in scan.signals)
            outcome=IngestOutcome(document_id=document_id,document_state=state,selected_pages=scan.candidate_pages,ranges=scan.ranges,needs_ocr=needs_ocr)
            if not scan.ranges:
                con.execute("UPDATE ingest_runs SET status='NEED_REVIEW',notes=? WHERE id=?",("no maintenance pages selected",run_id)); con.commit()
                outcome.notes.append("no maintenance pages selected"); return outcome
            parsed_ranges=pipeline.deep_parse_selected(temp_pdf,scan.ranges,artifacts_path=docling_models,enable_ocr=needs_ocr)
            aliases=_aliases(con)
            for parsed in parsed_ranges:
                for table in parsed.tables:
                    page=table.page_no or parsed.start_page; table_name=f"table-{table.table_index}"
                    kind=classify_table(table.rows)
                    if kind==TableKind.PERIODICITY:
                        for maintenance_type,interval in extract_periodicity_rows(table.rows).items():
                            con.execute("""INSERT OR REPLACE INTO source_periodicities(source_document_id,maintenance_type,verbatim,value,value_max,unit,qualifier,tolerance_percent,source_page,source_table,source_hash)
                                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(document_id,maintenance_type,interval.verbatim,interval.value,interval.value_max,interval.unit,interval.qualifier,interval.tolerance_percent,page,table_name,scan.sha256))
                            outcome.periodicities+=1
                    if kind in {TableKind.OPERATION_MATRIX,TableKind.OPERATION_LIST}:
                        for op in extract_operation_candidates(table.rows,document_code=document_code,page=page,table_name=table_name):
                            op=_apply_component_match(op,components,aliases)
                            op=op.model_copy(update={"source":op.source.model_copy(update={"source_hash":scan.sha256})})
                            insert_operation(con,document_id,op); outcome.operations+=1
                    if kind==TableKind.MATERIALS:
                        for fact in extract_material_facts(table.rows,document_code=document_code,page=page,table_name=table_name):
                            fact=fact.model_copy(update={"source":fact.source.model_copy(update={"source_hash":scan.sha256})}); insert_material(con,document_id,fact); outcome.materials+=1
                    if kind in {TableKind.CRITERIA,TableKind.OPERATION_MATRIX,TableKind.OPERATION_LIST}:
                        for fact in extract_criterion_facts(table.rows,document_code=document_code,page=page,table_name=table_name):
                            fact=fact.model_copy(update={"source":fact.source.model_copy(update={"source_hash":scan.sha256})}); insert_criterion(con,document_id,fact); outcome.criteria+=1

                # Prose extraction is deliberately conservative: all records remain NEED_REVIEW.
                for block in parsed.text_blocks:
                    page=block.page_no or parsed.start_page
                    for op in extract_prose_operation_candidates(block.text,document_code=document_code,page=page,label=block.label):
                        op=op.model_copy(update={"source":op.source.model_copy(update={"source_hash":scan.sha256})})
                        insert_operation(con,document_id,op); outcome.operations+=1; outcome.prose_operations+=1
                    for fact in extract_prose_criterion_facts(block.text,document_code=document_code,page=page):
                        fact=fact.model_copy(update={"source":fact.source.model_copy(update={"source_hash":scan.sha256})}); insert_criterion(con,document_id,fact); outcome.criteria+=1
            con.commit()
            con.execute("UPDATE ingest_runs SET status='COMPLETED',notes=? WHERE id=?",(json.dumps(outcome.__dict__,ensure_ascii=False,default=str),run_id)); con.commit()
            return outcome
    except Exception as exc:
        try:
            if 'run_id' in locals():
                con.execute("UPDATE ingest_runs SET status='FAILED',notes=? WHERE id=?",(f"{type(exc).__name__}: {exc}",run_id)); con.commit()
        finally:
            con.close()
        raise
    finally:
        try: con.close()
        except Exception: pass
