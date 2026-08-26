import { Suspense } from "react";

import { TimelineView } from "@/features/timeline";

export default function TimelinePage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-slate-100" />
          ))}
        </div>
      }
    >
      <TimelineView />
    </Suspense>
  );
}
