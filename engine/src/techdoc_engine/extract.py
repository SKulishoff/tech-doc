from __future__ import annotations

import re
from typing import Sequence

from . import MAINTENANCE_TYPES
from .core import (
    MaintenanceOperationCandidate, MatrixMarks, ReviewStatus, SourceLocator,
    detect_matrix_columns, marks_from_row, parse_interval,
)
from .facts import CriterionFact, MaterialFact


def clean(value: object) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def _find_header(rows: Sequence[Sequence[object]], aliases: tuple[str, ...], max_rows: int = 6) -> tuple[int,int] | None:
    best=None; best_len=0
    for ridx,row in enumerate(rows[:max_rows]):
        for cidx,cell in enumerate(row):
            text=clean(cell).lower()
            for alias in aliases:
                if alias in text and len(alias)>best_len:
                    best=(ridx,cidx); best_len=len(alias)
    return best


def extract_operation_candidates(rows: Sequence[Sequence[object]], *, document_code: str, page: int, table_name: str | None = None) -> list[MaintenanceOperationCandidate]:
    """Extract conservative candidates from an operation matrix/list.

    No component is auto-linked here and no missing IS mark is inferred.
    """
    if not rows: return []
    op_h=_find_header(rows,("работа по техническому обслуживанию","наименование операции","содержание работ","операция","работа"))
    comp_h=_find_header(rows,("составная часть","компонент","элемент"))
    doc_h=_find_header(rows,("документ (эд)","наименование документа","документ","эд"))
    point_h=_find_header(rows,("пункты эд","пункт эд","пункт"))
    if not op_h: return []
    header_end=max([x[0] for x in (op_h,comp_h,doc_h,point_h) if x] + [0])
    matrix_cols=detect_matrix_columns(rows[:header_end+2])
    out=[]
    for row_no,row in enumerate(rows[header_end+1:],start=header_end+2):
        if op_h[1]>=len(row): continue
        operation=clean(row[op_h[1]])
        if len(operation)<3: continue
        # Avoid treating repeated headers as operations.
        low=operation.lower()
        if any(x in low for x in ("работа по техническому обслуживанию","наименование операции")): continue
        marks=marks_from_row(row,matrix_cols) if matrix_cols else MatrixMarks()
        supplier_component=clean(row[comp_h[1]]) if comp_h and comp_h[1]<len(row) else None
        source_doc=clean(row[doc_h[1]]) if doc_h and doc_h[1]<len(row) else document_code
        point=clean(row[point_h[1]]) if point_h and point_h[1]<len(row) else None
        status=ReviewStatus.NEED_REVIEW
        out.append(MaintenanceOperationCandidate(
            supplier_component_name=supplier_component or None,
            operation_name=operation,
            marks=marks,
            regulating_document=source_doc or document_code,
            source=SourceLocator(document_code=document_code,page=page,section=point or None,table=table_name,row=str(row_no)),
            confidence=0.75 if marks.enabled() else 0.6,
            review_status=status,
        ))
    return out


def extract_material_facts(rows: Sequence[Sequence[object]], *, document_code: str, page: int, table_name: str | None = None) -> list[MaterialFact]:
    if not rows: return []
    name_h=_find_header(rows,("наименование материала","материал","смазочный материал","расходный материал","жидкость","зип"))
    qty_h=_find_header(rows,("количество","расход","норма"))
    unit_h=_find_header(rows,("единица измерения","ед. изм","единица"))
    if not name_h: return []
    start=max([x[0] for x in (name_h,qty_h,unit_h) if x])+1; out=[]
    for row_no,row in enumerate(rows[start:],start=start+1):
        if name_h[1]>=len(row): continue
        name=clean(row[name_h[1]])
        if not name or "материал" in name.lower() and len(name)<30: continue
        qty=None
        if qty_h and qty_h[1]<len(row):
            m=re.search(r"\d+(?:[.,]\d+)?",clean(row[qty_h[1]]))
            if m: qty=float(m.group().replace(",","."))
        unit=clean(row[unit_h[1]]) if unit_h and unit_h[1]<len(row) else None
        out.append(MaterialFact(name=name,quantity=qty,unit=unit or None,source=SourceLocator(document_code=document_code,page=page,table=table_name,row=str(row_no))))
    return out


CRITERION_RE=re.compile(r"(?P<cmp>не\s+более|не\s+менее|не\s+допускается|не\s+допуска|от|до|менее|более)\s*(?P<value>\d+(?:[.,]\d+)?)?\s*(?P<unit>мм|мкм|мпа|кпа|па|°?с|с|мин|ч|а|в|ом|%|км)?",re.I)


def extract_criterion_facts(rows: Sequence[Sequence[object]], *, document_code: str, page: int, table_name: str | None = None) -> list[CriterionFact]:
    out=[]
    for row_no,row in enumerate(rows,start=1):
        for cell in row:
            text=clean(cell)
            if len(text)<4: continue
            match=CRITERION_RE.search(text)
            if not match: continue
            value=float(match.group("value").replace(",",".")) if match.group("value") else None
            out.append(CriterionFact(parameter=text[:160],comparator=match.group("cmp"),value=value,unit=match.group("unit"),verbatim=text,
                source=SourceLocator(document_code=document_code,page=page,table=table_name,row=str(row_no))))
    return out
