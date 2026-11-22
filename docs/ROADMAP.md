# Yol Haritası (Roadmap)

## v1.0 — Mevcut (2026-09)

- mDNS keşfi, PIN korumalı P2P transfer (AES-256-GCM, streaming)
- Mesh relay (3 hop, parça SHA-256), WebRTC data channel,
  SQLite asenkron kuyruk
- GTK4/Adw 6 sekmeli arayüz, CLI, i18n (tr/en)
- ~550 test, benchmarklar, güvenlik denetimi

## v1.1 — Tamamlananlar (2026-09)

- [x] WebRTC çerçeve parçalama (64 KB üstü kareler; 200 KB ~19 ms)
- [x] Kaldığı yerden devam eden dosya transferi (resume, 0x03 modu)
- [x] Bütünlük doğrulamalı normal mod (SHA-256, 0x04 modu)
- [x] Hız/ETA göstergesi (ilerleme çubuğuna bağlı)

## v1.2 — Tamamlananlar (2026-11)
- [x] Mesh otomatik yol seçimi (en düşük gecikmeli relay + `FRAG_PING`/`FRAG_PONG` RTT + EWMA)
- [x] Otomatik GPL-3.0 lisans uyumluluk CI kapısı (`scripts/check_licenses.py`) + DEP-5 `debian/copyright`
- [x] Performans regresyon CI kapısı (`tests/test_perf_regression.py`)
- [x] Python 3.10/3.11/3.12 + Windows + GTK + Pardus 23 Docker `.deb` tam CI & Release hattı

## v1.3 — Birlikte Çalışabilirlik (Gelecek Hedefler)

- [ ] LocalSend protokolü ile dosya alışverişi
- [ ] KDE Connect bildirim köprüsü
- [ ] Wayland uzaktan kontrol (xdg-desktop-portal RemoteDesktop)
- [ ] Ek dil: Almanca, Arapça

## v2.0 — Vizyon (hedef: +6 ay)

- [ ] Uçtan uca şifreli grup paylaşımı
- [ ] Bağımsız güvenlik denetimi (penetrasyon testi)
