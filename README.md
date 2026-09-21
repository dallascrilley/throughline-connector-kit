# Throughline Connector Kit

[![CI](https://github.com/dallascrilley/throughline-connector-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/dallascrilley/throughline-connector-kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Sanitized extraction of the connector contract behind Throughline: one connector
interface, a small sync engine, and a runnable synthetic CRM example.

This is intentionally not the production repository. It contains no client data,
credentials, vendor schemas, or private business logic. The point is to make the
architecture behind the Throughline case study inspectable:

- connectors implement exactly four required methods
- the engine owns sync order, incremental checkpoints, retry classification, and
  destination writes
- examples use synthetic data only

## Quick Start

```bash
uv sync
uv run throughline-example
uv run pytest
```

Expected example output:

```text
accounts: created=2 updated=0 failed=0 checkpoint=2026-01-03T09:30:00+00:00
contacts: created=2 updated=0 failed=0 checkpoint=2026-01-03T10:00:00+00:00
destination records=4
```

## The Four-Method Contract

```python
class Connector(Protocol):
    name: str

    def authenticate(self) -> AuthContext: ...
    def get_sync_order(self) -> Sequence[str]: ...
    def fetch_entities(self, entity_type: str, since: datetime | None) -> Iterable[RawEntity]: ...
    def transform_entity(self, entity_type: str, raw: RawEntity) -> NormalizedRecord: ...
```

The connector knows the source schema and authentication. The engine knows
sync semantics. That keeps destination-specific write logic out of connector
implementations.

## Credentials And Checkpoints

Credentials live on the connector instance. Checkpoints live on the engine,
keyed by connector name and entity type. That is the isolation this kit
actually has.

`authenticate()` is the only contract method that talks to auth. It returns
`AuthContext` with a principal and scopes. The public type does not carry
tokens or API keys. Production connectors may hold OAuth clients internally;
this extract records only the principal. `SyncEngine.sync()` calls
`authenticate()` and does not keep the return value. Secrets never enter the
engine, the checkpoint map, or the destination key.

A second org is a second connector instance, constructed with its own
credentials and a distinct `name`. The engine does not take a tenant id.
Mixing two orgs on one instance would be a construction mistake, not a merge
the engine can perform.

Checkpoints are engine-owned. `SyncEngine.checkpoints` is a
`dict[tuple[str, str], datetime]` keyed `(connector.name, entity_type)`.
Incremental `fetch_entities` receives that timestamp as `since`. Destination
records use `NormalizedRecord.key`: `(source_system, entity_type, source_id)`.
Two connectors with different names cannot advance each other's checkpoints
or overwrite each other's rows.

This is not a multi-tenant SaaS control plane. The example `SyncEngine` holds
one connector and an in-memory destination. Production Throughline ran this
shape for six vendor integrations at one company. The kit shows the boundary.
It does not show a tenant registry, a credentials vault, or horizontal scale.

## Why This Is Sanitized

The production Throughline system connected QuickBooks, Copper, Basecamp,
PandaDoc, Airtable, PostgreSQL, and operational dashboards. This repo keeps only
the reusable shape:

- no real API clients
- no real tables or customer records
- no copied credentials or environment names
- no production migrations

The synthetic connector demonstrates the same architecture with accounts and
contacts generated in memory.

## Relationship To The Case Study

The architecture write-up is here:

https://dallascrilley.com/writing/throughline-connectors

The public case study is here:

https://dallascrilley.com/work/throughline

This repo is the inspectable code companion for the four-method connector
contract described in those pages.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security reports go through [SECURITY.md](SECURITY.md).

## License

MIT.
