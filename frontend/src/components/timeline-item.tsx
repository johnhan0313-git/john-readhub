import Link from "next/link";

import type { ArticleBrief } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

interface TimelineItemProps {
  article: ArticleBrief;
}

export function TimelineItem({ article }: TimelineItemProps) {
  return (
    <div className="relative pl-8">
      <div className="absolute left-0 top-2 h-3 w-3 rounded-full border-2 border-brand-500 bg-white" />
      <div className="glass-card">
        <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <time>{formatDateTime(article.published_at)}</time>
          <span>·</span>
          <span>{article.source.name}</span>
          {article.category && (
            <>
              <span>·</span>
              <span className="text-brand-600">{article.category.name}</span>
            </>
          )}
        </div>
        <Link
          href={`/articles/${article.id}`}
          className="text-base font-semibold text-slate-900 hover:text-brand-700"
        >
          {article.title}
        </Link>
        {article.summary && (
          <p className="mt-1 line-clamp-2 text-sm text-slate-600">{article.summary}</p>
        )}
      </div>
    </div>
  );
}
