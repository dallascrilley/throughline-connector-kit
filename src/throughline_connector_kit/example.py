from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from .contract import AuthContext, NormalizedRecord, RawEntity
from .engine import InMemoryDestination, PermanentSyncError, SyncEngine


def parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise PermanentSyncError("missing updated_at timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SyntheticCrmConnector:
    """Runnable connector example using synthetic accounts and contacts."""

    name = "synthetic_crm"

    def __init__(self) -> None:
        self._records: dict[str, list[dict[str, object]]] = {
            "accounts": [
                {
                    "id": "acct_001",
                    "name": "Example Robotics",
                    "stage": "customer",
                    "updated_at": "2026-01-02T12:00:00Z",
                },
                {
                    "id": "acct_002",
                    "name": "Northstar Media",
                    "stage": "proposal",
                    "updated_at": "2026-01-03T09:30:00Z",
                },
            ],
            "contacts": [
                {
                    "id": "cont_001",
                    "account_id": "acct_001",
                    "email": "ops@example.invalid",
                    "role": "operations",
                    "updated_at": "2026-01-02T13:15:00Z",
                },
                {
                    "id": "cont_002",
                    "account_id": "acct_002",
                    "email": "finance@northstar.invalid",
                    "role": "finance",
                    "updated_at": "2026-01-03T10:00:00Z",
                },
            ],
        }

    def authenticate(self) -> AuthContext:
        return AuthContext(principal="synthetic-demo", scopes=("read:accounts", "read:contacts"))

    def get_sync_order(self) -> list[str]:
        return ["accounts", "contacts"]

    def fetch_entities(self, entity_type: str, since: datetime | None) -> Iterable[RawEntity]:
        if entity_type not in self._records:
            raise PermanentSyncError(f"unsupported entity type: {entity_type}")

        for raw in self._records[entity_type]:
            updated_at = parse_timestamp(raw.get("updated_at"))
            if since is None or updated_at > since:
                yield raw

    def transform_entity(self, entity_type: str, raw: RawEntity) -> NormalizedRecord:
        source_id = raw.get("id")
        if not isinstance(source_id, str) or not source_id:
            raise PermanentSyncError(f"{entity_type} record missing id")

        updated_at = parse_timestamp(raw.get("updated_at"))
        payload = dict(raw)
        payload["synced_at"] = datetime.now(timezone.utc).isoformat()

        return NormalizedRecord(
            source_system=self.name,
            entity_type=entity_type,
            source_id=source_id,
            updated_at=updated_at,
            payload=payload,
        )


def run_example() -> tuple[dict[str, object], InMemoryDestination]:
    destination = InMemoryDestination()
    engine = SyncEngine(SyntheticCrmConnector(), destination)
    return engine.sync(), destination


def main() -> None:
    results, destination = run_example()
    for entity_type, result in results.items():
        checkpoint = result.checkpoint.isoformat() if result.checkpoint else "none"
        print(
            f"{entity_type}: created={result.created} updated={result.updated} "
            f"failed={result.failed} checkpoint={checkpoint}"
        )
    print(f"destination records={len(destination.records)}")
