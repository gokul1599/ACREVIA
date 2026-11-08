"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Locale, translations, TranslationDictionary } from "@/messages";

interface LocalizationContextType {
  locale: Locale;
  setLocale: (loc: Locale) => void;
  t: TranslationDictionary;
}

const LocalizationContext = createContext<LocalizationContextType | null>(null);

export const LocalizationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<Locale>("te"); // Default to Telugu for Telangana farmers

  useEffect(() => {
    try {
      const saved = localStorage.getItem("acrevia_locale") as Locale;
      if (saved && (saved === "en" || saved === "te" || saved === "hi")) {
        setLocaleState(saved);
      }
    } catch {
      // localStorage may fail in private mode
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    try {
      localStorage.setItem("acrevia_locale", newLocale);
      document.documentElement.lang = newLocale;
    } catch {
      // ignore
    }
  };

  const t = translations[locale] || translations.te;

  return (
    <LocalizationContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocalizationContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(LocalizationContext);
  if (!context) {
    // Return Telugu fallback if outside provider
    return {
      locale: "te" as Locale,
      setLocale: () => {},
      t: translations.te,
    };
  }
  return context;
};
