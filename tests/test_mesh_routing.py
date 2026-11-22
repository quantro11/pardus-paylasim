"""Mesh otomatik yol seçimi (en düşük gecikmeli relay) ve RTT prob testleri."""

import os
import threading
import time

from pardus_paylasim.discovery.mesh.mesh_network import (
    MeshNode,
    MeshPeer,
    TransferJob,
)


def test_select_best_relays_prefers_lowest_latency_and_healthy_peers():
    node = MeshNode("node_src", "127.0.0.1", mesh_port=0)
    node.add_peer(MeshPeer(id="slow", ip="127.0.0.1", port=9001, latency_ms=85.0))
    node.add_peer(MeshPeer(id="fast", ip="127.0.0.1", port=9002, latency_ms=4.5))
    node.add_peer(MeshPeer(id="unknown", ip="127.0.0.1", port=9003, latency_ms=None))
    node.add_peer(
        MeshPeer(id="flaky", ip="127.0.0.1", port=9004, latency_ms=1.0, failure_count=2)
    )
    node.add_peer(
        MeshPeer(id="offline", ip="127.0.0.1", port=9005, latency_ms=0.5, is_online=False)
    )

    ordered = [p.id for p in node.select_best_relays(exclude_ids={"target"})]
    assert ordered == ["fast", "slow", "unknown", "flaky"]

    table = node.get_routing_table()
    assert table[0]["peer_id"] == "fast"
    assert table[0]["latency_ms"] == 4.5


def test_measure_peer_latency_real_ping_pong_and_auth():
    key = b"k" * 32
    node_a = MeshNode("node_a", "127.0.0.1", mesh_port=0, auth_key=key)
    node_b = MeshNode("node_b", "127.0.0.1", mesh_port=0, auth_key=key)
    try:
        node_a.start()
        node_b.start()
        node_a.add_peer(MeshPeer(id="node_b", ip="127.0.0.1", port=node_b.mesh_port))

        rtt = node_a.measure_peer_latency("node_b", timeout=2.0)
        assert rtt is not None and rtt >= 0.0
        assert node_a.peers["node_b"].latency_ms is not None
        assert node_a.peers["node_b"].failure_count == 0

        probed = node_a.probe_all_peers(timeout=2.0)
        assert probed["node_b"] is not None
    finally:
        node_a.stop()
        node_b.stop()


def test_lowest_latency_relay_selected_in_end_to_end_transfer(tmp_path):
    """A -> {fast_relay, slow_relay} -> C: A her zaman fast_relay üzerinden iletmeli."""
    payload = os.urandom(96 * 1024)
    src_file = tmp_path / "dosya.bin"
    src_file.write_bytes(payload)

    done = threading.Event()
    received = {}

    node_a = MeshNode("node_a", "127.0.0.1", mesh_port=0)
    fast_relay = MeshNode("fast_relay", "127.0.0.1", mesh_port=0)
    slow_relay = MeshNode("slow_relay", "127.0.0.1", mesh_port=0)
    node_c = MeshNode("node_c", "127.0.0.1", mesh_port=0)
    try:
        for n in (node_a, fast_relay, slow_relay, node_c):
            n.start()
        time.sleep(0.15)

        # Bilerek önce yavaş relay eklenir; en düşük gecikmeli fast_relay seçilmelidir.
        node_a.add_peer(
            MeshPeer(id="slow_relay", ip="127.0.0.1", port=slow_relay.mesh_port, latency_ms=120.0)
        )
        node_a.add_peer(
            MeshPeer(id="fast_relay", ip="127.0.0.1", port=fast_relay.mesh_port, latency_ms=2.0)
        )
        fast_relay.add_peer(MeshPeer(id="node_c", ip="127.0.0.1", port=node_c.mesh_port))
        slow_relay.add_peer(MeshPeer(id="node_c", ip="127.0.0.1", port=node_c.mesh_port))

        tid = "route001"
        total = (len(payload) + 64 * 1024 - 1) // (64 * 1024)
        node_c.transfers[tid] = TransferJob(
            transfer_id=tid,
            file_name="dosya.bin",
            file_size=len(payload),
            total_chunks=total,
            file_hash="",
        )
        node_c.on_transfer_complete = lambda _t, _n, data: (
            received.update(data=data),
            done.set(),
        )

        node_a.offer_file_mesh(tid, "dosya.bin", len(payload), str(src_file), target="node_c")
        assert done.wait(timeout=10.0), "En düşük gecikmeli relay aktarımı tamamlanamadı"
        assert received["data"] == payload
        assert len(fast_relay._relay_seen) == total
        assert len(slow_relay._relay_seen) == 0
    finally:
        for n in (node_a, fast_relay, slow_relay, node_c):
            n.stop()
