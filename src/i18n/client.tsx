"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { locales, type Locale, defaultLocale } from "./config";

interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, namespace?: string) => string;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

const messagesCache: Record<Locale, Record<string, any>> = {} as any;

async function loadMessages(locale: Locale): Promise<Record<string, any>> {
  if (messagesCache[locale]) return messagesCache[locale];
  const mod = await import(`../messages/${locale}.json`);
  messagesCache[locale] = mod.default;
  return mod.default;
}

function getNestedValue(obj: any, path: string): string {
  return path.split(".").reduce((acc, key) => acc?.[key], obj) ?? path;
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);
  const [messages, setMessages] = useState<Record<string, any> | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Read locale from cookie
    if (typeof document !== "undefined") {
      const cookieLocale = document.cookie
        .split("; ")
        .find((row) => row.startsWith("locale="))
        ?.split("=")[1] as Locale | undefined;
      const initialLocale = (cookieLocale && locales.includes(cookieLocale)) ? cookieLocale : defaultLocale;
      setLocaleState(initialLocale);
      loadMessages(initialLocale).then(setMessages);
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    document.cookie = `locale=${newLocale}; path=/; max-age=${60 * 60 * 24 * 365}; samesite=lax`;
    loadMessages(newLocale).then(setMessages);
    // Reload to update server-rendered content
    window.location.reload();
  };

  const t = (key: string, namespace?: string): string => {
    if (!messages) return key;
    const fullKey = namespace ? `${namespace}.${key}` : key;
    return getNestedValue(messages, fullKey) ?? key;
  };

  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}

export function useT(namespace?: string) {
  const { t, locale } = useI18n();
  return (key: string) => t(key, namespace);
}