#!/usr/bin/env python3
"""Constrói o pacote independente e o manifesto de integridade da V2.6."""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THREAD = ROOT.parent.parent
RELEASE_NAME = "pih-ms-v2.6-prioridade-por-pergunta-experimental"
STAGE = THREAD / "release_v26" / RELEASE_NAME
OUTPUTS = THREAD / "outputs" / "6b2168c6942b"
WORKBOOK = OUTPUTS / "PIH_MS_PRIORIDADE_INVESTIGACAO_POR_PERGUNTA_V1.xlsx"
ZIP_PATH = OUTPUTS / f"{RELEASE_NAME}.zip"


def ignore(directory: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name == "__pycache__" or name.endswith(".pyc")}
    ignored.update(name for name in names if name.startswith(".well_requirement_status_long.csv."))
    return ignored


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if STAGE.exists():
        raise RuntimeError(f"A pasta de preparação já existe e não será sobrescrita automaticamente  {STAGE}")
    if not WORKBOOK.exists():
        raise FileNotFoundError(WORKBOOK)
    STAGE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, STAGE, ignore=ignore)
    shutil.copy2(WORKBOOK, STAGE / WORKBOOK.name)

    files = sorted(path for path in STAGE.rglob("*") if path.is_file() and path.name != "SHA256SUMS_V26.txt")
    lines = [f"{sha256(path)}  {path.relative_to(STAGE).as_posix()}" for path in files]
    (STAGE / "SHA256SUMS_V26.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                archive.write(path, Path(RELEASE_NAME) / path.relative_to(STAGE))

    with zipfile.ZipFile(ZIP_PATH) as archive:
        broken = archive.testzip()
        if broken is not None:
            raise RuntimeError(f"Entrada ZIP inválida  {broken}")
        members = len(archive.infolist())
    print(f"OK pacote  {ZIP_PATH}")
    print(f"Arquivos  {len(files) + 1}")
    print(f"Entradas ZIP  {members}")
    print(f"SHA256  {sha256(ZIP_PATH)}")


if __name__ == "__main__":
    main()
