from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from rapidfuzz import fuzz, process

from . import MAINTENANCE_TYPES


class ReviewStatus(StrEnum):
    AUTO_OK = "AUTO_OK"
    NEED_REVIEW = "NEED_REVIEW"
    UNRESOLVED = "UNRESOLVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class SourceLocator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_code: str
    page: int = Field(ge=1)
    section: str | None = None
    table: str | None = None
    row: str | None = None
    source_hash: str | None = None


class IntervalRule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verbatim: str
    value: float | None = None
    value_max: float | None = None
    unit: Literal["km", "day", "month", "year", "cycle", "hour", "event", "unknown"] = "unknown"
    qualifier: Literal["exact", "max", "min", "range", "event", "unknown"] = "unknown"
    tolerance_percent: float | None = None


class MatrixMarks(BaseModel):
    model_config = ConfigDict(extra="forbid")
    IS100: bool = False; IS200: bool = False; IS510: bool = False; IS520: bool = False
    IS530: bool = False; IS540: bool = False; IS600: bool = False; IS700: bool = False
    C: bool = False; E: bool = False; P: bool = False; T: bool = False

    def enabled(self) -> list[str]:
        return [name for name in MAINTENANCE_TYPES if getattr(self, name)]


class MaintenanceOperationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    component_code: str | None = None
    component_name: str | None = None
    supplier_component_name: str | None = None
    operation_code: str | None = None
    operation_name: str
    operation_type: str | None = None
    interval: IntervalRule | None = None
    marks: MatrixMarks = Field(default_factory=MatrixMarks)
    regulating_document: str
    source: SourceLocator
    confidence: float = Field(default=0.0, ge=0, le=1)
    review_status: ReviewStatus = ReviewStatus.NEED_REVIEW

    @model_validator(mode="after")
    def approved_requires_source(self):
        if self.review_status in {ReviewStatus.AUTO_OK, ReviewStatus.APPROVED} and not self.source.document_code:
            raise ValueError("approved fact requires source document")
        return self


class PageSignal(BaseModel):
    page: int
    score: int
    reasons: list[str] = Field(default_factory=list)
    text_length: int = 0
    needs_ocr: bool = False


SCAN_RULES: tuple[tuple[str, re.Pattern[str], int], ...] = (
    ("maintenance", re.compile(r"техническ\w*\s+обслуж", re.I), 6),
    ("toir", re.compile(r"\bТОи?Р\b|регламентн\w*\s+работ", re.I), 6),
    ("periodicity", re.compile(r"периодич|межремонтн|интервал\w*\s+обслуж", re.I), 5),
    ("is-code", re.compile(r"\bIS\s*(?:100|200|510|520|530|540|600|700)\b", re.I), 5),
    ("repair", re.compile(r"\bремонт\w*\b|восстановлен\w*", re.I), 3),
    ("material", re.compile(r"материал\w*|расходн\w*|смаз\w*|масл\w*|\bЗИП\b", re.I), 3),
    ("criterion", re.compile(r"критери\w*|не\s+допуска|не\s+более|не\s+менее|предельн\w*|износ", re.I), 3),
    ("actions", re.compile(r"\b(?:осмотр|инспекц|ревизи|проверк|контрол|очист|замен)\w*", re.I), 1),
    ("units", re.compile(r"\b(?:км|сут\w*|дн\w*|лет|год\w*|цикл\w*|моточас\w*|час\w*)\b", re.I), 1),
)


def score_page(text: str, page: int, ocr_text_threshold: int = 80) -> PageSignal:
    compact = " ".join((text or "").split())
    score = 0; reasons: list[str] = []
    for name, pattern, weight in SCAN_RULES:
        if pattern.search(compact):
            score += weight; reasons.append(name)
    return PageSignal(page=page, score=score, reasons=reasons, text_length=len(compact), needs_ocr=len(compact) < ocr_text_threshold)


def choose_candidate_pages(page_texts: Iterable[str], threshold: int = 5, neighbor_radius: int = 1) -> tuple[list[PageSignal], list[int]]:
    signals = [score_page(text, i + 1) for i, text in enumerate(page_texts)]
    chosen = {s.page for s in signals if s.score >= threshold}
    expanded = set(chosen)
    for page in chosen:
        for delta in range(-neighbor_radius, neighbor_radius + 1):
            p = page + delta
            if 1 <= p <= len(signals): expanded.add(p)
    return signals, sorted(expanded)


def pages_to_ranges(pages: Iterable[int]) -> list[tuple[int, int]]:
    values = sorted(set(int(p) for p in pages))
    if not values: return []
    out: list[tuple[int, int]] = []; start = prev = values[0]
    for value in values[1:]:
        if value == prev + 1: prev = value; continue
        out.append((start, prev)); start = prev = value
    out.append((start, prev)); return out


def _num(value: str) -> float:
    return float(value.replace("\u00a0", "").replace(" ", "").replace(",", "."))


def canonical_is(text: str) -> str | None:
    m = re.search(r"\bIS\s*(100|200|510|520|530|540|600|700)\b", str(text), re.I)
    return f"IS{m.group(1)}" if m else None


