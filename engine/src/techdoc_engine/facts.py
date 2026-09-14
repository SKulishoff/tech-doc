from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .core import ReviewStatus, SourceLocator


class MaterialFact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    quantity: float | None = None
    unit: str | None = None
    component_code: str | None = None
    maintenance_type: str | None = None
    source: SourceLocator
    review_status: ReviewStatus = ReviewStatus.NEED_REVIEW


class CriterionFact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parameter: str
    comparator: str | None = None
    value: float | None = None
    value_max: float | None = None
    unit: str | None = None
    verbatim: str
    component_code: str | None = None
    operation_code: str | None = None
    source: SourceLocator
    review_status: ReviewStatus = ReviewStatus.NEED_REVIEW
