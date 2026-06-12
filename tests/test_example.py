from datetime import datetime, timezone

from throughline_connector_kit.engine import InMemoryDestination, SyncEngine
from throughline_connector_kit.example import SyntheticCrmConnector, run_example


def test_example_syncs_accounts_before_contacts() -> None:
    results, destination = run_example()

    assert list(results) == ["accounts", "contacts"]
    assert results["accounts"].created == 2
    assert results["contacts"].created == 2
    assert results["accounts"].failed == 0
    assert len(destination.records) == 4


def test_incremental_sync_uses_checkpoints() -> None:
    connector = SyntheticCrmConnector()
    engine = SyncEngine(connector, InMemoryDestination())

    first = engine.sync()
    second = engine.sync()

    assert first["accounts"].created == 2
    assert first["contacts"].created == 2
    assert second["accounts"].created == 0
    assert second["contacts"].created == 0
    assert second["accounts"].updated == 0
    assert second["contacts"].updated == 0


def test_entity_subset_keeps_custom_order_warning_out_of_connector() -> None:
    connector = SyntheticCrmConnector()
    engine = SyncEngine(connector, InMemoryDestination())

    results = engine.sync(entity_types=["contacts"], incremental=False)

    assert list(results) == ["contacts"]
    assert results["contacts"].created == 2


def test_checkpoint_tracks_latest_record_timestamp() -> None:
    connector = SyntheticCrmConnector()
    engine = SyncEngine(connector, InMemoryDestination())

    results = engine.sync(entity_types=["accounts"])

    assert results["accounts"].checkpoint == datetime(2026, 1, 3, 9, 30, tzinfo=timezone.utc)
