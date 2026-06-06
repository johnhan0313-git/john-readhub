"use client";

import type { CategoryWithCount } from "@/lib/api";
import { cn } from "@/lib/utils";

interface CategoryTabsProps {
  categories: CategoryWithCount[];
  active: string | null;
  onChange: (slug: string | null) => void;
}

export function CategoryTabs({ categories, active, onChange }: CategoryTabsProps) {
  const sorted = [...categories].sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="-mx-1 overflow-x-auto px-1 pb-1">
      <div className="flex min-w-max flex-wrap gap-2 sm:flex-nowrap">
        <button
          type="button"
          onClick={() => onChange(null)}
          className={cn(active === null ? "chip-active" : "chip-inactive")}
        >
          全部
        </button>
        {sorted.map((cat) => (
          <button
            key={cat.slug}
            type="button"
            onClick={() => onChange(cat.slug)}
            className={cn(
              "shrink-0",
              active === cat.slug ? "chip-active" : "chip-inactive",
            )}
          >
            {cat.name}
            {cat.article_count > 0 && (
              <span className="ml-1 opacity-70">({cat.article_count})</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
