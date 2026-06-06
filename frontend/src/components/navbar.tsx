"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Clock, Newspaper } from "lucide-react";

import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "资讯", icon: Newspaper },
  { href: "/timeline", label: "时间线", icon: Clock },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="site-header">
      <div className="mx-auto flex h-full max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
            R
          </span>
          <span className="text-lg font-semibold text-slate-900">ReadHub</span>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-brand-50 text-brand-700"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900",
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
