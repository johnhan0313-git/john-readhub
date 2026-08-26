import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";

import type { ArticleDetail } from "@/features/article-detail/gateway/catalog";
import { articleDetailCopy } from "@/features/article-detail/model/copy";
import { formatDateTime } from "@/shared/lib/utils";

interface ArticleDetailViewProps {
  article: ArticleDetail;
}

export function ArticleDetailView({ article }: ArticleDetailViewProps) {
  return (
    <article className="mx-auto max-w-3xl space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600"
      >
        <ArrowLeft className="h-4 w-4" />
        {articleDetailCopy.backToList}
      </Link>

      <div className="glass-card space-y-4">
        <div className="flex flex-wrap items-center gap-2 text-sm text-slate-500">
          {article.category && (
            <span className="rounded-full bg-brand-50 px-2.5 py-0.5 font-medium text-brand-700">
              {article.category.name}
            </span>
          )}
          <span>{article.source.name}</span>
          {article.author && (
            <>
              <span>·</span>
              <span>{article.author}</span>
            </>
          )}
          <span>·</span>
          <time>{formatDateTime(article.published_at)}</time>
        </div>

        <h1 className="text-2xl font-bold leading-tight text-slate-900 sm:text-3xl">
          {article.title}
        </h1>

        {article.image_url && (
          <div className="overflow-hidden rounded-xl">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={article.image_url}
              alt=""
              className="w-full object-cover"
            />
          </div>
        )}

        {article.summary && (
          <p className="text-base leading-relaxed text-slate-700">{article.summary}</p>
        )}

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700"
        >
          {articleDetailCopy.readOriginal}
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </article>
  );
}
