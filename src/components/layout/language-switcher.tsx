"use client";

import { useI18n } from "@/i18n/client";
import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { locales, type Locale } from "@/i18n/config";

const localeLabels: Record<Locale, string> = {
  en: "English",
  sw: "Kiswahili",
};

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();

  return (
    <Select value={locale} onValueChange={setLocale}>
      <SelectTrigger className="w-[180px]">
        <Globe className="size-4 mr-2" />
        <SelectValue placeholder="Language" />
      </SelectTrigger>
      <SelectContent>
        {locales.map((l) => (
          <SelectItem key={l} value={l}>
            {localeLabels[l]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}