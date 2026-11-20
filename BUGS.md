# Bug reports

Each bug is written so a developer can fix it in one go. Web bugs 1 to 3 were reproduced by me on 21 Nov 2026 (Chrome, logged out) and are pinned by the strict-xfail tests in `tests/test_web_live.py`. App bugs 4 to 6 come from user reviews. I could not reproduce them without an app account, so they are marked as such.

---

## BUG-1: The footer "Refunds" link opens "Post not found"
- **Where:** https://front.page/ → footer → Refunds (`/s/refunds`)
- **Steps:** 1. Open https://front.page/ logged out. 2. Click **Refunds** in the footer.
- **Expected:** the refund and cancellation policy, like the sibling pages `/s/terms`, `/s/privacy` and `/s/about`, which all load.
- **Actual:** the feed layout with **"Post not found"**. The page title reads "Post refunds | Trading Discussion | FrontPage", so the `/s/:slug` route seems to treat `refunds` as a post id instead of a static policy page.
- **Why it matters:**
  - Several 1-star reviews are about subscription auto-debit and asking for refunds.
  - Payment gateways and app stores expect a reachable refund policy.
- **Evidence:** `evidence/refunds_page_1280.png`; test `test_refund_policy_page_has_content`.

## BUG-2: `/sitemap.xml` is an HTML "Stock Not Found" page
- **Steps:** open https://front.page/sitemap.xml (or `/sitemap_index.xml`).
- **Expected:** an XML sitemap (`Content-Type: application/xml`, `<urlset>` or `<sitemapindex>`).
- **Actual:** HTTP 200, `text/html`, a page titled "sitemap.xml | FrontPage" saying "Stock Not Found". The stock-symbol route catches it. `robots.txt` has no `Sitemap:` line either.
- **Why it matters:** search engines cannot find the stock and club discussion pages, which are the site's organic traffic.
- **Evidence:** `evidence/sitemap_1280.png`; test `test_sitemap_is_xml`.

## BUG-3: Unknown URLs return 200 instead of 404 (soft 404)
- **Steps:** `curl -I https://front.page/qa-radar-this-page-does-not-exist`
- **Expected:** HTTP 404.
- **Actual:** HTTP 200, with a "Stock Not Found" page titled after the URL.
- **Why it matters:** any typo or junk URL becomes an indexable page, and Google reports these as soft 404s.
- **Test:** `test_unknown_path_is_404`.

## BUG-4 (from reviews): Sign-up stuck on "Tell us your interests"
- **Reports:** 10 Aug 2025 (v17.3.3), 17 Nov 2025 (v18.0.3), 24 Nov 2025 (v18.0.3). It persisted across two releases.
- **User steps:** a new account selects 3 or more interests or clubs, taps continue, and the spinner returns to the same screen. Re-selecting loops again.
- **What to check first:**
  - the response of the "save interests" call (a non-2xx or a timeout that the UI swallows);
  - whether the call is made twice when several clubs are selected quickly;
  - behaviour on slow networks.
- **Automation idea:** a sign-up flow test on an emulator with a throttled network profile, asserting the next screen appears within N seconds.

## BUG-5 (from reviews): Certificate error locked users out on 19 Jun 2026
- **Reports:** 4 reviews on 19 Jun 2026 (v18.0.4) quoting "chain validation failed", "certificate invalid path expired" and "java script not…", plus a login failure the same day.
- **Likely cause:** an expired or incomplete TLS certificate chain on an API host. Android rejects incomplete chains that some desktop browsers accept.
- **Prevention, already in this repo:** `test_tls_certificate_not_expiring_soon` fails 14 days before the certificate expires. It runs daily at 08:00 IST in CI, before market open. It should also be pointed at each API host the app calls.

## BUG-6 (from reviews): Server errors and freezes on 25 Jun 2026 (v18.0.5)
- **Reports:** 7 bug reviews in one day ("Server Misbehaving", "server error at the time of trading", hangs). This is the largest single-day cluster in 19 months.
- **Ask:** match the day against backend error rates. If it was a release regression, a canary or staged rollout gate on error rate would have caught it. The analysis flags any day with 3 or more bug reviews, so it can also be run as an alert.
