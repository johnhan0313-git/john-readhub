import { request } from "@/shared/lib/http";
import type {
  CategoryWithCount,
  TimelineResponse,
} from "@/shared/lib/catalog-types";

export type { ArticleBrief, CategoryWithCount } from "@/shared/lib/catalog-types";

export function fetchCategories(): Promise<CategoryWithCount[]> {
  return request("/categories");
}

export function fetchTimeline(category?: string): Promise<TimelineResponse> {
  const qs = category ? `?category=${encodeURIComponent(category)}` : "";
  return request(`/timeline${qs}`);
}
