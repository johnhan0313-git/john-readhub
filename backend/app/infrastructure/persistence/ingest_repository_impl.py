from __future__ import annotations

from sqlalchemy import delete, select

from app.domains.ingest.ingest_domain import (
    ArticleDraft,
    FetchOutcome,
    SourceRecord,
    SourceType,
)
from app.infrastructure.persistence.models import (
    ArticleRow,
    CategoryRow,
    FetchLogRow,
    FetchStatus as FetchStatusRow,
    SourceRow,
    SourceType as SourceTypeRow,
)
from app.infrastructure.persistence.unit_of_work import get_current_session


def _to_source_record(row: SourceRow) -> SourceRecord:
    return SourceRecord(
        id=row.id,
        name=row.name,
        type=SourceType(row.type.value),
        endpoint=row.endpoint,
        config=row.config or {},
        enabled=row.enabled,
        last_fetched_at=row.last_fetched_at,
    )


class SqlAlchemySourceRepository:
    def list_enabled(self, source_type: SourceType | None = None) -> list[SourceRecord]:
        session = get_current_session()
        stmt = select(SourceRow).where(SourceRow.enabled.is_(True)).order_by(SourceRow.id)
        if source_type is not None:
            stmt = stmt.where(SourceRow.type == SourceTypeRow(source_type.value))
        rows = session.scalars(stmt).all()
        return [_to_source_record(r) for r in rows]

    def get(self, source_id: int) -> SourceRecord | None:
        row = get_current_session().get(SourceRow, source_id)
        return _to_source_record(row) if row else None

    def upsert_category(
        self, *, name: str, slug: str, sort_order: int
    ) -> tuple[int, bool, bool]:
        session = get_current_session()
        existing = session.scalar(select(CategoryRow).where(CategoryRow.slug == slug))
        if existing:
            changed = False
            if existing.name != name:
                existing.name = name
                changed = True
            if existing.sort_order != sort_order:
                existing.sort_order = sort_order
                changed = True
            return existing.id, False, changed
        row = CategoryRow(name=name, slug=slug, sort_order=sort_order)
        session.add(row)
        session.flush()
        return row.id, True, True

    def upsert_source(
        self,
        *,
        name: str,
        source_type: SourceType,
        endpoint: str,
        config: dict,
        enabled: bool,
    ) -> tuple[int, bool, bool]:
        session = get_current_session()
        existing = session.scalar(select(SourceRow).where(SourceRow.name == name))
        new_type = SourceTypeRow(source_type.value)
        if existing:
            changed = False
            if existing.type != new_type:
                existing.type = new_type
                changed = True
            if existing.endpoint != endpoint:
                existing.endpoint = endpoint
                changed = True
            if existing.config != config:
                existing.config = config
                changed = True
            if existing.enabled != enabled:
                existing.enabled = enabled
                changed = True
            return existing.id, False, changed
        row = SourceRow(
            name=name,
            type=new_type,
            endpoint=endpoint,
            config=config,
            enabled=enabled,
        )
        session.add(row)
        session.flush()
        return row.id, True, True

    def retire_named(self, names: frozenset[str]) -> int:
        session = get_current_session()
        retired = 0
        for name in names:
            source = session.scalar(select(SourceRow).where(SourceRow.name == name))
            if source and source.enabled:
                source.enabled = False
                retired += 1
        return retired

    def mark_fetched(self, source_id: int, fetched_at: int) -> None:
        row = get_current_session().get(SourceRow, source_id)
        if row:
            row.last_fetched_at = fetched_at

    def add_fetch_log(self, outcome: FetchOutcome, created_at: int) -> int:
        session = get_current_session()
        row = FetchLogRow(
            source_id=outcome.source_id,
            status=FetchStatusRow(outcome.status.value),
            articles_count=outcome.articles_count,
            error_message=outcome.error_message,
            created_at=created_at,
        )
        session.add(row)
        session.flush()
        return row.id


class SqlAlchemyArticleRepository:
    def url_hash_exists(self, url_hash: str) -> bool:
        session = get_current_session()
        return (
            session.scalar(select(ArticleRow.id).where(ArticleRow.url_hash == url_hash))
            is not None
        )

    def existing_url_hashes(self, hashes: set[str]) -> set[str]:
        if not hashes:
            return set()
        session = get_current_session()
        rows = session.scalars(
            select(ArticleRow.url_hash).where(ArticleRow.url_hash.in_(hashes))
        ).all()
        return set(rows)

    def recent_titles(self, since_ms: int, limit: int = 500) -> list[str]:
        session = get_current_session()
        return list(
            session.scalars(
                select(ArticleRow.title)
                .where(ArticleRow.published_at >= since_ms)
                .limit(limit)
            ).all()
        )

    def add_articles(self, drafts: list[ArticleDraft]) -> int:
        session = get_current_session()
        for draft in drafts:
            session.add(
                ArticleRow(
                    title=draft.title,
                    summary=draft.summary,
                    url=draft.url,
                    url_hash=draft.url_hash,
                    source_id=draft.source_id,
                    category_id=draft.category_id,
                    author=draft.author,
                    image_url=draft.image_url,
                    published_at=draft.published_at,
                    fetched_at=draft.fetched_at,
                    language=draft.language,
                )
            )
        return len(drafts)

    def delete_older_than(self, cutoff_ms: int) -> int:
        session = get_current_session()
        result = session.execute(delete(ArticleRow).where(ArticleRow.fetched_at < cutoff_ms))
        return result.rowcount or 0

    def category_id_by_slug(self, slug: str) -> int | None:
        session = get_current_session()
        return session.scalar(select(CategoryRow.id).where(CategoryRow.slug == slug))
