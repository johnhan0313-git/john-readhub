from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.application.catalog.catalog_input import GetArticleInput, ListArticlesInput
from app.application.catalog.catalog_query import CatalogQueries
from app.composition.catalog_composition import get_catalog_queries

router = APIRouter(prefix="/articles", tags=["articles"])


class CategoryBriefResponse(BaseModel):
    id: int
    name: str
    slug: str


class SourceBriefResponse(BaseModel):
    id: int
    name: str


class ArticleBriefResponse(BaseModel):
    id: int
    title: str
    summary: str | None
    url: str
    author: str | None
    image_url: str | None
    published_at: int | None
    fetched_at: int
    source: SourceBriefResponse
    category: CategoryBriefResponse | None


class ArticleDetailResponse(ArticleBriefResponse):
    language: str | None


class ArticleListResponse(BaseModel):
    items: list[ArticleBriefResponse]
    total: int
    page: int
    page_size: int


def _map_article(a) -> ArticleBriefResponse:
    return ArticleBriefResponse(
        id=a.id,
        title=a.title,
        summary=a.summary,
        url=a.url,
        author=a.author,
        image_url=a.image_url,
        published_at=a.published_at,
        fetched_at=a.fetched_at,
        source=SourceBriefResponse(id=a.source.id, name=a.source.name),
        category=CategoryBriefResponse(id=a.category.id, name=a.category.name, slug=a.category.slug)
        if a.category
        else None,
    )


@router.get("", response_model=ArticleListResponse)
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    source_id: int | None = None,
    q: str | None = None,
    from_date: int | None = Query(None, alias="from", description="Unix timestamp in milliseconds"),
    to_date: int | None = Query(None, alias="to", description="Unix timestamp in milliseconds"),
    queries: CatalogQueries = Depends(get_catalog_queries),
):
    result = queries.list_articles(
        ListArticlesInput(
            page=page,
            page_size=page_size,
            category=category,
            source_id=source_id,
            q=q,
            from_ms=from_date,
            to_ms=to_date,
        )
    )
    return ArticleListResponse(
        items=[_map_article(a) for a in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article(
    article_id: int,
    queries: CatalogQueries = Depends(get_catalog_queries),
):
    article = queries.get_article(GetArticleInput(article_id=article_id))
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    brief = _map_article(article)
    return ArticleDetailResponse(**brief.model_dump(), language=article.language)
