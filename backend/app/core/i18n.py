_TRANSLATIONS = {
    "en": {
        "risk_fresh": "Fresh — sell at your convenience",
        "risk_at_risk": "Sell within 24 hours",
        "risk_critical": "Critical — sell immediately",
        "notify_critical_shipment": "Your {crop} shipment has entered critical risk. Consider selling immediately.",
        "notify_manifest_changed": "Your manifest has been updated. Please re-sync for the latest pickup schedule.",
        "otp_message": "Your FreshRoute verification code is: {code}. It expires in {minutes} minutes.",
    },
    "sw": {
        "risk_fresh": "Mpya — uza unapotaka",
        "risk_at_risk": "Uza ndani ya masaa 24",
        "risk_critical": "Hatari — uza mara moja",
        "notify_critical_shipment": "Shipment yako ya {crop imeingia katika hatari. Fikiria kuza mara moja.",
        "notify_manifest_changed": "Orodha yako ya pickup imesasishwa. Tafadhali sync upya kwa ratiba ya sasa.",
        "otp_message": "Kodi yako ya uthibitisho ya FreshRoute ni: {code}. Inaisha baada ya dakika {minutes}.",
    },
}

DEFAULT_LOCALE = "en"

_RISK_TIER_MAP = {
    "FRESH": "risk_fresh",
    "AT_RISK": "risk_at_risk",
    "CRITICAL": "risk_critical",
}


def get_risk_label(risk_tier: str, locale: str = DEFAULT_LOCALE) -> str:
    lang = _TRANSLATIONS.get(locale, _TRANSLATIONS[DEFAULT_LOCALE])
    key = _RISK_TIER_MAP.get(risk_tier, "risk_fresh")
    return lang[key]


def get_notification_copy(template_key: str, locale: str = DEFAULT_LOCALE, **kwargs) -> str:
    lang = _TRANSLATIONS.get(locale, _TRANSLATIONS[DEFAULT_LOCALE])
    template = lang.get(template_key, "")
    return template.format(**kwargs) if kwargs else template
