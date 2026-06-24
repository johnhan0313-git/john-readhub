import { cn } from "@/lib/utils";

function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
      className={cn("h-8 w-8 shrink-0", className)}
    >
      <rect width="32" height="32" rx="8" fill="url(#news-logo-gradient)" />
      <rect x="8" y="9" width="16" height="2.5" rx="1.25" fill="white" fillOpacity="0.95" />
      <rect x="8" y="14.75" width="11" height="2.5" rx="1.25" fill="white" fillOpacity="0.85" />
      <rect x="8" y="20.5" width="7" height="2.5" rx="1.25" fill="white" fillOpacity="0.75" />
      <defs>
        <linearGradient id="news-logo-gradient" x1="4" y1="4" x2="28" y2="28" gradientUnits="userSpaceOnUse">
          <stop stopColor="#0ea5e9" />
          <stop offset="1" stopColor="#0284c7" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <LogoMark />
      <span className="text-lg font-semibold tracking-tight text-slate-900">
        <span className="text-brand-600">n</span>
        ews
      </span>
    </span>
  );
}
