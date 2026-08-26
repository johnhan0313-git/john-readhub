from __future__ import annotations

from app.application.ingest.ingest_command import IngestCommands
from app.composition.container import get_container


def get_ingest_commands() -> IngestCommands:
    return get_container().ingest
