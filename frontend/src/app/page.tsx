import { Suspense } from "react";

import { HomeFeed } from "@/features/feed";

export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="glass-card h-28 animate-pulse bg-slate-100" />
          ))}
        </div>
      }
    >
      <HomeFeed />
    </Suspense>
  );
}
