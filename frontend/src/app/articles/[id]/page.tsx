import { notFound } from "next/navigation";

import { ArticleDetailView, fetchArticle } from "@/features/article-detail";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function ArticlePage({ params }: PageProps) {
  const { id } = await params;
  const articleId = Number(id);
  if (Number.isNaN(articleId)) notFound();

  let article;
  try {
    article = await fetchArticle(articleId);
  } catch {
    notFound();
  }

  return <ArticleDetailView article={article} />;
}
