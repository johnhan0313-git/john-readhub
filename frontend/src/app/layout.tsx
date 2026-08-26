import type { Metadata } from "next";
import { Noto_Sans_SC } from "next/font/google";

import { Navbar } from "@/shared/ui/navbar";
import { Providers } from "@/shared/ui/providers";
import "./globals.css";

const notoSans = Noto_Sans_SC({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "news - 新闻聚合阅读",
  description: "多源新闻爬取、分类汇总与阅读平台",
  icons: {
    icon: "https://shared.cool-app.me/logos/readhub.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className={`${notoSans.variable} font-sans app-shell`}>
        <Providers>
          <Navbar />
          <main className="mx-auto max-w-6xl px-4 pb-16 pt-6 sm:px-6">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
