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

# GPL-3.0 ile kesin uyumlu OSI lisans belirteçleri.
COMPATIBLE_MARKERS = (
    "mit",
    "bsd",
    "apache-2.0",
    "apache software license",
    "psf",
    "python software foundation",
    "hpnd",
    "isc",
    "unlicense",
    "lgpl-2.1",
    "lgpl-3",
    "lesser general public license",
    "gpl-3",
    "mpl-2.0",
)

# GPL-3.0 ile uyumsuz lisans belirteçleri (yalnız uyumlu OSI lisansı yoksa reddedilir).
HARD_INCOMPATIBLE_MARKERS = (
    "sspl",
    "gpl-2.0-only",
    "gplv2 only",
)


def extract_license(dist: metadata.Distribution) -> str:
    meta = dist.metadata
    spdx = meta.get("License-Expression")
    if spdx and spdx.strip():
        return spdx.strip()
    all_classifiers = [
        c.split("::")[-1].strip()
        for c in (meta.get_all("Classifier") or [])
        if c.startswith("License ::")
    ]
    osi_classifiers = [
        c.split("::")[-1].strip()
        for c in (meta.get_all("Classifier") or [])
        if c.startswith("License :: OSI Approved ::")
    ]
    if osi_classifiers:
        return " / ".join(osi_classifiers)
    raw = (meta.get("License") or "").strip().splitlines()
    if raw and raw[0].strip():
        return raw[0].strip()[:100]
    if all_classifiers:
        return " / ".join(all_classifiers)
    return "UNKNOWN"


def is_gpl3_compatible(license_text: str) -> bool:
    low = license_text.lower()
    if any(bad in low for bad in HARD_INCOMPATIBLE_MARKERS):
        return False
    if any(ok in low for ok in COMPATIBLE_MARKERS):
        return True
    return "proprietary" not in low


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
        if not is_gpl3_compatible(lic):
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
