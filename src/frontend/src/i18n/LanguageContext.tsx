import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { LANGS, MESSAGES, type Lang } from "./messages";

const STORAGE_KEY = "maive.lang";

// DEC-014: default to "en" for ALL clients. We do NOT sniff Accept-Language
// or navigator.language — the user must opt into "es" explicitly.
const DEFAULT_LANG: Lang = "en";

function loadInitialLang(): Lang {
  if (typeof window === "undefined") return DEFAULT_LANG;
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "en" || stored === "es") return stored;
  return DEFAULT_LANG;
}

interface LanguageContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(loadInitialLang);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((next: Lang) => {
    if (LANGS.includes(next)) setLangState(next);
  }, []);

  const t = useCallback(
    (key: string) => MESSAGES[lang][key] ?? MESSAGES.en[key] ?? key,
    [lang]
  );

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used inside <LanguageProvider>");
  }
  return ctx;
}
