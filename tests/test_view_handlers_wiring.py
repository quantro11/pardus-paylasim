"""UI ViewHandler ve MainWindow başlangıç kablolama regresyon testleri."""

from pardus_paylasim.auth.trust_store import TrustStore
from pardus_paylasim.config import AppConfig
from pardus_paylasim.ui.mesh_view import MeshViewHandler
from pardus_paylasim.ui.settings_view import SettingsViewHandler


def test_settings_view_handler_and_trust_store_roundtrip(tmp_path):
    store = TrustStore(file_path=str(tmp_path / "trusted.json"))
    handler = SettingsViewHandler(config=AppConfig(), trust_store=store)

    fp = "a" * 64
    handler.add_trusted_device(fp, "Tahta 9A", "192.168.1.42")
    assert handler.is_trusted(fp) is True
    listed = handler.get_trusted_devices()
    assert fp in listed
    assert listed[fp]["device_name"] == "Tahta 9A"
    assert handler.remove_trusted_device(fp) is True
    assert handler.is_trusted(fp) is False


def test_trust_store_singleton_get_instance():
    s1 = TrustStore.get_instance()
    s2 = TrustStore.get_instance()
    assert s1 is s2
    # Varsayılan SettingsViewHandler çökmeden başlatılabilmeli.
    handler = SettingsViewHandler()
    assert handler.trust_store is s1


def test_mesh_view_handler_add_and_list_peers():
    handler = MeshViewHandler()
    node = handler.ensure_node(peer_id="test_ui", local_ip="127.0.0.1", port=0)
    assert handler.add_peer("127.0.0.1", 8999, peer_id="peer1") is True
    peers = handler.get_peers()
    assert len(peers) == 1
    assert peers[0].peer_id == "peer1"
    assert peers[0].port == 8999
    assert handler.get_stats()["peers_count"] == 1
    assert node is handler.node


def test_main_window_headless_init_does_not_crash():
    """MainWindow(app=None) tüm 7 handler ve sunucularla çökmeden başlamalı."""
    from pardus_paylasim.window import MainWindow

    win = MainWindow(app=None)
    try:
        assert win.settings_handler is not None
        assert win.mesh_handler is not None
        assert win.classroom_handler is not None
        assert win.privacy_handler is not None
        assert win.discovery_handler is not None
        assert win.screen_handler is not None
        assert win.clipboard_handler is not None
    finally:
        win.receiver.stop()
        win.clipboard_server.stop()
