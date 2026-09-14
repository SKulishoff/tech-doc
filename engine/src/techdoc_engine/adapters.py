from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader


class PyPdfAdapter:
    def page_texts(self, path: str | Path) -> list[str]:
        reader = PdfReader(str(path))
        result: list[str] = []
        for page in reader.pages:
            try:
                result.append(page.extract_text() or "")
            except Exception:
                result.append("")
        return result


@dataclass
class ParsedRange:
    start_page: int
    end_page: int
    document: Any
    tables: list[list[list[object]]]


class DoclingAdapter:
    """Local Docling wrapper. Lazy import keeps rule/unit tests light."""

    def __init__(self, artifacts_path: str | Path | None = None, enable_ocr: bool = False):
        self.artifacts_path = Path(artifacts_path) if artifacts_path else None
        self.enable_ocr = enable_ocr

    def _converter(self):
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        opts = PdfPipelineOptions()
        opts.do_ocr = self.enable_ocr
        opts.do_table_structure = True
        opts.generate_page_images = False
        opts.generate_picture_images = False
        opts.enable_remote_services = False
        opts.allow_external_plugins = False
        if self.artifacts_path:
            opts.artifacts_path = self.artifacts_path
        return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})

    def parse_range(self, path: str | Path, start_page: int, end_page: int) -> ParsedRange:
        converter = self._converter()
        result = converter.convert(str(path), page_range=(start_page, end_page))
        tables: list[list[list[object]]] = []
        for table in result.document.tables:
            df = table.export_to_dataframe(doc=result.document)
            rows = [list(df.columns)] + df.astype(object).where(df.notna(), None).values.tolist()
            tables.append(rows)
        return ParsedRange(start_page, end_page, result.document, tables)


class ExcelAdapter:
    """Read old/new Excel families using python-calamine without pandas."""

    def rows(self, path: str | Path, sheet_name: str | None = None) -> list[list[object]]:
        from python_calamine import CalamineWorkbook

        book = CalamineWorkbook.from_path(str(path))
        if sheet_name is None:
            sheet_name = book.sheet_names[0]
        return book.get_sheet_by_name(sheet_name).to_python()
