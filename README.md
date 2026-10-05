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
- **Confirmed working end-to-end**: request shape verified (correct field mapping, correct content type), a genuine network failure was verified to correctly show the error/WhatsApp message instead of silently claiming success (unlike the earlier Form-based attempt), and a real test submission has been confirmed to land as a new row in the target Sheet.

## College Directory

`colleges.html` is a filterable directory (state, category, course, search) over `data/colleges.json` — 468 institutions across Engineering, Management, Medical, Law, Design, Distance & Open Education, and Study Abroad, rendered client-side by `js/main.js` (fetch + filter, no framework). It also accepts `?category=`, `?state=`, and `?course=` query params, used by links from the vertical pages and the College Predictor's result box to deep-link into a pre-filtered view.

**The Course filter** is a finer level than Category (e.g. picking "MBBS" or "BDS" within Medical, or "B.Arch" within Design) — deliberately built with no guessing involved. Each institution's `courses` array is populated only from two explicit sources: its row's own fine-grained `Primary Course` value in the spreadsheet (this is only ever `B.Tech`/`MBA`/`MBBS` — a real distinct field, not an inference), or real degree tokens (from a fixed vocabulary — `LLB`, `B.Arch`, `B.Pharm`, `MBBS`, `BDS`, etc.) found by parsing that institution's own "Approvals/programmes" text (e.g. "MBBS, BDS, MD" → three separate course tags). An accreditation-only string like "UGC/AICTE" matches no vocabulary token and correctly produces no course tag. **305 of 468 institutions have at least one course tag; the other 163 simply don't appear when a specific course is selected** (only under "All courses") — that includes all 125 Study Abroad entries, whose notes list broad subject areas ("Specialties: Engineering, Business, AI...") rather than specific degree names, so nothing is guessed to force a course tag there.

**Where the data came from and how it was cleaned:** `data/colleges.json` is a point-in-time export from an internal spreadsheet (`Master_Database_8.xlsx`, `INSTITUTIONS` sheet, 468 rows) with real, deliberate filtering — not a raw dump. Every row is included or excluded by the single `"Active for 2027"` flag; nothing else gates inclusion.

- **Study Abroad (125 institutions, 14 countries — Australia, Canada, Cyprus, Hungary, Ireland, Italy, Japan, Malaysia, Malta, New Zealand, Spain, Sweden, UAE, UK) uses a different note format than the Indian institutions**, and gets its own parsing rules in `build_colleges_json.py` (`STUDY_ABROAD_FEE_RE`, `STUDY_ABROAD_ENTRY_RE`) rather than the Indian `NOTES_FEE_RE`/`NOTES_APPROVALS_RE`/`NOTES_ENTRANCE_RE` patterns, which don't match this vertical's notes at all. `fee` and `entrance_exam` are populated from this vertical's own "Fees/yr:" and "Entry requirement:" fields; there's no equivalent of "Approvals/programmes" (degree tokens), so `courses` and `approvals` stay empty rather than guessed from "Specialties" (a list of broad subject areas, not degree names). The `state` field holds the country name for these rows (the source spreadsheet reuses that column for both), so the Directory splits this into two dropdowns — **State** (Indian states, from every non-Study-Abroad institution) and **Country** (the 14 Study Abroad countries) — both built from `_states`/`_countries` in `build.py`, split by `category != "Study Abroad"` rather than a hardcoded country list. The two filter the same underlying `state` field; `js/main.js` resets whichever one isn't active when you pick a value in the other, so selecting both at once (which would always match zero institutions) isn't possible through the UI. `?country=` works as a deep-link param alongside the existing `?state=`/`?category=`/`?course=`.
- **The `FEES_COMMISSION` sheet (internal commission %, profit margins, payment splits) was never touched.** Nothing from it is in `colleges.json` or anywhere on the site. Same for `LEAD_DATABASE` and partner reps' personal contact numbers from the `PARTNERS` sheet.
- Of the 468 institutions, only **93 are marked `verified: true`** in the JSON (independently confirmed — mostly well-known engineering institutes with real NIRF rankings/placement data). The other 375 (250 Indian + all 125 Study Abroad) are `verified: false` ("Partner-provided (unverified)" in the source). This field is still in the data for anyone who wants to build on it later, but as of the current UI it isn't surfaced on the page — an earlier "Verified" / "Partner network" badge per row was removed on request, so all cards currently render identically regardless of `verified`.
- Any spreadsheet cell reading literally "Needs Verification" (or a longer sentence starting with it, e.g. "Needs Verification - no reliable figure found") was dropped rather than shown — a field with no real value is simply absent from that college's card, never replaced with a placeholder. For the 125 Study Abroad rows, that's nearly every structured field except name, country, fee, and entry requirement — city, website, established year, ranking, and placement are all "Needs Verification" in the source and so don't appear on those cards.
- Fee ranges, entrance exams, and approved programmes were parsed out of each row's free-text "Important Notes" field via regex (the structured fee/exam columns in the source were themselves mostly unfilled) — see the extraction script's `parse_notes()` if this needs re-running.
- **`COURSE_PROGRAMS`, `ADMISSION_ROUTES`, and `FEES_COMMISSION`** (the three internal sheets backing actual admission routing and commission tracking — none of it published) now have one placeholder row per Study Abroad institution too, matching the same "Needs Verification, ready for real numbers" state the other 343 institutions already had. These were previously empty for all 125 Study Abroad rows, which is a separate, internal-operations gap from what's described above for the public site — the Important Notes explicitly flagged this as "intentionally not built yet, pending confirmation that Study Abroad is an active launch vertical" before that confirmation happened.

