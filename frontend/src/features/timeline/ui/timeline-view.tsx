"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";

import {
  fetchCategories,
  fetchTimeline,
} from "@/features/timeline/gateway/catalog";
import {
  parseTimelineSearchParams,
  timelineCopy,
} from "@/features/timeline/model/copy";
import { TimelineItem } from "@/features/timeline/ui/timeline-item";
import { formatDate } from "@/shared/lib/utils";
import { CategoryTabs } from "@/shared/ui/category-tabs";

export function TimelineView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nav = useMemo(
    () =>
      parseTimelineSearchParams({
        category: searchParams.get("category") ?? undefined,
      }),
    [searchParams],
  );

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: ["timeline", nav.category],
    queryFn: () => fetchTimeline(nav.category ?? undefined),
  });

  const handleCategoryChange = (slug: string | null) => {
    const qs = slug ? `?category=${encodeURIComponent(slug)}` : "";
    router.replace(`/timeline${qs}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{timelineCopy.title}</h1>
        <p className="mt-1 text-sm text-slate-500">{timelineCopy.subtitle}</p>
      </div>

      <CategoryTabs
        categories={categories}
        active={nav.category}
        onChange={handleCategoryChange}
        allLabel={timelineCopy.allCategories}
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
          {timelineCopy.loadError}
        </div>
      )}

      {data && data.groups.length === 0 && (
        <div className="glass-card text-center text-sm text-slate-500">
          {timelineCopy.empty}
        </div>
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
