from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable, Mapping, Protocol, Sequence


RawEntity = Mapping[str, Any]


@dataclass(frozen=True)
class AuthContext:
    """Sanitized auth result returned by a connector.

    Production connectors may hold OAuth tokens or API clients internally. This
    public example records only the authenticated principal and granted scopes.
    """

    principal: str
    scopes: tuple[str, ...] = ()


@dataclass(frozen=True)
class NormalizedRecord:
    """Destination-neutral record emitted by connector transforms."""

    source_system: str
    entity_type: str
    source_id: str
    updated_at: datetime
    payload: Mapping[str, Any]

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source_system, self.entity_type, self.source_id)


@dataclass
class SyncResult:
    entity_type: str
    created: int = 0
    updated: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    checkpoint: datetime | None = None


class Connector(Protocol):
    """Four-method contract for a source connector."""

    name: str

    def authenticate(self) -> AuthContext:
        """Validate credentials and prepare the connector for fetches."""

    def get_sync_order(self) -> Sequence[str]:
        """Return entity types in dependency order."""

    def fetch_entities(self, entity_type: str, since: datetime | None) -> Iterable[RawEntity]:
        """Fetch raw source records, optionally changed since a checkpoint."""

    def transform_entity(self, entity_type: str, raw: RawEntity) -> NormalizedRecord:
        """Convert a raw source record into the shared destination shape."""