**This export does not auto-update.** If the source spreadsheet changes, regenerate it with `python3 dev/build_colleges_json.py /path/to/Master_Database.xlsx` (writes `data/colleges.json`), then re-run `python3 dev/build.py` and commit both the regenerated `colleges.html` and the new `data/colleges.json` — there's no live sync. If the record count here ever looks off against the live spreadsheet, that's the first thing to check: it usually means the spreadsheet changed after the last export, not a bug in the extraction logic.

## Brand mark

The logo is a "Compass Pin" &mdash; a location pin with a graduation cap where the lens would be, standing for "the right place of learning, located." It replaced a plain "DL" initials badge. It's inline SVG, defined once in `build.py` as `BRAND_MARK_HEADER` (navy pin on blue, for the header on light backgrounds) and `BRAND_MARK_FOOTER` (navy pin on amber, matching the footer's existing accent-swap convention) and written into every page's header/footer by the generator &mdash; there's no separate logo image file for those two spots. The favicon, apple-touch-icon, and `assets/icon-192.png`/`icon-512.png` are static PNG/ICO exports of the same mark (header colorway) at fixed sizes, rendered once from the SVG and committed as binary files. If the mark ever changes, regenerate them by rendering `BRAND_MARK_HEADER`'s SVG at 1024&times;1024 (e.g. with a headless browser screenshot) and downscaling to 16/32/180/192/512px plus a multi-size `.ico` &mdash; there's no automated pipeline for that, same as `data/colleges.json`.

## Blog

Five articles, one per vertical (Engineering, Management, Medical, Study Abroad, Distance & Open Education), defined as a single `BLOG_POSTS` list in `build.py` and rendered through a shared `blog_post_main()` template &mdash; `blog.html` is the card-grid index, and each post is its own flat file (`blog-<slug>.html`, no subdirectory, so the shared header/footer/asset relative paths needed no changes).

Content is deliberately scoped to **public, generic process information** &mdash; how JoSAA/CSAB counselling works, what NEET counselling documents are commonly asked for, how CAT/CMAT/MAT differ, what study-abroad applications typically require, how open-schooling recognition actually gets decided &mdash; never DegreeLelo-specific claims, institution names, fees, or placement figures. Each post ends with an honest caveat (reusing the `.notice.notice-info` pattern already used elsewhere) pointing out that exact rules/deadlines/documents change and should be verified against the current official source, not assumed from the article. To add a post: append an entry to `BLOG_POSTS` and re-run `build.py` &mdash; it's picked up by both the index grid and the generator's per-post `write()` loop automatically. Because exam/counselling processes genuinely do change over time, these articles are worth an occasional accuracy re-check, same spirit as the College Directory's "doesn't auto-update" caveat above.

## Before going live

**WhatsApp Business number** — the "Chat with us on WhatsApp" button is already wired to the real number. If it ever needs to change, it's declared once, at the top of `js/main.js` (`DEGREELELO_CONFIG.whatsappNumber`).

