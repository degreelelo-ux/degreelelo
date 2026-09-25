# DegreeLelo

Lead-generation website for DegreeLelo, an Indian education admission consultancy covering Engineering, Management, Medical, and Study Abroad guidance.

Plain HTML/CSS/JS, no build step, no framework. Deployable as-is on GitHub Pages.

## How the enquiry form works

The enquiry popup (present on every page) is a custom-styled modal that submits to a Google Apps Script Web App bound directly to a Google Sheet, which appends each submission as a new row. Submission is a plain `fetch()` POST (`js/main.js`), and the modal's "Thank you" state only shows once the script's response confirms `{ result: "success" }` — a genuine success signal, not a guess.

(An earlier version of this submitted directly to a Google Form via a hidden iframe. That was abandoned after live testing hit a hard `400` from Google's `/formResponse` endpoint — Google increasingly requires a `fbzx` anti-abuse session token that's only generated when a browser actually loads the real `/viewform` page, which a static POST built ahead of time can't supply. The Apps Script Web App has no such requirement.)

Each field's `name` attribute is still the original Google Form's `entry.XXXXXXX` ID — kept as-is because the Apps Script (below) reads submissions by those same keys, so no HTML changes were needed when switching from the Form to the Script:

| Modal field | Entry ID |
|---|---|
| Full name | `entry.207722185` |
| Phone number | `entry.804843000` |
| Email address | `entry.15042384` |
| City | `entry.287878406` |
| Course of interest | `entry.922132532` |
| Score / percentile | `entry.1558959334` |
| How did you hear about us | `entry.1372671113` |

The submission endpoint (in the `<form action>` in every page's modal markup) is the deployed Apps Script Web App URL, currently:
`https://script.google.com/macros/s/AKfycbw0VbFqKKRZM7UBFx3DDR-11UU6cioS4jWPLb7XWKcc7O0TZ_B11D2T6no9HRSJFIPQWw/exec`

The script itself lives in the target Google Sheet's **Extensions → Apps Script** editor (not in this repo, since Apps Script projects aren't files Git can track) — roughly:

```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var p = e.parameter;
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Timestamp', 'Name', 'Phone', 'Email', 'City', 'Course of Interest', 'Score / Percentile', 'How did you hear about us']);
  }
  sheet.appendRow([new Date(), p['entry.207722185'], p['entry.804843000'], p['entry.15042384'], p['entry.287878406'], p['entry.922132532'], p['entry.1558959334'], p['entry.1372671113']]);
  return ContentService.createTextOutput(JSON.stringify({ result: 'success' })).setMimeType(ContentService.MimeType.JSON);
}
```

**Worth knowing:**
- The request is sent as `FormData` (not JSON) deliberately — that keeps it a CORS "simple request" that skips a preflight `OPTIONS` call, which Apps Script Web Apps don't handle.
- Redeploying the Apps Script (Deploy → Manage deployments → edit → new version) is required after any script code change for the live `/exec` URL to pick it up — saving alone isn't enough.
- If the endpoint URL, the script's deployment, or its "Who has access" setting ever changes, update the `<form action>` value across all pages (it's identical on every page, so a single find-and-replace works) — currently only editable directly, no shared JS config constant for it.
- **Confirmed working end-to-end**: request shape verified (correct field mapping, correct content type), and — unlike the earlier Form-based attempt — a genuine network failure was verified to correctly show the error/WhatsApp message instead of silently claiming success.

## Before going live

**WhatsApp Business number** — the "Chat with us on WhatsApp" button is already wired to the real number. If it ever needs to change, it's declared once, at the top of `js/main.js` (`DEGREELELO_CONFIG.whatsappNumber`).

## Structure

```
index.html               Home
about.html                About
engineering.html          Engineering admissions (JEE / COMEDK / MHT-CET)
management.html           Management admissions (CAT / CMAT / MAT / MAH-CET)
medical.html               Medical / NEET counselling guidance
study-abroad.html         Study Abroad (launching soon)
college-predictor.html    Free college predictor tool
blog.html                  Blog (placeholder)
faq.html                    FAQ
contact.html               Contact
privacy-policy.html       Privacy Policy
terms.html                  Terms & Disclaimer
404.html                    Custom 404 page

css/style.css              Design system + all site styles
js/main.js                  Mobile nav, enquiry modal (Apps Script submit), predictor logic
assets/                     Favicon, apple-touch-icon, OG/Twitter card image
robots.txt, sitemap.xml    SEO basics
```

## Notes

- The College Predictor only gives route guidance for Engineering/Management in Karnataka and Maharashtra, per the product's current verified data. Every other combination (including Medical anywhere, and Study Abroad) is intentionally routed to "a counsellor will personally review your profile" — this is deliberate, not a gap to fill in with a fake match.
- Canonical URLs, Open Graph tags, and `sitemap.xml` currently point at `https://degreelelo-ux.github.io/degreelelo` (the default GitHub Pages URL for this repo). If you attach a custom domain, update those in bulk (they're the `SITE_URL` constant equivalent — a simple find-and-replace across the HTML files, `robots.txt`, and `sitemap.xml`).
- No JS framework, no build step. Pages are static HTML; the shared header/footer/modal markup is duplicated per page by design (kept in sync via a local generation script during development, not part of the deployed site).
- **`css/style.css` and `js/main.js` are referenced with a `?v=N` query string** (e.g. `js/main.js?v=2`) on every page, identical across all 13. This is deliberate cache-busting — GitHub Pages' CDN and browsers can hold onto an old copy of these files for a while, which previously caused a live page to keep running stale JS after a deploy (a form submit silently misbehaved because the HTML had updated but the JS hadn't). **Whenever you edit either file, bump the `v=` number on all 13 pages** (a single find-and-replace) so every visitor is guaranteed to fetch the new version rather than a cached one.
