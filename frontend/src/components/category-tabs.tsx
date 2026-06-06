"use client";

import type { CategoryWithCount } from "@/lib/api";
import { cn } from "@/lib/utils";

interface CategoryTabsProps {
  categories: CategoryWithCount[];
  active: string | null;
  onChange: (slug: string | null) => void;
}

export function CategoryTabs({ categories, active, onChange }: CategoryTabsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={() => onChange(null)}
        className={cn(active === null ? "chip-active" : "chip-inactive")}
      >
        全部
      </button>
      {categories.map((cat) => (
        <button
          key={cat.slug}
          type="button"
          onClick={() => onChange(cat.slug)}
          className={cn(active === cat.slug ? "chip-active" : "chip-inactive")}
        >
          {cat.name}
          {cat.article_count > 0 && (
            <span className="ml-1 opacity-70">({cat.article_count})</span>
          )}
        </button>
      ))}
    </div>
  );
}
