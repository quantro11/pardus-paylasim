"""Çekirdek sıcak-yollar için CI performans regresyon kapısı.

Eşikler paylaşımlı CI sunucularında sahte alarm vermeyecek, ancak gerçek
10x performans gerilemesini anında yakalayacak şekilde belirlenmiştir.
"""

import os
import time

import pytest

from pardus_paylasim.clipboard.sensitive_masker import SensitiveMasker
from pardus_paylasim.discovery.async_transfer.manager import AsyncTransfer, AsyncTransferStore
from pardus_paylasim.discovery.mesh.mesh_network import FRAG_DATA, MeshProtocol


@pytest.mark.unit
def test_masking_latency_budget():
    sample = "Toplantı notu: Ahmet Yılmaz (a.yilmaz@ornek.com), TCKN 10000000146, tel 0532 123 45 67."
    # Isınma
    for _ in range(20):
        SensitiveMasker.mask_text(sample)
    iterations = 300
    t0 = time.perf_counter()
    for _ in range(iterations):
        SensitiveMasker.mask_text(sample)
    mean_ms = ((time.perf_counter() - t0) * 1000.0) / iterations
    assert mean_ms < 5.0, f"Maskeleme gecikmesi eşiği aştı: {mean_ms:.3f} ms"


@pytest.mark.unit
def test_mesh_64kb_pack_unpack_budget():
    chunk = os.urandom(64 * 1024)
    key = b"k" * 32
    iterations = 200
    t0 = time.perf_counter()
    for _ in range(iterations):
        pkt = MeshProtocol.pack_fragment(
            FRAG_DATA, "bench001", 0, 1, chunk, "peer_a", 0, "a" * 32, auth_key=key
        )
        unpacked = MeshProtocol.unpack_fragment(pkt, auth_key=key)
        assert unpacked is not None
    mean_ms = ((time.perf_counter() - t0) * 1000.0) / iterations
    assert mean_ms < 10.0, f"Mesh 64KB pack+unpack+HMAC gecikmesi eşiği aştı: {mean_ms:.3f} ms"


@pytest.mark.unit
def test_async_sqlite_queue_budget(tmp_path):
    store = AsyncTransferStore(db_path=str(tmp_path / "perf.db"))
    try:
        iterations = 100
        t0 = time.perf_counter()
        for i in range(iterations):
            store.queue_transfer(
                AsyncTransfer(
                    id=f"p{i}",
                    file_name="f.txt",
                    file_size=1024,
                    file_hash=f"h{i}",
                    sender_id="s",
                    sender_name="S",
                    receiver_id="r",
                    status="pending",
                    file_path="/tmp/f.txt",
                )
            )
        mean_ms = ((time.perf_counter() - t0) * 1000.0) / iterations
        assert mean_ms < 50.0, f"SQLite kuyruk yazma gecikmesi eşiği aştı: {mean_ms:.3f} ms"
    finally:
        store.close()
