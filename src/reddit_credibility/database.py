from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, TypeVar

import pandas as pd
from pydantic import BaseModel

from reddit_credibility.config import Settings
from reddit_credibility.schemas import ExtractedClaim, RedditItem, ReviewedClaim, ValidatedClaim

TModel = TypeVar("TModel", bound=BaseModel)


def ensure_data_dirs(settings: Settings) -> None:
    for child in ("raw", "processed", "reports"):
        (settings.data_dir / child).mkdir(parents=True, exist_ok=True)


def raw_reddit_path(settings: Settings, username: str) -> Path:
    return settings.data_dir / "raw" / f"{username}_reddit.json"


def claims_json_path(settings: Settings, username: str) -> Path:
    return settings.data_dir / "processed" / f"{username}_claims.json"


def claims_csv_path(settings: Settings, username: str) -> Path:
    return settings.data_dir / "processed" / f"{username}_claims.csv"


def review_csv_path(settings: Settings, username: str) -> Path:
    return settings.data_dir / "processed" / f"{username}_review.csv"


def validated_csv_path(settings: Settings, username: str) -> Path:
    return settings.data_dir / "processed" / f"{username}_validated.csv"


def report_path(settings: Settings, username: str) -> Path:
    return settings.data_dir / "reports" / f"{username}_report.md"


def save_json_models(path: Path, models: Iterable[BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [model.model_dump(mode="json") for model in models]
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def load_json_models(path: Path, model_type: type[TModel]) -> list[TModel]:
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [model_type.model_validate(row) for row in rows]


def save_raw_items(settings: Settings, username: str, items: list[RedditItem]) -> Path:
    path = raw_reddit_path(settings, username)
    save_json_models(path, items)
    return path


def load_raw_items(settings: Settings, username: str) -> list[RedditItem]:
    return load_json_models(raw_reddit_path(settings, username), RedditItem)


def save_claims(settings: Settings, username: str, claims: list[ExtractedClaim]) -> tuple[Path, Path]:
    json_path = claims_json_path(settings, username)
    csv_path = claims_csv_path(settings, username)
    save_json_models(json_path, claims)
    save_models_csv(csv_path, claims)
    return json_path, csv_path


def load_claims(settings: Settings, username: str) -> list[ExtractedClaim]:
    return load_json_models(claims_json_path(settings, username), ExtractedClaim)


def save_models_csv(path: Path, models: Iterable[BaseModel]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [model.model_dump(mode="json") for model in models]
    pd.DataFrame(rows).to_csv(path, index=False)


def save_review_csv(settings: Settings, username: str, claims: list[ExtractedClaim]) -> Path:
    reviewed = [ReviewedClaim(**claim.model_dump(), manual_status="pending") for claim in claims]
    path = review_csv_path(settings, username)
    save_models_csv(path, reviewed)
    return path


def load_review_csv(path: Path) -> list[ReviewedClaim]:
    if not path.exists():
        return []
    frame = pd.read_csv(path)
    return [
        ReviewedClaim.model_validate(_clean_csv_record(row))
        for row in frame.to_dict(orient="records")
    ]


def save_validated_claims(
    settings: Settings, username: str, claims: list[ValidatedClaim]
) -> Path:
    path = validated_csv_path(settings, username)
    save_models_csv(path, claims)
    return path


def load_validated_claims(settings: Settings, username: str) -> list[ValidatedClaim]:
    path = validated_csv_path(settings, username)
    if not path.exists():
        return []
    frame = pd.read_csv(path)
    return [
        ValidatedClaim.model_validate(_clean_csv_record(row))
        for row in frame.to_dict(orient="records")
    ]


def _clean_csv_record(row: dict[str, object]) -> dict[str, object | None]:
    return {key: (None if pd.isna(value) else value) for key, value in row.items()}