def parse_interval(text: str) -> IntervalRule | None:
    raw = " ".join(str(text).replace("−", "-").replace("–", "-").split()); low = raw.lower()
    if not raw: return None
    unit = "unknown"
    for candidate, pattern in [
        ("km", r"\b(?:км|километр\w*)\b"), ("day", r"\b(?:сут\w*|дн(?:я|ей|и)?|день)\b"),
        ("month", r"\bмесяц\w*\b"), ("year", r"\b(?:лет|год\w*)\b"),
        ("cycle", r"\b(?:цикл\w*|срабатывани\w*)\b"), ("hour", r"\b(?:моточас\w*|час\w*)\b")]:
        if re.search(pattern, low): unit = candidate; break
    number = r"(\d+(?:[\s\u00a0]\d{3})*(?:[.,]\d+)?)"; space = r"[\s\u00a0]*"
    m = re.search(number + space + r"(?:км)?" + space + r"[±+]" + space + number + space + r"%", raw, re.I)
    if m: return IntervalRule(verbatim=raw, value=_num(m.group(1)), unit=unit, qualifier="exact", tolerance_percent=_num(m.group(2)))
    m = re.search(number + space + r"[-–]" + space + number, raw)
    if m and unit != "unknown": return IntervalRule(verbatim=raw, value=_num(m.group(1)), value_max=_num(m.group(2)), unit=unit, qualifier="range")
    qualifier = "max" if re.search(r"не\s+(?:позднее|более)|максим", low) else "min" if re.search(r"не\s+(?:ранее|менее)|миним", low) else "exact"
    m = re.search(r"(?:\d+\s*раз\w*\s+)?(?:в|за)\s+" + number + space + r"(сут\w*|дн\w*|месяц\w*|год\w*|лет|час\w*|цикл\w*)", low)
    if m: return IntervalRule(verbatim=raw, value=_num(m.group(1)), unit=unit, qualifier=qualifier)
    m = re.search(number, raw)
    if m and unit != "unknown": return IntervalRule(verbatim=raw, value=_num(m.group(1)), unit=unit, qualifier=qualifier)
    if re.search(r"при\s+(?:кажд|необходим|обнаруж|замен|ремонт)", low): return IntervalRule(verbatim=raw, unit="event", qualifier="event")
    return None


class TableKind(StrEnum):
    PERIODICITY = "periodicity"; OPERATION_MATRIX = "operation_matrix"; OPERATION_LIST = "operation_list"
    MATERIALS = "materials"; CRITERIA = "criteria"; UNKNOWN = "unknown"


def _norm(value: object) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).lower()


def classify_table(rows: Sequence[Sequence[object]]) -> TableKind:
    if not rows: return TableKind.UNKNOWN
    header = " | ".join(_norm(cell) for row in rows[:3] for cell in row)
    is_count = len(set(re.findall(r"is\s*(?:100|200|510|520|530|540|600|700)", header, re.I)))
    if ("периодич" in header or "межремонт" in header) and ("вид" in header or is_count): return TableKind.PERIODICITY
    if is_count >= 3 and any(k in header for k in ("работ", "операц", "элемент", "обслужив")): return TableKind.OPERATION_MATRIX
    if all(k in header for k in ("документ", "работ")) and ("элемент" in header or "пункт" in header): return TableKind.OPERATION_LIST
    if any(k in header for k in ("материал", "смаз", "жидкост", "зип")): return TableKind.MATERIALS
    if any(k in header for k in ("критери", "допуст", "предельн", "параметр")): return TableKind.CRITERIA
    return TableKind.UNKNOWN


def extract_periodicity_rows(rows: Sequence[Sequence[object]]) -> dict[str, IntervalRule]:
    result: dict[str, IntervalRule] = {}
    for row in rows:
        mtype = canonical_is(" | ".join(str(c or "") for c in row))
        if not mtype: continue
        for cell in row:
            parsed = parse_interval(str(cell or ""))
            if parsed and parsed.value is not None:
                result[mtype] = parsed; break
    return result


def detect_matrix_columns(header_rows: Sequence[Sequence[object]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in header_rows:
        for idx, cell in enumerate(row):
            text = _norm(cell)
            for name in MAINTENANCE_TYPES:
                if name.startswith("IS") and canonical_is(text) == name: result.setdefault(name, idx)
                elif not name.startswith("IS") and re.fullmatch(rf"{name.lower()}[.)]?", text): result.setdefault(name, idx)
    return result


def marks_from_row(row: Sequence[object], columns: dict[str, int]) -> MatrixMarks:
    values = {}
    for name, idx in columns.items():
        cell = _norm(row[idx]) if idx < len(row) else ""
        values[name] = cell in {"+", "х", "x", "●", "•", "да", "1"}
    return MatrixMarks(**values)


@dataclass(frozen=True)
class ComponentRecord:
    code: str
    name: str


@dataclass(frozen=True)
class MatchResult:
    code: str | None; name: str | None; score: float; method: str; needs_review: bool


def normalize_name(value: str) -> str:
    return " ".join(re.sub(r"[^a-zа-я0-9]+", " ", value.lower().replace("ё", "е"), flags=re.I).split())


def match_component(query: str, components: list[ComponentRecord], aliases: dict[str, str] | None = None) -> MatchResult:
    aliases = aliases or {}; nq = normalize_name(query)
    if not nq: return MatchResult(None, None, 0, "empty", True)
    by_norm = {normalize_name(c.name): c for c in components}
    for comp in components:
        if re.search(rf"(?<![a-z0-9]){re.escape(comp.code.lower())}(?![a-z0-9])", query.lower()): return MatchResult(comp.code, comp.name, 100, "code", False)
    if nq in aliases:
        code = aliases[nq]; comp = next((c for c in components if c.code == code), None)
        return MatchResult(code, comp.name if comp else None, 100, "alias", comp is None)
    if nq in by_norm:
        comp = by_norm[nq]; return MatchResult(comp.code, comp.name, 100, "exact_name", False)
    hit = process.extractOne(nq, list(by_norm), scorer=fuzz.token_set_ratio)
    if not hit: return MatchResult(None, None, 0, "none", True)
    matched, score, _ = hit; comp = by_norm[matched]
    return MatchResult(comp.code if score >= 75 else None, comp.name if score >= 75 else None, float(score), "fuzzy", score < 90)
