from app.core.i18n import get_risk_label, get_notification_copy


def test_risk_label_english():
    assert get_risk_label("FRESH", "en") == "Fresh — sell at your convenience"


def test_risk_label_swahili():
    assert get_risk_label("AT_RISK", "sw") == "Uza ndani ya masaa 24"


def test_notification_copy_english():
    result = get_notification_copy(
        "notify_critical_shipment",
        "en",
        crop="Tomatoes",
    )
    assert "Tomatoes" in result
    assert "critical risk" in result


def test_notification_copy_fallback():
    result = get_notification_copy(
        "notify_critical_shipment",
        "fr",
        crop="Tomatoes",
    )
    assert "Tomatoes" in result
    assert "critical risk" in result
