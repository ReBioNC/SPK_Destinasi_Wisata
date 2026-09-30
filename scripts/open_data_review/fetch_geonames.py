"""Download the one free GeoNames country archive, capped and without extraction."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile


URL = "https://download.geonames.org/export/dump/ID.zip"
MAX_BYTES = 30 * 1024 * 1024


def fetch(output: Path) -> dict:
    output = Path(output)
    if output.exists() or output.with_suffix(".source.json").exists():
        raise FileExistsError("Archive or receipt already exists")
    request = Request(URL, headers={"User-Agent": "TravelFit-academic-review/1.0"})
    with urlopen(request, timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("GeoNames archive exceeded size limit")
    with ZipFile(BytesIO(data)) as archive:
        if "ID.txt" not in archive.namelist():
            raise ValueError("Archive has no official ID.txt country file")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(data)
    receipt = {"source_url": URL,
               "retrieved_at": datetime.now(timezone.utc).date().isoformat(),
               "sha256": hashlib.sha256(data).hexdigest(),
               "license_ref": "https://download.geonames.org/export/dump/readme.txt"}
    with output.with_suffix(".source.json").open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
    return {"url": URL, "bytes": len(data), "path": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(fetch(args.output), sort_keys=True))


if __name__ == "__main__":
    main()
