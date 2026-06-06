"use client";

import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useCallback, useState } from "react";

import { fetchArticles, fetchCategories } from "@/lib/api";
import { ArticleCard } from "@/components/article-card";
import { CategoryTabs } from "@/components/category-tabs";

export function HomeFeed() {
  const [category, setCategory] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["articles", category, search, page],
    queryFn: () =>
      fetchArticles({
        page,
        page_size: 20,
        category: category ?? undefined,
        q: search || undefined,
      }),
  });

  const handleSearch = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      setSearch(query.trim());
      setPage(1);
    },
    [query],
  );

  const handleCategoryChange = (slug: string | null) => {
    setCategory(slug);
    setPage(1);
  };

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">最新资讯</h1>
        <p className="mt-1 text-sm text-slate-500">
          聚合 RSS 与新闻 API，按分类浏览全网热点
        </p>
      </div>

      <form onSubmit={handleSearch} className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索标题或摘要..."
          className="input-field pl-10"
        />
      </form>

      <CategoryTabs
        categories={categories}
        active={category}
        onChange={handleCategoryChange}
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
          加载失败，请确认后端服务已启动（http://localhost:8000）
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="glass-card text-center text-sm text-slate-500">
          暂无文章。请等待采集任务运行，或调用 POST /api/admin/fetch 手动触发。
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
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="chip-inactive disabled:opacity-40"
          >
            上一页
          </button>
          <span className="text-sm text-slate-500">
            {page} / {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="chip-inactive disabled:opacity-40"
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
}
