from datetime import datetime, timezone

from throughline_connector_kit.contract import AuthContext, NormalizedRecord
from throughline_connector_kit.engine import InMemoryDestination


def test_normalized_record_key_is_destination_neutral() -> None:
    record = NormalizedRecord(
        source_system="synthetic_crm",
        entity_type="accounts",
        source_id="acct_001",
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        payload={"name": "Example Robotics"},
    )

    assert record.key == ("synthetic_crm", "accounts", "acct_001")


def test_destination_reports_create_then_update() -> None:
    destination = InMemoryDestination()
    record = NormalizedRecord(
        source_system="synthetic_crm",
        entity_type="accounts",
        source_id="acct_001",
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        payload={"name": "Example Robotics"},
    )

    assert destination.upsert(record) == "created"
    assert destination.upsert(record) == "updated"


def test_auth_context_keeps_public_example_secret_free() -> None:
    context = AuthContext(principal="synthetic-demo", scopes=("read:accounts",))

    assert context.principal == "synthetic-demo"
    assert context.scopes == ("read:accounts",)
