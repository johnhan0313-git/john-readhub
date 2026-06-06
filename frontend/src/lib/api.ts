import { API_BASE } from "@/lib/env";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    next: { revalidate: 60 },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(text || res.statusText, res.status);
  }
  return res.json();
}

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
  published_at: string | null;
  fetched_at: string;
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

export function fetchArticles(params: {
  page?: number;
  page_size?: number;
  category?: string;
  q?: string;
}): Promise<ArticleListResponse> {
  const search = new URLSearchParams();
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  if (params.category) search.set("category", params.category);
  if (params.q) search.set("q", params.q);
  const qs = search.toString();
  return request(`/articles${qs ? `?${qs}` : ""}`);
}

export function fetchArticle(id: number): Promise<ArticleDetail> {
  return request(`/articles/${id}`);
}

export function fetchCategories(): Promise<CategoryWithCount[]> {
  return request("/categories");
}

export function fetchTimeline(category?: string): Promise<TimelineResponse> {
  const qs = category ? `?category=${category}` : "";
  return request(`/timeline${qs}`);
}
