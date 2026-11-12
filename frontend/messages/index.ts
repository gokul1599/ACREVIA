// ACREVIA Multilingual Dictionary Index (English, Telugu, Hindi)
import { en } from "./en";
import { te } from "./te";
import { hi } from "./hi";

export type Locale = "en" | "te" | "hi";

export const translations = {
  en,
  te,
  hi,
};

export type TranslationDictionary = typeof en;
