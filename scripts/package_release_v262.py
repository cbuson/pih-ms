#!/usr/bin/env python3
"""Constrói o pacote independente PIH MS V2.6.2."""
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THREAD = ROOT.parent.parent
OUTPUTS = THREAD / "outputs" / "6b2168c6942b"
RELEASE_NAME = "pih-ms-v2.6.2-controle-visual-camadas"
MANIFEST = ROOT / "SHA256SUMS_V262.txt"
ZIP_PATH = OUTPUTS / f"{RELEASE_NAME}.zip"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def package_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path != MANIFEST
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and not path.name.startswith(".")
    )


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    files = package_files()
    MANIFEST.write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in files) + "\n",
        encoding="utf-8",
    )
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in sorted([*files, MANIFEST]):
            archive.write(path, Path(RELEASE_NAME) / path.relative_to(ROOT))
    with zipfile.ZipFile(ZIP_PATH) as archive:
        broken = archive.testzip()
        if broken is not None:
            raise RuntimeError(f"Entrada ZIP inválida {broken}")
        members = len(archive.infolist())
    print(f"OK pacote {ZIP_PATH}")
    print(f"Arquivos {len(files) + 1}")
    print(f"Entradas ZIP {members}")
    print(f"SHA256 {sha256(ZIP_PATH)}")


if __name__ == "__main__":
    main()
