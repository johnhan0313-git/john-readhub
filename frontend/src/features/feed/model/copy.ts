export const feedCopy = {
  title: "最新资讯",
  subtitle: "泛资讯阅读 — 含 IT 技术、招聘等 16 类优质来源聚合",
  searchPlaceholder: "搜索标题或摘要...",
  loadError: "加载失败，请确认后端服务已启动",
  empty: "暂无文章。请等待采集任务运行，或由管理员触发采集。",
  prevPage: "上一页",
  nextPage: "下一页",
  allCategories: "全部",
  viewDetail: "查看详情",
  readOriginal: "阅读原文",
} as const;

export function parseFeedSearchParams(params: {
  category?: string | string[] | undefined;
  q?: string | string[] | undefined;
  page?: string | string[] | undefined;
}): { category: string | null; q: string; page: number } {
  const categoryRaw = Array.isArray(params.category)
    ? params.category[0]
    : params.category;
  const qRaw = Array.isArray(params.q) ? params.q[0] : params.q;
  const pageRaw = Array.isArray(params.page) ? params.page[0] : params.page;
  const page = Math.max(1, Number(pageRaw) || 1);
  return {
    category: categoryRaw?.trim() || null,
    q: qRaw?.trim() || "",
    page,
  };
}

export function buildFeedSearchParams(state: {
  category: string | null;
  q: string;
  page: number;
}): URLSearchParams {
  const next = new URLSearchParams();
  if (state.category) next.set("category", state.category);
  if (state.q) next.set("q", state.q);
  if (state.page > 1) next.set("page", String(state.page));
  return next;
}
