from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)

    for source in (ROOT / "app" / "static").glob("*"):
        if source.is_file():
            copy_file(source, PUBLIC / source.name)

    for source in (ROOT / "assets").glob("*"):
        if source.is_file():
            copy_file(source, PUBLIC / "assets" / source.name)

    copy_file(ROOT / "wechat-qrcode.jpg", PUBLIC / "wechat-qrcode.jpg")


if __name__ == "__main__":
    main()
