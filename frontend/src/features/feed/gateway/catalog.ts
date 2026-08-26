import { request } from "@/shared/lib/http";
import type {
  ArticleListResponse,
  CategoryWithCount,
} from "@/shared/lib/catalog-types";

export type { ArticleBrief, CategoryWithCount } from "@/shared/lib/catalog-types";

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

export function fetchCategories(): Promise<CategoryWithCount[]> {
  return request("/categories");
}
