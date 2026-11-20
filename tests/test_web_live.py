"""Live checks against the public front.page website (read-only, a few requests, robots.txt respected).
Known bugs are strict xfails: the suite stays green while the bug exists and turns red (XPASS) the day it is fixed,
which tells you to remove the marker. Run: LIVE=1 python -m pytest tests/test_web_live.py -v"""
import os, re, socket, ssl, datetime as dt
import urllib.request, urllib.error
import pytest

pytestmark = pytest.mark.skipif(os.environ.get("LIVE") != "1", reason="set LIVE=1 to hit the real site")
BASE = "https://front.page"
UA = {"User-Agent": "Mozilla/5.0 (frontpage-qa-radar smoke test)"}


def get(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=30)
        return r.status, r.headers.get("content-type", ""), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("content-type", ""), e.read().decode("utf-8", "replace")


def title(html):
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    return m.group(1) if m else ""


@pytest.mark.parametrize("path,must", [("/", "FrontPage"), ("/popular", "Popular"), ("/paper-trade", "Paper Trading"),
                                       ("/s/about", "About"), ("/s/terms", "Terms"), ("/s/privacy", "Privacy")])
def test_key_pages_load(path, must):
    status, _, html = get(path)
    assert status == 200 and must.lower() in title(html).lower()


@pytest.mark.xfail(strict=True, reason="BUG-1: footer 'Refunds' link /s/refunds renders 'Post not found'")
def test_refund_policy_page_has_content():
    status, _, html = get("/s/refunds")
    assert status == 200 and "Post not found" not in html and "refund" in title(html).lower() and "Post refunds" not in title(html)


@pytest.mark.xfail(strict=True, reason="BUG-2: /sitemap.xml returns an HTML 'Stock Not Found' page, not an XML sitemap")
def test_sitemap_is_xml():
    status, ctype, body = get("/sitemap.xml")
    assert status == 200 and "xml" in ctype and ("<urlset" in body or "<sitemapindex" in body)


@pytest.mark.xfail(strict=True, reason="BUG-3: unknown URLs return HTTP 200 (soft 404) instead of 404")
def test_unknown_path_is_404():
    status, _, _ = get("/qa-radar-this-page-does-not-exist")
    assert status == 404


def test_tls_certificate_not_expiring_soon():
    """The 19 Jun 2026 review spike was 'chain validation failed' / 'certificate expired'. Alert 14 days early."""
    ctx = ssl.create_default_context()
    with socket.create_connection(("front.page", 443), timeout=20) as s, ctx.wrap_socket(s, server_hostname="front.page") as t:
        cert = t.getpeercert()
    exp = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=dt.timezone.utc)
    assert (exp - dt.datetime.now(dt.timezone.utc)).days > 14, f"certificate expires {exp:%d %b %Y}"
