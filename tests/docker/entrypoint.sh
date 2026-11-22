#!/bin/bash
set -e

if [ ! -f "/app/pardus-paylasim.deb" ]; then
    echo "[HATA] /app/pardus-paylasim.deb bulunamadı!"
    exit 1
fi

echo "[Pardus Test] Lintian (Debian Paket Analizi) Çalıştırılıyor..."
lintian --no-tag-display-limit /app/pardus-paylasim.deb || true

echo "[Pardus Test] Paket Kurulumu (dpkg/apt)..."
apt-get update
apt-get install -y /app/pardus-paylasim.deb

echo "[Pardus Test] Geçerli Test Görseli Oluşturuluyor..."
python3 -c '
from PIL import Image
im = Image.new("RGB", (64, 64), color=(57, 73, 171))
im.save("/tmp/dummy.png", format="PNG")
'

echo "[Pardus Test] CLI Testleri (--clean, --mask, --mesh-status)..."
pardus-paylasim --clean /tmp/dummy.png --out /tmp/dummy_clean.png
file /tmp/dummy_clean.png
pardus-paylasim --mask "TCKN: 10000000146"
pardus-paylasim --mesh-status

echo "[Pardus Test] Headless GUI Testi (Xvfb + Cairo GSK + DBus ile başlatma)..."
export $(dbus-launch)
export GSK_RENDERER=cairo
export LIBGL_ALWAYS_SOFTWARE=1
xvfb-run -a pardus-paylasim >/tmp/gui.log 2>&1 &
APP_PID=$!
sleep 3
if kill -0 $APP_PID 2>/dev/null; then
    echo "[Pardus Test] GTK arayüzü çökmeden başarıyla başlatıldı!"
    kill $APP_PID || true
else
    echo "[HATA] GTK arayüzü başlatılırken çöktü (Fatal Error)!"
    tail -n 20 /tmp/gui.log || true
    exit 1
fi

echo ""
echo "==========================================="
echo "⚙️ Pardus Backend Testleri Çalıştırılıyor (Config & P2P & AES)..."
echo "==========================================="
export PYTHONPATH="/usr/lib/python3/dist-packages"
pytest /app/test_backend.py -v

echo ""
echo "==========================================="
echo "🧪 Pardus Turing Testleri (Fonksiyonel) Başlıyor..."
echo "==========================================="
python3 /app/test_turing.py

# Kurulu .deb paketi üzerinde çekirdek protokol, mesh yönlendirme ve performans testleri
if [ -d "/app/project-tests" ]; then
    echo ""
    echo "==========================================="
    echo "📦 Kurulu Paket Entegrasyon Testleri (Mesh, Relay, Performans)..."
    echo "==========================================="
    pytest \
      /app/project-tests/test_mesh_relay.py \
      /app/project-tests/test_mesh_routing.py \
      /app/project-tests/test_perf_regression.py \
      /app/project-tests/test_innovations.py \
      -v
fi

echo "[Pardus Test] Tüm testler BAŞARILI!"
