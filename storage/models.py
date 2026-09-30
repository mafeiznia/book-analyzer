"""Data models — dataclass-style for internal use."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: int | None
    title: str
    author: str
    urls: str = ""          # JSON array
    snippet: str = ""
    status: str = "draft"
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Analysis:
    id: int | None
    project_id: int
    version: int
    provider: str
    model: str
    result_json: str
    translation_prompt: str = ""
    sources_used: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    created_at: datetime | None = None