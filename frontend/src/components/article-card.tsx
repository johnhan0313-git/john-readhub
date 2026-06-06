import Link from "next/link";
import { ExternalLink } from "lucide-react";

import type { ArticleBrief } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

interface ArticleCardProps {
  article: ArticleBrief;
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <article className="glass-card-hover group">
      <div className="flex gap-4">
        {article.image_url && (
          <div className="hidden h-24 w-32 shrink-0 overflow-hidden rounded-lg sm:block">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={article.image_url}
              alt=""
              className="h-full w-full object-cover"
            />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            {article.category && (
              <span className="rounded-full bg-brand-50 px-2 py-0.5 font-medium text-brand-700">
                {article.category.name}
              </span>
            )}
            <span>{article.source.name}</span>
            <span>·</span>
            <time>{formatDateTime(article.published_at)}</time>
          </div>
          <Link href={`/articles/${article.id}`} className="block">
            <h2 className="text-base font-semibold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 sm:text-lg">
              {article.title}
            </h2>
          </Link>
          {article.summary && (
            <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-600">
              {article.summary}
            </p>
          )}
          <div className="mt-3 flex items-center gap-3">
            <Link
              href={`/articles/${article.id}`}
              className="text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              查看详情
            </Link>
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
            >
              阅读原文
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>
      </div>
    </article>
  );
}
