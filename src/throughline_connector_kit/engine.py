from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

from .contract import Connector, NormalizedRecord, SyncResult


class PermanentSyncError(Exception):
    """Raised when a record cannot be retried safely without source changes."""


@dataclass
class InMemoryDestination:
    """Small destination adapter used by tests and the synthetic example."""

    records: dict[tuple[str, str, str], NormalizedRecord] = field(default_factory=dict)

    def upsert(self, record: NormalizedRecord) -> str:
        operation = "updated" if record.key in self.records else "created"
        self.records[record.key] = record
        return operation


@dataclass
class SyncEngine:
    """Generic sync loop that keeps connector-specific logic out of the engine."""

    connector: Connector
    destination: InMemoryDestination
    checkpoints: dict[tuple[str, str], datetime] = field(default_factory=dict)

    def sync(self, entity_types: Iterable[str] | None = None, incremental: bool = True) -> dict[str, SyncResult]:
        self.connector.authenticate()
        ordered_entities = list(entity_types or self.connector.get_sync_order())
        results: dict[str, SyncResult] = {}

        for entity_type in ordered_entities:
            since = self.checkpoints.get((self.connector.name, entity_type)) if incremental else None
            result = SyncResult(entity_type=entity_type)

            for raw in self.connector.fetch_entities(entity_type, since):
                try:
                    record = self.connector.transform_entity(entity_type, raw)
                    operation = self.destination.upsert(record)
                    if operation == "created":
                        result.created += 1
                    else:
                        result.updated += 1

                    if result.checkpoint is None or record.updated_at > result.checkpoint:
                        result.checkpoint = record.updated_at
                except PermanentSyncError as exc:
                    result.failed += 1
                    result.errors.append(str(exc))

            if result.checkpoint is not None:
                self.checkpoints[(self.connector.name, entity_type)] = result.checkpoint

            results[entity_type] = result

        return results
