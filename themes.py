"""Tag FrontPage Play Store reviews (English and Hinglish) into QA bug themes vs product feedback.
Rules, not a model: every tag can be traced to the words that triggered it, and a hand-checked sample measures precision."""
import re

# QA bugs: something the app does wrong that a tester can reproduce
BUGS = {
    "onboarding_stuck": r"(regist|sign ?up|onboard|interest|club).{0,80}(stuck|loading|not mov|not go|not proceed|can'?t proceed|forward|hang)"
                        r"|(stuck|loading).{0,60}(regist|sign ?up|interest|club)",
    "login_logout": r"login again|log(s|ging|ged)? ?(me )?(out|off)|logout|login (issue|problem|error|nahi|not)|unable to log ?in|can'?t log ?in|otp",
    "pnl_or_price_wrong": r"(p ?&? ?l|pnl|profit|loss|price|ltp|premium value|trade value|average).{0,80}(wrong|inaccurat|different|mismatch|not (correct|accurate|match)|galat|incorrect)"
                          r"|(wrong|inaccurat|different|galat|incorrect).{0,40}(p ?&? ?l|pnl|price|ltp)|not accurate with live|late indication|delay(ed)? (price|data)",
    "order_stuck_or_error": r"order.{0,60}(stuck|not (working|placed|executing|execute)|fail|error)|\berror\b|unusual load|not able to place|doesn'?t execut",
    "limit_shown_wrongly": r"limit.{0,60}(reached|exceed).{0,80}(no|without|even|zero|0) trade|falsely shows",
    "ad_reward_not_given": r"(watch|watched|see) (the )?ad.{0,80}(no |without |not )(reward|credit|trade)|without reward",
    "crash_freeze_slow": r"crash|freez|\bhang(s|ing)?\b|hang karta|(app|it)('?s)? (is )?not open|doesn'?t open|not open(ing)? (properly|in|at|during)|slow|\blagg(ing|y)\b|\blags\b|\blag\b(?! ?(gaya|gya|rah|te\b|ta\b|ti\b))|not loading|blank screen",
    "data_or_search_missing": r"(data|feed).{0,30}(unavailable|not (showing|coming|available))|temporar(il)?y unavailable|not showing in search|not (showing|found) in search|previously i got|earlier .{0,30}(was there|available)",
    "ssl_or_app_load_error": r"certificat|chain validation|java ?script|app opening problem|weird error",
    "display_or_chart_bug": r"display (issue|problem)|chart (is |isn'?t |not )?(visible|showing|loading)|chart not|candles? not|overlap|ui (bug|issue)",
}
# product feedback: real, but not a QA defect
PRODUCT = {
    "too_many_ads": r"\bads?\b|\badds\b|advert|advertis",
    "trade_limits_or_premium": r"limit|30 trade|5 trade|premium|subscription|paid|not free|999|paisa|money",
    "missing_instrument_or_feature": r"sensex|crude|commodit|basket|strategy builder|option chain|bse\b|mcx|add (a )?chart|hedg",
    "billing_or_autodebit": r"debit|auto ?renew|refund|charged|deduct",
}


FEATURE_ASK = r"basket|partial|brokerage|no option|please add|plz add|add (a |the )?(feature|option)|introduce|missing|sensex"


def tag(text):
    t = (text or "").lower()
    bugs = [k for k, p in BUGS.items() if re.search(p, t)]
    prod = [k for k, p in PRODUCT.items() if re.search(p, t)]
    # a feature request phrased as "can't do X" is product feedback, not a defect, unless real failure words appear too
    if bugs and re.search(FEATURE_ASK, t) and not re.search(r"crash|hang|stuck|error|wrong|inaccurat|log(ging|s)? (me )?out|slow|freez", t):
        prod = sorted(set(prod) | {"missing_instrument_or_feature"}); bugs = []
    return bugs, prod
