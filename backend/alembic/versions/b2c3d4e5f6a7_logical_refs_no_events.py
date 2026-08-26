"""Initial schema without entity-table foreign keys. Drops legacy events table if present."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = set(inspector.get_table_names())

    # Drop legacy FK-backed schema if upgrading from create_all era
    if "articles" in tables:
        fks = inspector.get_foreign_keys("articles")
        for fk in fks:
            if fk.get("name"):
                op.drop_constraint(fk["name"], "articles", type_="foreignkey")
        cols = {c["name"] for c in inspector.get_columns("articles")}
        if "event_id" in cols:
            op.drop_column("articles", "event_id")

    if "fetch_logs" in tables:
        fks = inspector.get_foreign_keys("fetch_logs")
        for fk in fks:
            if fk.get("name"):
                op.drop_constraint(fk["name"], "fetch_logs", type_="foreignkey")

    if "events" in tables:
        op.drop_table("events")

    if "categories" not in tables:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("slug", sa.String(100), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.UniqueConstraint("slug"),
        )

    if "sources" not in tables:
        sourcetype = sa.Enum("rss", "api", "scraper", name="sourcetype")
        op.create_table(
            "sources",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("type", sourcetype, nullable=False),
            sa.Column("endpoint", sa.String(500), nullable=False),
            sa.Column("config", sa.JSON(), nullable=False),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("last_fetched_at", sa.BigInteger(), nullable=True),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
            sa.UniqueConstraint("name"),
        )

    if "articles" not in tables:
        op.create_table(
            "articles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(500), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("url", sa.String(2000), nullable=False),
            sa.Column("url_hash", sa.String(64), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("author", sa.String(200), nullable=True),
            sa.Column("image_url", sa.String(2000), nullable=True),
            sa.Column("published_at", sa.BigInteger(), nullable=True),
            sa.Column("fetched_at", sa.BigInteger(), nullable=False),
            sa.Column("language", sa.String(10), nullable=True),
            sa.UniqueConstraint("url_hash"),
        )
        op.create_index("ix_articles_published_at", "articles", ["published_at"])
        op.create_index("ix_articles_category_id", "articles", ["category_id"])
        op.create_index("ix_articles_source_id", "articles", ["source_id"])
        op.create_index("ix_articles_fetched_at", "articles", ["fetched_at"])
    else:
        existing_indexes = {ix["name"] for ix in inspector.get_indexes("articles")}
        if "ix_articles_source_id" not in existing_indexes:
            op.create_index("ix_articles_source_id", "articles", ["source_id"])
        if "ix_articles_fetched_at" not in existing_indexes:
            op.create_index("ix_articles_fetched_at", "articles", ["fetched_at"])

    if "fetch_logs" not in tables:
        fetchstatus = sa.Enum("success", "failed", name="fetchstatus")
        op.create_table(
            "fetch_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("status", fetchstatus, nullable=False),
            sa.Column("articles_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.BigInteger(), nullable=False),
        )
        op.create_index("ix_fetch_logs_source_id", "fetch_logs", ["source_id"])


def downgrade() -> None:
    op.drop_table("fetch_logs")
    op.drop_table("articles")
    op.drop_table("sources")
    op.drop_table("categories")
    sa.Enum(name="fetchstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sourcetype").drop(op.get_bind(), checkfirst=True)
