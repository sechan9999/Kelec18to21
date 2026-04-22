import type { Metadata } from "next";
import { Inter, Roboto_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const robotoMono = Roboto_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "한국 대통령 선거 대시보드 | Korean Presidential Election Dashboard",
  description: "18대~21대 한국 대통령 선거 결과 분석 대시보드 (2012–2025)",
  openGraph: {
    title: "K18–K21 Korean Presidential Election Dashboard",
    description:
      "Interactive analytics dashboard for 18th–21st Korean presidential elections.",
    type: "website",
    locale: "ko_KR",
  },
  twitter: {
    card: "summary_large_image",
    title: "K18–K21 Korean Presidential Election Dashboard",
    description:
      "Election analytics, regional swings, audit scorecards, and reproducible exports.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: "Korean Presidential Elections 18th–21st Dashboard",
    description:
      "Dashboard with analytics and audit summaries for Korean presidential elections from 2012 to 2025.",
    inLanguage: ["ko", "en"],
  };

  return (
    <html
      lang="ko"
      className={`${inter.variable} ${robotoMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        {children}
      </body>
    </html>
  );
}
