from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from .adapters import DoclingAdapter, PyPdfAdapter
from .core import PageSignal, choose_candidate_pages, pages_to_ranges
from .storage import sha256_file


@dataclass
class ScanResult:
    sha256: str
    signals: list[PageSignal]
    candidate_pages: list[int]
    ranges: list[tuple[int,int]]


class MaintenancePipeline:
    def __init__(self, scan_threshold: int = 5, neighbor_radius: int = 1):
        self.scan_threshold = scan_threshold
        self.neighbor_radius = neighbor_radius
        self.fast = PyPdfAdapter()

    def scan_pdf(self, path: str | Path) -> ScanResult:
        path=Path(path); texts=self.fast.page_texts(path)
        signals,pages=choose_candidate_pages(texts,self.scan_threshold,self.neighbor_radius)
        return ScanResult(sha256_file(path),signals,pages,pages_to_ranges(pages))

    def deep_parse_selected(self, path: str | Path, ranges: list[tuple[int,int]], *, artifacts_path: str | Path | None = None, enable_ocr: bool = False):
        parser=DoclingAdapter(artifacts_path=artifacts_path,enable_ocr=enable_ocr)
        return [parser.parse_range(path,start,end) for start,end in ranges]


@contextmanager
def secure_temp_copy(source: str | Path):
    suffix=Path(source).suffix; fd,temp_name=tempfile.mkstemp(prefix="techdoc-",suffix=suffix); os.close(fd)
    try:
        shutil.copy2(source,temp_name); yield Path(temp_name)
    finally:
        try: Path(temp_name).unlink(missing_ok=True)
        except OSError: pass
