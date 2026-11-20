"""QA radar for FrontPage: turn public Play Store reviews into ranked, versioned bug themes.
Input: data/reviews_raw.json (newest 3,000 reviews, fetched with google-play-scraper on 21 Nov 2026).
Output: out/summary.json and demo/data.js (the dashboard reads it).   Run: python analysis.py"""
import json
from pathlib import Path
import pandas as pd
import themes

ROOT = Path(__file__).resolve().parent
LABEL = {
    "crash_freeze_slow": "Freezes, crashes or slow (often in market hours)",
    "order_stuck_or_error": "Order stuck or server error",
    "pnl_or_price_wrong": "P&L or price looks wrong",
    "login_logout": "Login fails or logs user out",
    "ssl_or_app_load_error": "App will not load (certificate or script error)",
    "data_or_search_missing": "Market data or stock missing",
    "onboarding_stuck": "Sign-up stuck at “select interests”",
    "display_or_chart_bug": "Display or chart bug",
    "ad_reward_not_given": "Ad watched, reward not given",
    "limit_shown_wrongly": "“Limit reached” with no trades",
    "too_many_ads": "Too many ads",
    "trade_limits_or_premium": "Trade limits and premium",
    "missing_instrument_or_feature": "Missing instrument or feature (Sensex, basket orders…)",
    "billing_or_autodebit": "Billing or auto-debit",
}
# hand checks, done by reading the reviews (see README)
HAND_CHECK = {"first_pass": {"n": 60, "real_bug": 53, "right_theme": 51},
              "after_fixes_fresh_sample": {"n": 40, "real_bug": 39, "right_theme": 37},
              "untagged_negative_sample": {"n": 40, "missed_bugs": 8, "note": "patterns for 5 of them added afterwards"}}


def load():
    d = pd.read_json(ROOT / "data" / "reviews_raw.json")
    d["at"] = pd.to_datetime(d["at"])
    d[["bugs", "prod"]] = d.content.apply(lambda t: pd.Series(themes.tag(t)))
    return d


def summarise(d):
    neg = d[d.score <= 3]
    bug = neg[neg.bugs.str.len() > 0]
    count = lambda col, keys: {k: int(sum(k in x for x in neg[col])) for k in keys}
    bugs = dict(sorted(count("bugs", themes.BUGS).items(), key=lambda kv: -kv[1]))
    prod = dict(sorted(count("prod", themes.PRODUCT).items(), key=lambda kv: -kv[1]))
    # monthly: share of ALL reviews that report a bug, so months with more reviews are comparable
    d = d.assign(month=d["at"].dt.to_period("M").astype(str), is_bug=d.bugs.str.len() > 0, is_neg=d.score <= 3)
    m = d.groupby("month").agg(reviews=("score", "size"), bug_reports=("is_bug", "sum"), negative=("is_neg", "sum"), avg_stars=("score", "mean")).reset_index()
    m = m[m.reviews >= 30]
    # app versions with the most bug reports
    v = bug.groupby(bug.reviewCreatedVersion.fillna("unknown")).size().sort_values(ascending=False).head(6)
    vtot = neg.groupby(neg.reviewCreatedVersion.fillna("unknown")).size()
    quotes = {}
    for k in bugs:
        rows = bug[bug.bugs.apply(lambda x: k in x)].sort_values("thumbsUpCount", ascending=False)
        quotes[k] = [{"text": r.content[:220], "stars": int(r.score), "date": str(r["at"])[:10], "version": r.reviewCreatedVersion or "unknown"}
                     for _, r in rows.head(2).iterrows()]
    market_hours = int(neg.content.str.contains(r"market (?:time|hour|open)|live market|9[:.]15|opening|execution", case=False).sum())
    # incidents: days where 3+ reviews report a bug; usually an outage or a bad release, worth a post-mortem
    day = bug.assign(day=bug["at"].dt.strftime("%Y-%m-%d")).groupby("day")
    incidents = []
    for k, g in day:
        if len(g) >= 3:
            th = pd.Series([b for x in g.bugs for b in x]).value_counts()
            incidents.append({"day": k, "bug_reports": int(len(g)), "top_theme": th.index[0],
                              "versions": sorted({str(v) for v in g.reviewCreatedVersion.dropna()}), "example": g.content.iloc[0][:160]})
    replied = float(neg.replyContent.notna().mean())
    return {
        "fetched": "21 Nov 2026", "reviews": int(len(d)), "from": str(d["at"].min())[:10], "to": str(d["at"].max())[:10],
        "avg_stars": float(d.score.mean()), "negative": int(len(neg)), "negative_with_bug": int(len(bug)),
        "bug_themes": bugs, "product_themes": prod, "labels": LABEL, "monthly": m.to_dict("records"),
        "versions": [{"version": k, "bug_reports": int(c), "negative": int(vtot.get(k, 0))} for k, c in v.items()],
        "quotes": quotes, "market_hours_mentions": market_hours, "incidents": incidents, "negative_reply_rate": replied, "hand_check": HAND_CHECK,
        "app": json.loads((ROOT / "data" / "app_meta.json").read_text()),
    }


def main():
    s = summarise(load())
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "summary.json").write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "demo").mkdir(exist_ok=True)
    (ROOT / "demo" / "data.js").write_text("window.DATA = " + json.dumps(s, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(json.dumps({k: s[k] for k in ["reviews", "from", "to", "negative", "negative_with_bug", "bug_themes", "product_themes",
                                        "versions", "market_hours_mentions", "negative_reply_rate", "incidents"]}, indent=1))
    print(s["monthly"][-8:])


if __name__ == "__main__":
    main()
