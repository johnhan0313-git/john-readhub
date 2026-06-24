from __future__ import annotations

from pydantic import BaseModel


class CategoryBrief(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class SourceBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ArticleBrief(BaseModel):
    id: int
    title: str
    summary: str | None
    url: str
    author: str | None
    image_url: str | None
    published_at: int | None
    fetched_at: int
    source: SourceBrief
    category: CategoryBrief | None

    model_config = {"from_attributes": True}


class ArticleDetail(ArticleBrief):
    language: str | None


class ArticleListResponse(BaseModel):
    items: list[ArticleBrief]
    total: int
    page: int
    page_size: int


class CategoryWithCount(BaseModel):
    id: int
    name: str
    slug: str
    sort_order: int
    article_count: int


class TimelineGroup(BaseModel):
    date: str
    articles: list[ArticleBrief]


class TimelineResponse(BaseModel):
    groups: list[TimelineGroup]
    total: int
