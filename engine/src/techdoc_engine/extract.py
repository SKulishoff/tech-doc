from __future__ import annotations

import re
from typing import Sequence

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


def _unit_from_header(text: str) -> str | None:
    low=text.lower()
    if re.search(r"\bкм\b|километр",low): return "km"
    if re.search(r"\bсут|дн",low): return "day"
    if "месяц" in low: return "month"
    if re.search(r"\bлет\b|год",low): return "year"
    if "цикл" in low: return "cycle"
    if "час" in low: return "hour"
    return None


def extract_operation_candidates(rows: Sequence[Sequence[object]], *, document_code: str, page: int, table_name: str | None = None) -> list[MaintenanceOperationCandidate]:
    """Conservative table extractor. It never invents an IS mark or component link."""
    if not rows: return []
    op_h=_find_header(rows,("работа по техническому обслуживанию","наименование работы и объекта то","виды работ при обслуживании","наименование операции","содержание работ","тип работ","операция","работа"))
    comp_h=_find_header(rows,("составная часть","компонент","элемент"))
    doc_h=_find_header(rows,("документ (эд)","наименование документа","документ","эд"))
    point_h=_find_header(rows,("номер пункта рэ","пункты эд","пункт эд","указание по выполнению работ","пункт"))
    interval_h=_find_header(rows,("периодичность, км","периодичность","межремонтный пробег","интервал"))
    if not op_h: return []
    header_end=max([x[0] for x in (op_h,comp_h,doc_h,point_h,interval_h) if x] + [0])
    matrix_cols=detect_matrix_columns(rows[:header_end+3])
    interval_header_text=clean(rows[interval_h[0]][interval_h[1]]) if interval_h else ""
    interval_header_unit=_unit_from_header(interval_header_text)
    out=[]; last_component=None; last_doc=document_code
    for row_no,row in enumerate(rows[header_end+1:],start=header_end+2):
        if op_h[1]>=len(row): continue
        operation=clean(row[op_h[1]])
        if len(operation)<3: continue
        low=operation.lower()
        if any(x in low for x in ("работа по техническому обслуживанию","наименование операции","наименование работы и объекта то")): continue
        marks=marks_from_row(row,matrix_cols) if matrix_cols else MatrixMarks()
        supplier_component=clean(row[comp_h[1]]) if comp_h and comp_h[1]<len(row) else ""
        if supplier_component: last_component=supplier_component
        source_doc=clean(row[doc_h[1]]) if doc_h and doc_h[1]<len(row) else ""
        if source_doc: last_doc=source_doc
        point=clean(row[point_h[1]]) if point_h and point_h[1]<len(row) else None
        interval=None
        if interval_h and interval_h[1]<len(row):
            interval=parse_interval(clean(row[interval_h[1]]))
            if interval and interval.unit=="unknown" and interval_header_unit:
                interval=interval.model_copy(update={"unit":interval_header_unit})
        if interval is None:
            for cell in row:
                candidate=parse_interval(clean(cell))
                if candidate and (candidate.unit!="unknown" or candidate.qualifier=="event"):
                    interval=candidate; break
        out.append(MaintenanceOperationCandidate(
            supplier_component_name=last_component or None,
            operation_name=operation,
            interval=interval,
            marks=marks,
            regulating_document=last_doc or document_code,
            source=SourceLocator(document_code=document_code,page=page,section=point or None,table=table_name,row=str(row_no)),
            confidence=0.80 if marks.enabled() else 0.65,
            review_status=ReviewStatus.NEED_REVIEW,
        ))
    return out


def extract_material_facts(rows: Sequence[Sequence[object]], *, document_code: str, page: int, table_name: str | None = None) -> list[MaterialFact]:
    if not rows: return []
    name_h=_find_header(rows,("наименование материала","материал","смазочный материал","расходный материал","жидкость","зип"))
    qty_h=_find_header(rows,("количество","расход","норма")); unit_h=_find_header(rows,("единица измерения","ед. изм","единица"))
    if not name_h: return []
    start=max([x[0] for x in (name_h,qty_h,unit_h) if x])+1; out=[]
    for row_no,row in enumerate(rows[start:],start=start+1):
        if name_h[1]>=len(row): continue
        name=clean(row[name_h[1]])
        if not name or ("материал" in name.lower() and len(name)<30): continue
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


PROSE_ACTION_RE = re.compile(
    r"(?:^|\b)(?:произвести|выполнить|провести|проводить|проверить|контролировать|осмотреть|очистить|заменить|смазать|измерить|осуществить)\b",
    re.I,
)
SECTION_PREFIX_RE = re.compile(r"^\s*(\d+(?:\.\d+){1,5})\s+")


def _compact_operation_text(text: str, limit: int = 360) -> tuple[str, str | None]:
    value=clean(text); section=None
    m=SECTION_PREFIX_RE.match(value)
    if m:
        section=m.group(1); value=value[m.end():].strip()
    # One source paragraph may carry procedure detail; candidate name stays bounded but verbatim source is not persisted here.
    first=re.split(r"(?<=[.!?])\s+(?=[А-ЯA-Z0-9])",value,maxsplit=1)[0].strip()
    return (first[:limit] if len(first)>limit else first), section


def extract_prose_operation_candidates(text: str, *, document_code: str, page: int, label: str | None = None) -> list[MaintenanceOperationCandidate]:
    value=clean(text)
    if len(value)<8 or not PROSE_ACTION_RE.search(value): return []
    low=value.lower()
    # Suppress common non-maintenance meta/safety statements. They can still be found in source but are not Plan ТО operations.
    if any(x in low for x in ("персонал обязан", "персоналу запрещ", "должны соблюдаться", "требования безопасности", "следует произвести необходимые записи")):
        return []
    operation,section=_compact_operation_text(value)
    interval=parse_interval(value)
    confidence=0.55
    if section: confidence+=0.08
    if interval: confidence+=0.07
    return [MaintenanceOperationCandidate(
        operation_name=operation,
        interval=interval,
        regulating_document=document_code,
        source=SourceLocator(document_code=document_code,page=page,section=section),
        confidence=min(confidence,0.75),
        review_status=ReviewStatus.NEED_REVIEW,
    )]


def extract_prose_criterion_facts(text: str, *, document_code: str, page: int) -> list[CriterionFact]:
    value=clean(text); out=[]
    for match in CRITERION_RE.finditer(value):
        cmp=match.group("cmp"); raw_value=match.group("value")
        number=float(raw_value.replace(",",".")) if raw_value else None
        start=max(0,match.start()-90); end=min(len(value),match.end()+110)
        snippet=value[start:end].strip()
        out.append(CriterionFact(
            parameter=snippet[:160], comparator=cmp, value=number, unit=match.group("unit"), verbatim=snippet,
            source=SourceLocator(document_code=document_code,page=page), review_status=ReviewStatus.NEED_REVIEW,
        ))
    return out
