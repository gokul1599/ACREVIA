"use client";

import React from "react";
import { useTranslation } from "@/lib/localization/context";
import { Locale } from "@/messages";
import { Globe } from "lucide-react";

export const LanguageSelector: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const { locale, setLocale } = useTranslation();

  const options: { code: Locale; label: string }[] = [
    { code: "te", label: "తెలుగు" },
    { code: "en", label: "English" },
    { code: "hi", label: "हिंदी" },
  ];

  return (
    <div className="flex items-center gap-1 bg-[#E8F0EC] p-1 rounded-lg border border-[#C8C0B5]">
      {!compact && <Globe className="w-4 h-4 text-[#1E3A2B] ml-1 mr-0.5 shrink-0" aria-hidden="true" />}
      {options.map((opt) => (
        <button
          key={opt.code}
          type="button"
          onClick={() => setLocale(opt.code)}
          className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all touch-target ${
            locale === opt.code
              ? "bg-[#1E3A2B] text-white shadow-xs"
              : "text-[#1E3A2B] hover:bg-[#D5E5DC]"
          }`}
          aria-pressed={locale === opt.code}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
};
