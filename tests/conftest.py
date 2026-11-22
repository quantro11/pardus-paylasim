"""Ortak test yapılandırması: deterministik Türkçe kaynak dil izolasyonu.

Ubuntu/CI sunucularında `LANG=en_US.UTF-8` olduğunda gettext İngilizce `.mo`
kataloğunu yükleyip Türkçe mesaj bekleyen birim testlerini kırabiliyordu.
Bu fixture her test öncesi varsayılan olarak kaynak dili (TR) yükler;
`TestI18n.test_english_translation` gibi testler kendi içinde `LANGUAGE=en`
ile çeviriyi açıkça sınamaya devam eder.
"""

import pytest

from pardus_paylasim import i18n


@pytest.fixture(autouse=True)
def _reset_default_locale(monkeypatch):
    monkeypatch.setenv("LANGUAGE", "tr")
    monkeypatch.setenv("LANG", "tr_TR.UTF-8")
    i18n.setup_i18n()
    yield
    i18n.setup_i18n()
