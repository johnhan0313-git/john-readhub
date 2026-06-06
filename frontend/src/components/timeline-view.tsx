"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { fetchCategories, fetchTimeline } from "@/lib/api";
import { CategoryTabs } from "@/components/category-tabs";
import { TimelineItem } from "@/components/timeline-item";
import { formatDate } from "@/lib/utils";

export function TimelineView() {
  const [category, setCategory] = useState<string | null>(null);

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["timeline", category],
    queryFn: () => fetchTimeline(category ?? undefined),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">新闻时间线</h1>
        <p className="mt-1 text-sm text-slate-500">按日期浏览新闻进展</p>
      </div>

      <CategoryTabs
        categories={categories}
        active={category}
        onChange={setCategory}
      />

      {isLoading && (
        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-slate-100" />
          ))}
        </div>
      )}

      {isError && (
        <div className="glass-card text-center text-sm text-red-600">
          加载失败，请确认后端服务已启动
        </div>
      )}

      {data && data.groups.length === 0 && (
        <div className="glass-card text-center text-sm text-slate-500">暂无数据</div>
      )}

      {data?.groups.map((group) => (
        <section key={group.date}>
          <h2 className="mb-4 text-lg font-semibold text-slate-800">
            {formatDate(group.date)}
          </h2>
          <div className="relative space-y-4 border-l-2 border-brand-200 pl-0">
            {group.articles.map((article) => (
              <TimelineItem key={article.id} article={article} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
