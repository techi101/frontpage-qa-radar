"""Fetch the newest Play Store reviews for FrontPage (in.crowdware.one) into data/. Run: python fetch_reviews.py"""
import json
import pandas as pd
from google_play_scraper import app, reviews, Sort

APP = "in.crowdware.one"
meta = app(APP, lang="en", country="in")
rows, tok = [], None
for _ in range(15):
    r, tok = reviews(APP, lang="en", country="in", sort=Sort.NEWEST, count=200, continuation_token=tok)
    rows += r
    if not tok or not r:
        break
d = pd.DataFrame(rows)[["reviewId", "at", "score", "content", "thumbsUpCount", "reviewCreatedVersion", "replyContent"]]
d["at"] = d["at"].astype(str)
d.to_json("data/reviews_raw.json", orient="records", force_ascii=False, indent=0)
json.dump({k: str(meta.get(k)) for k in ["title", "installs", "score", "ratings", "reviews", "version", "updated"]}, open("data/app_meta.json", "w"))
print(len(d), "reviews")
