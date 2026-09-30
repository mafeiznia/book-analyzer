"""Pydantic schemas for LLM analysis output (bilingual fa/en)."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Bilingual(BaseModel):
    """A bilingual string with Persian and English versions.

    For backward compatibility, if a plain string is given, it is used for both.
    """

    fa: str = Field(description="Persian version (فارسی)")
    en: str = Field(description="English version")

    @model_validator(mode="before")
    @classmethod
    def _coerce_plain_string(cls, v):
        if isinstance(v, str):
            return {"fa": v, "en": v}
        return v


class GenreInfo(BaseModel):
    primary: Bilingual
    secondary: Bilingual | None = None
    notes: Bilingual


class ToneInfo(BaseModel):
    description: Bilingual
    examples: list[Bilingual] = Field(default_factory=list)


class StyleInfo(BaseModel):
    sentence_length: Bilingual
    narrative_voice: Bilingual
    vocabulary: Bilingual
    notable_features: list[Bilingual] = Field(default_factory=list)


class TranslationNote(BaseModel):
    topic: Bilingual
    issue: Bilingual
    suggestion: Bilingual


class Analysis(BaseModel):
    genre: GenreInfo
    tone: ToneInfo
    style: StyleInfo
    translation_notes: list[TranslationNote] = Field(default_factory=list)
    confidence: Literal["Confirmed", "Probable", "Unknown"]
    sources_used: list[str] = Field(default_factory=list)