export const timelineCopy = {
  title: "新闻时间线",
  subtitle: "按日期浏览新闻进展",
  loadError: "加载失败，请确认后端服务已启动",
  empty: "暂无数据",
  allCategories: "全部",
} as const;

export function parseTimelineSearchParams(params: {
  category?: string | string[] | undefined;
}): { category: string | null } {
  const categoryRaw = Array.isArray(params.category)
    ? params.category[0]
    : params.category;
  return { category: categoryRaw?.trim() || null };
}
