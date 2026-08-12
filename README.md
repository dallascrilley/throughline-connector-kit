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
