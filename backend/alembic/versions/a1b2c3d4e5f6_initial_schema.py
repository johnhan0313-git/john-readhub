"""Legacy baseline revision (schema already applied via create_all historically)."""

from __future__ import annotations

revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: deployed databases already have the baseline tables.
    # Fresh installs continue to b2c3d4e5f6a7 which creates tables if missing.
    pass


def downgrade() -> None:
    pass
