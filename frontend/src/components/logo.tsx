import { AppLogo } from "@johnhan0313-git/shared/brand";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <AppLogo appId="readhub" size={32} className="h-8 w-8 shrink-0 rounded-lg" alt="ReadHub" />
      <span className="text-lg font-semibold tracking-tight text-slate-900">
        <span className="text-brand-600">n</span>
        ews
      </span>
    </span>
  );
}
