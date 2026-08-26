from __future__ import annotations

from sqlalchemy import func, or_, select

from app.domains.catalog.catalog_domain import (
    ArticleRead,
    CategoryBrief,
    CategoryWithCount,
    FetchLogRead,
    SourceBrief,
    SourceRead,
)
from app.infrastructure.persistence.models import (
    ArticleRow,
    CategoryRow,
    FetchLogRow,
    SourceRow,
)
from app.infrastructure.persistence.unit_of_work import get_current_session


def _map_article(
    article: ArticleRow,
    source: SourceRow | None,
    category: CategoryRow | None,
) -> ArticleRead:
    return ArticleRead(
        id=article.id,
        title=article.title,
        summary=article.summary,
        url=article.url,
        author=article.author,
        image_url=article.image_url,
        published_at=article.published_at,
        fetched_at=article.fetched_at,
        language=article.language,
        source=SourceBrief(id=source.id, name=source.name)
        if source
        else SourceBrief(id=article.source_id, name="unknown"),
        category=CategoryBrief(id=category.id, name=category.name, slug=category.slug)
        if category
        else None,
    )


class SqlAlchemyCatalogRepository:
    def list_articles(
        self,
        *,
        page: int,
        page_size: int,
        category_slug: str | None = None,
        source_id: int | None = None,
        q: str | None = None,
        from_ms: int | None = None,
        to_ms: int | None = None,
    ) -> tuple[list[ArticleRead], int]:
        session = get_current_session()
        filters = []
        if category_slug:
            cat_id = session.scalar(
                select(CategoryRow.id).where(CategoryRow.slug == category_slug)
            )
            if cat_id is None:
                return [], 0
            filters.append(ArticleRow.category_id == cat_id)
        if source_id is not None:
            filters.append(ArticleRow.source_id == source_id)
        if q:
            pattern = f"%{q}%"
            filters.append(
                or_(ArticleRow.title.ilike(pattern), ArticleRow.summary.ilike(pattern))
            )
        if from_ms is not None:
            filters.append(ArticleRow.published_at >= from_ms)
        if to_ms is not None:
            filters.append(ArticleRow.published_at <= to_ms)

        count_stmt = select(func.count(ArticleRow.id))
        for f in filters:
            count_stmt = count_stmt.where(f)
        total = session.scalar(count_stmt) or 0

        stmt = select(ArticleRow).order_by(
            ArticleRow.published_at.desc().nullslast(), ArticleRow.id.desc()
        )
        for f in filters:
            stmt = stmt.where(f)
        rows = session.scalars(
            stmt.offset((page - 1) * page_size).limit(page_size)
        ).all()
        return self._hydrate(rows), total

    def get_article(self, article_id: int) -> ArticleRead | None:
        session = get_current_session()
        row = session.get(ArticleRow, article_id)
        if row is None:
            return None
        items = self._hydrate([row])
        return items[0] if items else None

    def list_categories_with_counts(self) -> list[CategoryWithCount]:
        session = get_current_session()
        rows = session.execute(
            select(
                CategoryRow.id,
                CategoryRow.name,
                CategoryRow.slug,
                CategoryRow.sort_order,
                func.count(ArticleRow.id).label("article_count"),
            )
            .outerjoin(ArticleRow, ArticleRow.category_id == CategoryRow.id)
            .group_by(CategoryRow.id)
            .order_by(CategoryRow.sort_order, CategoryRow.id)
        ).all()
        return [
            CategoryWithCount(
                id=row.id,
                name=row.name,
                slug=row.slug,
                sort_order=row.sort_order,
                article_count=row.article_count,
            )
            for row in rows
        ]

    def list_timeline(
        self,
        *,
        category_slug: str | None = None,
        limit: int = 100,
    ) -> list[ArticleRead]:
        session = get_current_session()
        stmt = select(ArticleRow).order_by(
            ArticleRow.published_at.desc().nullslast(), ArticleRow.id.desc()
        ).limit(limit)
        if category_slug:
            cat_id = session.scalar(
                select(CategoryRow.id).where(CategoryRow.slug == category_slug)
            )
            if cat_id is None:
                return []
            stmt = stmt.where(ArticleRow.category_id == cat_id)
        rows = session.scalars(stmt).all()
        return self._hydrate(rows)

    def list_sources(self) -> list[SourceRead]:
        session = get_current_session()
        rows = session.scalars(select(SourceRow).order_by(SourceRow.id)).all()
        return [
            SourceRead(
                id=r.id,
                name=r.name,
                type=r.type.value,
                endpoint=r.endpoint,
                enabled=r.enabled,
                last_fetched_at=r.last_fetched_at,
            )
            for r in rows
        ]

    def list_fetch_logs(self, *, limit: int = 50) -> list[FetchLogRead]:
        session = get_current_session()
        rows = session.scalars(
            select(FetchLogRow).order_by(FetchLogRow.created_at.desc()).limit(limit)
        ).all()
        return [
            FetchLogRead(
                id=r.id,
                source_id=r.source_id,
                status=r.status.value,
                articles_count=r.articles_count,
                error_message=r.error_message,
                created_at=r.created_at,
            )
            for r in rows
        ]

    def _hydrate(self, rows: list[ArticleRow]) -> list[ArticleRead]:
        if not rows:
            return []
        session = get_current_session()
        source_ids = {r.source_id for r in rows}
        category_ids = {r.category_id for r in rows if r.category_id is not None}
        sources = {
            s.id: s
            for s in session.scalars(
                select(SourceRow).where(SourceRow.id.in_(source_ids))
            ).all()
        }
        categories = {
            c.id: c
            for c in session.scalars(
                select(CategoryRow).where(CategoryRow.id.in_(category_ids))
            ).all()
        } if category_ids else {}
        return [
            _map_article(r, sources.get(r.source_id), categories.get(r.category_id) if r.category_id else None)
            for r in rows
        ]
