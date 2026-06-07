import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"]
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"]
});

export const metadata: Metadata = {
  title: {
    default: "FirstAI",
    template: "%s | FirstAI"
  },
  description: "Fast local AI agent workspace with planning, memory, and file-aware chat.",
  applicationName: "FirstAI",
  icons: {
    icon: "/icon"
  },
  openGraph: {
    title: "FirstAI",
    description: "Fast local AI agent workspace with planning, memory, and file-aware chat.",
    type: "website"
  }
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
