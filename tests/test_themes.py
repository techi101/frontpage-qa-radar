"""Offline: the theme rules on real-style review text, including Hinglish traps."""
import pytest
from themes import tag

CASES = [
    ("Stuck on registration at \"tell us your interests\" app doesn't proceed further", "onboarding_stuck"),
    ("keeps logging me out when I click any join button", "login_logout"),
    ("the P/L amount displayed for the active trade is completely inaccurate", "pnl_or_price_wrong"),
    ("always getting a server error at the time of trading", "order_stuck_or_error"),
    ("it's showing chain validation failed, I am a premium member", "ssl_or_app_load_error"),
    ("it's always shows Mcx data temporary unavailable", "data_or_search_missing"),
    ("The app falsely shows that the daily trade limit has been reached even when no trades are made", "limit_shown_wrongly"),
    ("bahut hang karta h proper work nhi karta", "crash_freeze_slow"),
]


@pytest.mark.parametrize("text,theme", CASES)
def test_bug_themes(text, theme):
    assert theme in tag(text)[0]


@pytest.mark.parametrize("text", [
    "pahale isme rupe nahi lagte the but ab 999 rupees lag rahe hai",      # Hindi 'lag' = costs, not lag
    "premium mangne lag Gaya",
    "Please add basket order option, I cannot execute option trades one by one",  # feature ask, not a defect
    "There is no option to exit partially from the trade positions",
    "too many ads",
])
def test_not_bugs(text):
    assert tag(text)[0] == []


def test_feature_ask_goes_to_product():
    assert "missing_instrument_or_feature" in tag("Please provide Sensex option")[1]
