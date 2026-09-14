from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from openpyxl import Workbook

from . import MAINTENANCE_TYPES
from .core import MaintenanceOperationCandidate
from .facts import CriterionFact, MaterialFact

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS documents(
 id INTEGER PRIMARY KEY, code TEXT NOT NULL, title TEXT, revision TEXT,
 sha256 TEXT NOT NULL UNIQUE, filename TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS ix_documents_code ON documents(code);
CREATE TABLE IF NOT EXISTS components(
 code TEXT PRIMARY KEY, subgroup TEXT, name TEXT NOT NULL, quantity REAL, location TEXT);
CREATE TABLE IF NOT EXISTS component_aliases(
 alias_norm TEXT PRIMARY KEY, component_code TEXT NOT NULL REFERENCES components(code), confirmed INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS operations(
 id INTEGER PRIMARY KEY, component_code TEXT REFERENCES components(code), operation_code TEXT UNIQUE,
 operation_name TEXT NOT NULL, operation_type TEXT, regulating_document TEXT NOT NULL,
 source_document_id INTEGER NOT NULL REFERENCES documents(id), source_page INTEGER NOT NULL,
 source_section TEXT, source_table TEXT, source_row TEXT, source_hash TEXT,
 confidence REAL NOT NULL DEFAULT 0, review_status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS intervals(
 id INTEGER PRIMARY KEY, operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
 verbatim TEXT NOT NULL, value REAL, value_max REAL, unit TEXT NOT NULL, qualifier TEXT NOT NULL, tolerance_percent REAL);
CREATE TABLE IF NOT EXISTS matrix_marks(
 operation_id INTEGER NOT NULL REFERENCES operations(id) ON DELETE CASCADE,
 maintenance_type TEXT NOT NULL, is_explicit INTEGER NOT NULL DEFAULT 1,
 PRIMARY KEY(operation_id,maintenance_type));
CREATE TABLE IF NOT EXISTS materials(
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, quantity REAL, unit TEXT, component_code TEXT REFERENCES components(code),
 maintenance_type TEXT, source_document_id INTEGER NOT NULL REFERENCES documents(id), source_page INTEGER NOT NULL,
 source_table TEXT, source_row TEXT, source_hash TEXT, review_status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS criteria(
 id INTEGER PRIMARY KEY, parameter TEXT NOT NULL, comparator TEXT, value REAL, value_max REAL, unit TEXT, verbatim TEXT NOT NULL,
 component_code TEXT REFERENCES components(code), operation_code TEXT, source_document_id INTEGER NOT NULL REFERENCES documents(id),
 source_page INTEGER NOT NULL, source_table TEXT, source_row TEXT, source_hash TEXT, review_status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ingest_runs(
 id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES documents(id), status TEXT NOT NULL,
 selected_pages TEXT, notes TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
"""

PLAN_HEADERS = [
    "Код подгруппы/компонента", "Подгруппа", "Компонент", "Код операции",
    "Наименование операции", "Тип операции", "Предельный интервал обслуживания",
    *MAINTENANCE_TYPES, "Наименование документа регламентирующего ТО",
]


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while chunk := fh.read(chunk_size): digest.update(chunk)
    return digest.hexdigest()


def connect(path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(path); con.row_factory = sqlite3.Row; con.executescript(SCHEMA); return con


def register_document(con: sqlite3.Connection, *, code: str, sha256: str, filename: str, title: str | None = None, revision: str | None = None) -> tuple[int, str]:
    same = con.execute("SELECT id FROM documents WHERE sha256=?", (sha256,)).fetchone()
    if same: return int(same["id"]), "duplicate"
    prior = con.execute("SELECT id FROM documents WHERE code=? ORDER BY id DESC LIMIT 1", (code,)).fetchone()
    cur = con.execute("INSERT INTO documents(code,title,revision,sha256,filename) VALUES(?,?,?,?,?)", (code,title,revision,sha256,filename)); con.commit()
    return int(cur.lastrowid), "revision" if prior else "new"


def create_ingest_run(con: sqlite3.Connection, document_id: int, status: str, selected_pages: list[int], notes: str | None = None) -> int:
    cur = con.execute("INSERT INTO ingest_runs(document_id,status,selected_pages,notes) VALUES(?,?,?,?)", (document_id,status,json.dumps(selected_pages,ensure_ascii=False),notes)); con.commit(); return int(cur.lastrowid)


def insert_operation(con: sqlite3.Connection, document_id: int, op: MaintenanceOperationCandidate) -> int:
    with con:
        cur = con.execute("""INSERT INTO operations(component_code,operation_code,operation_name,operation_type,regulating_document,
        source_document_id,source_page,source_section,source_table,source_row,source_hash,confidence,review_status)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""", (op.component_code,op.operation_code,op.operation_name,op.operation_type,op.regulating_document,
        document_id,op.source.page,op.source.section,op.source.table,op.source.row,op.source.source_hash,op.confidence,op.review_status.value))
        oid = int(cur.lastrowid)
        if op.interval:
            i=op.interval; con.execute("INSERT INTO intervals(operation_id,verbatim,value,value_max,unit,qualifier,tolerance_percent) VALUES(?,?,?,?,?,?,?)",
                (oid,i.verbatim,i.value,i.value_max,i.unit,i.qualifier,i.tolerance_percent))
        for t in op.marks.enabled(): con.execute("INSERT INTO matrix_marks(operation_id,maintenance_type,is_explicit) VALUES(?,?,1)",(oid,t))
    return oid


def insert_material(con: sqlite3.Connection, document_id: int, fact: MaterialFact) -> int:
    cur=con.execute("""INSERT INTO materials(name,quantity,unit,component_code,maintenance_type,source_document_id,source_page,source_table,source_row,source_hash,review_status)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(fact.name,fact.quantity,fact.unit,fact.component_code,fact.maintenance_type,document_id,fact.source.page,fact.source.table,fact.source.row,fact.source.source_hash,fact.review_status.value)); con.commit(); return int(cur.lastrowid)


def insert_criterion(con: sqlite3.Connection, document_id: int, fact: CriterionFact) -> int:
    cur=con.execute("""INSERT INTO criteria(parameter,comparator,value,value_max,unit,verbatim,component_code,operation_code,source_document_id,source_page,source_table,source_row,source_hash,review_status)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(fact.parameter,fact.comparator,fact.value,fact.value_max,fact.unit,fact.verbatim,fact.component_code,fact.operation_code,document_id,fact.source.page,fact.source.table,fact.source.row,fact.source.source_hash,fact.review_status.value)); con.commit(); return int(cur.lastrowid)


def export_plan_xlsx(con: sqlite3.Connection, path: str | Path) -> Path:
    wb=Workbook(); ws=wb.active; ws.title="План ТО"; ws.append(PLAN_HEADERS)
    rows=con.execute("""SELECT o.id,o.component_code,c.subgroup,c.name component_name,o.operation_code,o.operation_name,
        o.operation_type,o.regulating_document,i.verbatim interval_text FROM operations o
        LEFT JOIN components c ON c.code=o.component_code LEFT JOIN intervals i ON i.operation_id=o.id
        WHERE o.review_status IN ('AUTO_OK','APPROVED') ORDER BY o.component_code,o.operation_code,o.id""").fetchall()
    for r in rows:
        marks={x["maintenance_type"] for x in con.execute("SELECT maintenance_type FROM matrix_marks WHERE operation_id=? AND is_explicit=1",(r["id"],))}
        ws.append([r["component_code"],r["subgroup"],r["component_name"],r["operation_code"],r["operation_name"],r["operation_type"],r["interval_text"],
                   *[("+" if t in marks else "-") for t in MAINTENANCE_TYPES],r["regulating_document"]])
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True); wb.save(target); return target
