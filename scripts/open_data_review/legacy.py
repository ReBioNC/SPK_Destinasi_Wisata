"""Read legacy files as candidates, not facts about live destinations."""

import math
import re
from pathlib import Path

import pandas as pd

from .schema import Candidate


SYNTHETIC_UNTRUSTED = (
    "Place_Name", "Description", "Category", "Sub_Category", "City", "Province",
    "Price", "Rating", "Time_Minutes", "Coordinate", "Lat", "Long", "Facilities",
)
KAGGLE_UNTRUSTED = (
    "Description", "Category", "Price", "Rating", "Time_Minutes", "Coordinate",
    "Lat", "Long", "Facilities",
)


def _plain(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return value.item() if hasattr(value, "item") else value


def _text(value) -> str:
    value = _plain(value)
    return "" if value is None else str(value).strip()


def _rows(frame, origin: str, path: Path, flags: tuple[str, ...]):
    for ordinal, (_, row) in enumerate(frame.iterrows(), 1):
        raw = {str(key): _plain(value) for key, value in row.items()}
        name = _text(raw.get("Place_Name"))
        source_row_id = _text(raw.get("Place_Id")) or str(ordinal)
        # Ordinal remains stable even if the source's Place_Id is repeated.
        yield Candidate(
            candidate_id=f"{origin}:{ordinal}", origin=origin, name=name,
            city=_text(raw.get("City")), province=_text(raw.get("Province")),
            source_row_id=source_row_id, source_path=str(path), raw=raw,
            untrusted_fields=flags,
            possible_filler_name=origin == "synthetic_1900" and bool(re.search(r"\s\d+$", name)),
        )


def load_legacy_candidates(xlsx_path: Path, kaggle_csv_path: Path) -> list[Candidate]:
    """Return every original row with origin and trust warnings; never edit inputs."""
    xlsx_path, kaggle_csv_path = Path(xlsx_path), Path(kaggle_csv_path)
    xlsx = pd.read_excel(xlsx_path)
    kaggle = pd.read_csv(kaggle_csv_path)
    return [
        *_rows(xlsx, "synthetic_1900", xlsx_path, SYNTHETIC_UNTRUSTED),
        *_rows(kaggle, "kaggle_437", kaggle_csv_path, KAGGLE_UNTRUSTED),
    ]
