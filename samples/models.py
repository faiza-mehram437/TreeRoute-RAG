"""Data models used by the citation sample."""

from pydantic import BaseModel, Field


class PaperInfo(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None


class Citations(BaseModel):
    apa: str
    mla: str
    bibtex: str
