"""GPL-3.0 bağımlılık lisans uyumluluğu denetleyici (CI kapısı).

Çevrimdışı ve CI ortamında ek paket gerektirmeden `importlib.metadata`
üzerinden kurulu çalışma zamanı bağımlılıklarının lisanslarını doğrular.
"""

from __future__ import annotations

import importlib.metadata as metadata
import sys

RUNTIME_PACKAGES = [
    "cryptography",
    "defusedxml",
    "filelock",
    "Pillow",
    "pyperclip",
    "qrcode",
    "websockets",
    "zeroconf",
]

# GPL-3.0 ile uyumsuz lisans anahtar sözcükleri (ör. GPL-2.0-only, AGPL/SSPL/Proprietary).
INCOMPATIBLE_MARKERS = (
    "proprietary",
    "sspl",
    "gpl-2.0-only",
    "gplv2 only",
    "wtfpl-incompatible",
)


def extract_license(dist: metadata.Distribution) -> str:
    meta = dist.metadata
    spdx = meta.get("License-Expression")
    if spdx:
        return spdx.strip()
    classifiers = [
        c.split("::")[-1].strip()
        for c in (meta.get_all("Classifier") or [])
        if c.startswith("License ::")
    ]
    if classifiers:
        return " / ".join(classifiers)
    raw = (meta.get("License") or "").strip().splitlines()
    return raw[0][:100] if raw else "UNKNOWN"


def main() -> int:
    failures: list[str] = []
    print(f"{'Paket':<18} {'Sürüm':<12} {'Lisans'}")
    print("-" * 72)
    for pkg in RUNTIME_PACKAGES:
        try:
            dist = metadata.distribution(pkg)
        except metadata.PackageNotFoundError:
            print(f"{pkg:<18} {'(kurulu değil)':<12} -")
            continue
        lic = extract_license(dist)
        print(f"{pkg:<18} {dist.version:<12} {lic}")
        low = lic.lower()
        if any(bad in low for bad in INCOMPATIBLE_MARKERS):
            failures.append(f"{pkg}: GPL-3.0 ile uyumsuz lisans ({lic})")

    if failures:
        print("\n[HATA] Lisans uyumluluk ihlalleri:")
        for f in failures:
            print("  -", f)
        return 1
    print("\n[OK] Tüm kurulu çalışma zamanı bağımlılıkları GPL-3.0 ile uyumlu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
