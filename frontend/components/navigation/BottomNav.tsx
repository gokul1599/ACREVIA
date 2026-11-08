"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "@/lib/localization/context";
import { useAuth } from "@/lib/auth/context";
import {
  LayoutDashboard,
  Camera,
  BotMessageSquare,
  Activity,
  Layers,
} from "lucide-react";

export const BottomNav: React.FC = () => {
  const pathname = usePathname();
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) return null;

  const navItems = [
    {
      href: "/dashboard",
      label: t.nav.dashboard,
      icon: LayoutDashboard,
      isActive: pathname === "/dashboard",
    },
    {
      href: "/crops",
      label: t.nav.crops,
      icon: Layers,
      isActive: pathname.startsWith("/crops"),
    },
    {
      href: "/diagnosis",
      label: t.nav.diagnosis,
      icon: Camera,
      isActive: pathname.startsWith("/diagnosis"),
      highlight: true,
    },
    {
      href: "/knowledge",
      label: t.nav.knowledge,
      icon: BotMessageSquare,
      isActive: pathname.startsWith("/knowledge"),
    },
    {
      href: "/croppulse",
      label: t.nav.croppulse,
      icon: Activity,
      isActive: pathname.startsWith("/croppulse"),
    },
  ];

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-[#E5E0D8] shadow-lg pb-safe"
      aria-label="Mobile Navigation"
    >
      <div className="max-w-md mx-auto grid grid-cols-5 h-16">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center py-1 transition-colors touch-target ${
                item.isActive
                  ? "text-[#1E3A2B] font-bold"
                  : "text-[#78857E] hover:text-[#1E3A2B]"
              }`}
            >
              <div
                className={`p-1 rounded-full transition-all ${
                  item.highlight
                    ? "bg-[#1E3A2B] text-white -mt-4 shadow-md p-2.5 border-2 border-white"
                    : item.isActive
                    ? "bg-[#E8F0EC]"
                    : ""
                }`}
              >
                <Icon className={item.highlight ? "w-6 h-6" : "w-5 h-5"} />
              </div>
              <span className={`text-[10px] tracking-tight mt-0.5 truncate max-w-[64px] ${item.highlight ? "font-bold text-[#1E3A2B]" : ""}`}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
