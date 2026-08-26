import { request } from "@/shared/lib/http";
import type { ArticleDetail } from "@/shared/lib/catalog-types";

export type { ArticleDetail } from "@/shared/lib/catalog-types";

export function fetchArticle(id: number): Promise<ArticleDetail> {
  return request(`/articles/${id}`, { revalidate: 60 });
}
