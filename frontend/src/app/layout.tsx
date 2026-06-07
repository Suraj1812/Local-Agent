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
    default: "FirstAI AP Automation",
    template: "%s | FirstAI AP"
  },
  description: "AI-powered accounts payable automation for invoice matching, exceptions, journal posting, and ERP sync.",
  applicationName: "FirstAI AP",
  icons: {
    icon: "/icon"
  },
  openGraph: {
    title: "FirstAI AP Automation",
    description: "AI-powered accounts payable automation for invoice matching, exceptions, journal posting, and ERP sync.",
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