## Structure

```
index.html               Home
about.html                About
engineering.html          Engineering admissions (JEE / COMEDK / MHT-CET)
management.html           Management admissions (CAT / CMAT / MAT / MAH-CET)
medical.html               Medical / NEET counselling guidance
study-abroad.html         Study Abroad admissions (UK / Europe / Commonwealth / Asia — 14 countries)
distance-education.html  Distance, Online & Open Schooling guidance
college-predictor.html    Free college predictor tool
colleges.html              College Directory (filterable, 343 institutions)
blog.html                  Blog index (5 articles, one per vertical)
blog-*.html                 Individual blog articles (flat filenames, no subdirectory — keeps the shared header/footer/asset relative paths unchanged)
faq.html                    FAQ
contact.html               Contact
privacy-policy.html       Privacy Policy
terms.html                  Terms & Disclaimer
404.html                    Custom 404 page

css/style.css              Design system + all site styles
js/main.js                  Mobile nav, enquiry modal (Apps Script submit), predictor logic, directory filter
data/colleges.json         College Directory data (see "College Directory" section below)
assets/                     Favicon, apple-touch-icon, OG/Twitter card image
robots.txt, sitemap.xml    SEO basics
dev/                        Generator scripts (not part of the deployed site — see "Generator scripts" below)
```

## Generator scripts

Everything under `dev/` is a local tool for maintaining the site — none of it is linked from or served by any page, and GitHub Pages ignores it.

- **`dev/build.py`** generates all `.html` pages from the shared `page()`/`header()`/`footer()` templates and the content defined inline in the script. Run `python3 dev/build.py` after any content or structural change, then commit the regenerated `.html` files alongside your change to `build.py` itself. Needs `dev/icons.py` (a sibling import) and `openpyxl` only if you also regenerate the College Directory data in the same session. `ASSET_VERSION` near the top cache-busts `css/style.css` and `js/main.js` — bump it whenever either file's content changes, then re-run the script so all 15 pages pick up the new version string.
- **`dev/icons.py`** is the hand-authored inline-SVG icon set (`ICON_CAP`, `ICON_GLOBE`, etc.) that `build.py` imports — no external icon library.
- **`dev/build_colleges_json.py`** regenerates `data/colleges.json` from a Master Database spreadsheet export: `python3 dev/build_colleges_json.py /path/to/Master_Database.xlsx`. See the "College Directory" section above for what it does and doesn't infer.

These three files are committed specifically so a fresh contributor (human or AI) can maintain the site without first having to reverse-engineer its structure from the rendered HTML, or without access to a prior session's local files that were never checked in.

## Notes

- The College Predictor only gives route guidance for Engineering/Management in Karnataka and Maharashtra, per the product's current verified data. Every other combination (including Medical anywhere, and Study Abroad) is intentionally routed to "a counsellor will personally review your profile" — this is deliberate, not a gap to fill in with a fake match.
- Canonical URLs, Open Graph tags, and `sitemap.xml` currently point at `https://degreelelo-ux.github.io/degreelelo` (the default GitHub Pages URL for this repo). If you attach a custom domain, update those in bulk (they're the `SITE_URL` constant equivalent — a simple find-and-replace across the HTML files, `robots.txt`, and `sitemap.xml`).
- No JS framework, no build step at deploy time. Pages are static HTML; the shared header/footer/modal markup is duplicated per page by design, kept in sync via `dev/build.py` (not part of the deployed site — see "Generator scripts" below).
- The About page's "What We Help With" section lists DegreeLelo's services (counselling, admissions guidance, test prep, scholarships, visa/documentation support, etc.) in the site's own voice, including foreign-admission-adjacent services (foreign university admissions, student visa & documentation) that `study-abroad.html` now explains in more detail.
- **`css/style.css` and `js/main.js` are referenced with a `?v=N` query string** (e.g. `js/main.js?v=2`) on every page, identical across all 15. This is deliberate cache-busting — GitHub Pages' CDN and browsers can hold onto an old copy of these files for a while, which previously caused a live page to keep running stale JS after a deploy (a form submit silently misbehaved because the HTML had updated but the JS hadn't). **Whenever you edit either file, bump the `v=` number on all 15 pages** (a single find-and-replace) so every visitor is guaranteed to fetch the new version rather than a cached one.
