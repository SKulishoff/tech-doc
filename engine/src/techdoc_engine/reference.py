from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .adapters import ExcelAdapter
from .core import ComponentRecord


def _norm(value: object) -> str:
    return " ".join(str(value or "").replace("\n", " ").split())


def find_header_row(rows: list[list[object]], required_any: Iterable[str], max_rows: int = 25) -> int:
    needles=tuple(required_any); best_idx=-1; best_count=0
    for idx,row in enumerate(rows[:max_rows]):
        cells={_norm(c) for c in row}; count=sum(1 for n in needles if n in cells)
        if count>best_count: best_idx,best_count=idx,count
    if best_count==0: raise ValueError("header row not found")
    return best_idx


def rows_as_dicts(rows: list[list[object]], header_idx: int) -> list[dict[str,object]]:
    headers=[_norm(c) for c in rows[header_idx]]; out=[]
    for row in rows[header_idx+1:]:
        if not any(_norm(c) for c in row): continue
        padded=list(row)+[None]*max(0,len(headers)-len(row))
        out.append({headers[i]:padded[i] for i in range(len(headers)) if headers[i]})
    return out


def load_plan_rows(path: str|Path, sheet_name: str|None=None) -> list[dict[str,object]]:
    rows=ExcelAdapter().rows(path,sheet_name)
    idx=find_header_row(rows,("Код подгруппы/компонента","Код операции","Наименование операции"))
    return rows_as_dicts(rows,idx)


def components_from_plan_rows(rows: list[dict[str,object]]) -> list[ComponentRecord]:
    seen: dict[str,ComponentRecord]={}
    for row in rows:
        code=_norm(row.get("Код подгруппы/компонента")); name=_norm(row.get("Компонент"))
        if code and name: seen.setdefault(code,ComponentRecord(code,name))
    return list(seen.values())
