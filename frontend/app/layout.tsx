// ACREVIA Root Layout - Progressive Web Application Shell (Telangana, India)
import type { Metadata, Viewport } from "next";
import "./globals.css";
import { LocalizationProvider } from "@/lib/localization/context";
import { AuthProvider } from "@/lib/auth/context";
import { Header } from "@/components/navigation/Header";
import { BottomNav } from "@/components/navigation/BottomNav";
import { OfflineBanner } from "@/components/ui/OfflineBanner";
import React from "react";

export const metadata: Metadata = {
  title: "ACREVIA — Agricultural Intelligence Platform",
  description:
    "Research-grade computer vision diagnostics, KrishiBrain agricultural knowledge RAG, and foliar health monitoring for Cotton, Rice, and Chilli farmers in Telangana.",
  manifest: "/manifest.json",
  icons: {
    icon: "/icons/icon-192.png",
    apple: "/icons/icon-192.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#1E3A2B",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="te">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body className="min-h-screen flex flex-col bg-[#F7F5F0] text-[#1A241F]">
        <LocalizationProvider>
          <AuthProvider>
            <OfflineBanner />
            <Header />
            <main className="flex-1 pb-20 md:pb-8">{children}</main>
            <BottomNav />
            {/* Service Worker Registration */}
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  if ('serviceWorker' in navigator) {
                    window.addEventListener('load', function() {
                      navigator.serviceWorker.register('/sw.js').catch(function(err) {
                        console.warn('ACREVIA: ServiceWorker registration failed: ', err);
                      });
                    });
                  }
                `,
              }}
            />
          </AuthProvider>
        </LocalizationProvider>
      </body>
    </html>
  );
}
