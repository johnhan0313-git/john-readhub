"use client";

import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo, useState } from "react";

import { fetchArticles, fetchCategories } from "@/features/feed/gateway/catalog";
import {
  buildFeedSearchParams,
  feedCopy,
  parseFeedSearchParams,
} from "@/features/feed/model/copy";
import { ArticleCard } from "@/features/feed/ui/article-card";
import { CategoryTabs } from "@/shared/ui/category-tabs";

export function HomeFeed() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nav = useMemo(
    () =>
      parseFeedSearchParams({
        category: searchParams.get("category") ?? undefined,
        q: searchParams.get("q") ?? undefined,
        page: searchParams.get("page") ?? undefined,
      }),
    [searchParams],
  );

  const [draftQuery, setDraftQuery] = useState(nav.q);

  const syncUrl = useCallback(
    (next: { category: string | null; q: string; page: number }) => {
      const qs = buildFeedSearchParams(next).toString();
      router.replace(qs ? `/?${qs}` : "/");
    },
    [router],
  );

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["articles", nav.category, nav.q, nav.page],
    queryFn: () =>
      fetchArticles({
        page: nav.page,
        page_size: 20,
        category: nav.category ?? undefined,
        q: nav.q || undefined,
      }),
  });

  const handleSearch = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      syncUrl({ category: nav.category, q: draftQuery.trim(), page: 1 });
    },
    [draftQuery, nav.category, syncUrl],
  );

  const handleCategoryChange = (slug: string | null) => {
    syncUrl({ category: slug, q: nav.q, page: 1 });
  };

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{feedCopy.title}</h1>
        <p className="mt-1 text-sm text-slate-500">{feedCopy.subtitle}</p>
      </div>

      <form onSubmit={handleSearch} className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="search"
          value={draftQuery}
          onChange={(e) => setDraftQuery(e.target.value)}
          placeholder={feedCopy.searchPlaceholder}
          className="input-field pl-10"
        />
      </form>

      <CategoryTabs
        categories={categories}
        active={nav.category}
        onChange={handleCategoryChange}
        allLabel={feedCopy.allCategories}
      />

      {isLoading && (
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="glass-card h-28 animate-pulse bg-slate-100" />
          ))}
        </div>
      )}

      {isError && (
        <div className="glass-card text-center text-sm text-red-600">
          {feedCopy.loadError}
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="glass-card text-center text-sm text-slate-500">
          {feedCopy.empty}
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="space-y-4">
          {data.items.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <button
            type="button"
            disabled={nav.page <= 1}
            onClick={() =>
              syncUrl({ category: nav.category, q: nav.q, page: nav.page - 1 })
            }
            className="chip-inactive disabled:opacity-40"
          >
            {feedCopy.prevPage}
          </button>
          <span className="text-sm text-slate-500">
            {nav.page} / {totalPages}
          </span>
          <button
            type="button"
            disabled={nav.page >= totalPages}
            onClick={() =>
              syncUrl({ category: nav.category, q: nav.q, page: nav.page + 1 })
            }
            className="chip-inactive disabled:opacity-40"
          >
            {feedCopy.nextPage}
          </button>
        </div>
      )}
    </div>
  );
}
