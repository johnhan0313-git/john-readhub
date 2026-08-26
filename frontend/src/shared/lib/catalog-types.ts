export interface CategoryBrief {
  id: number;
  name: string;
  slug: string;
}

export interface SourceBrief {
  id: number;
  name: string;
}

export interface ArticleBrief {
  id: number;
  title: string;
  summary: string | null;
  url: string;
  author: string | null;
  image_url: string | null;
  published_at: number | null;
  fetched_at: number;
  source: SourceBrief;
  category: CategoryBrief | null;
}

export interface ArticleDetail extends ArticleBrief {
  language: string | null;
}

export interface ArticleListResponse {
  items: ArticleBrief[];
  total: number;
  page: number;
  page_size: number;
}

export interface CategoryWithCount extends CategoryBrief {
  sort_order: number;
  article_count: number;
}

export interface TimelineGroup {
  date: string;
  articles: ArticleBrief[];
}

export interface TimelineResponse {
  groups: TimelineGroup[];
  total: number;
}
