"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth/context";
import { useTranslation } from "@/lib/localization/context";
import { LanguageSelector } from "@/components/ui/LanguageSelector";
import { Sprout, LogOut, User as UserIcon } from "lucide-react";

export const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const { t } = useTranslation();

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[#E5E0D8] shadow-xs">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
        {/* Logo & Platform Name */}
        <Link href={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-[#1E3A2B] text-white flex items-center justify-center shadow-xs group-hover:bg-[#284D3A] transition-colors">
            <Sprout className="w-6 h-6 text-[#86EFAC]" />
          </div>
          <div>
            <span className="font-bold text-lg text-[#1E3A2B] tracking-tight block leading-tight">
              {t.app.name}
            </span>
            <span className="text-[11px] text-[#556059] block leading-tight font-medium">
              {t.app.tagline}
            </span>
          </div>
        </Link>

        {/* Controls: Language & Auth */}
        <div className="flex items-center gap-2">
          <LanguageSelector compact />

          {isAuthenticated && user && (
            <div className="flex items-center gap-2 pl-1 border-l border-[#E5E0D8]">
              <Link
                href="/profile"
                className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-sm text-[#1E3A2B] hover:bg-[#E8F0EC] transition-colors"
                title={user.full_name}
              >
                <div className="w-7 h-7 rounded-full bg-[#1E3A2B] text-white flex items-center justify-center text-xs font-semibold">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : <UserIcon className="w-4 h-4" />}
                </div>
                <span className="hidden sm:inline font-medium text-xs max-w-[100px] truncate">
                  {user.full_name}
                </span>
              </Link>
              <button
                type="button"
                onClick={logout}
                className="p-2 text-[#78857E] hover:text-[#C92A2A] rounded-lg hover:bg-[#FFE3E3] transition-colors"
                title={t.auth.signOut}
                aria-label={t.auth.signOut}
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
