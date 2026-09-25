# DegreeLelo

Lead-generation website for DegreeLelo, an Indian education admission consultancy covering Engineering, Management, Medical, and Study Abroad guidance.

Plain HTML/CSS/JS, no build step, no framework. Deployable as-is on GitHub Pages.

## How the enquiry form works

The enquiry popup (present on every page) is a custom-styled modal that submits into a Google Form in the background, via a hidden iframe (`target="hidden_iframe"` on the `<form>`) — the page never navigates to Google, and the modal's own "Thank you" state is what the visitor sees. Submissions land in the Google Form's linked Sheet.

Each field's `name` attribute is the target Google Form question's `entry.XXXXXXX` ID:

| Modal field | Entry ID |
|---|---|
| Full name | `entry.207722185` |
| Phone number | `entry.804843000` |
| Email address | `entry.15042384` |
| City | `entry.287878406` |
| Course of interest | `entry.922132532` |
| Score / percentile | `entry.1558959334` |
| How did you hear about us | `entry.1372671113` |

The submission endpoint (`js/main.js`-adjacent, in the `<form action>` in every page's modal markup) is `https://docs.google.com/forms/d/e/1FAIpQLSelDjmk3jOax0goum4VtmfoOLKHkvRg6YCxsT3EpRQMIWjfOA/formResponse`.

**Caveats worth knowing (the important one is the second bullet — tested, not theoretical):**
- This is the standard "hidden iframe POST to `/formResponse`" technique for submitting to a Google Form without the visible Google UI. It isn't an officially documented API — it works today and is widely used, but isn't guaranteed never to change.
- **The iframe's `load` event fires on essentially any outcome — success, a Google-side validation rejection, or even a failed network request** — because a failed navigation still renders *something* (an error page), and that still counts as "loaded." This was confirmed directly: in an environment where the request couldn't reach Google at all, the modal still showed "Thank you." Practically, this means the 8-second timeout fallback (which shows an error/WhatsApp prompt) only catches a request that never resolves *at all* — it cannot tell a saved submission apart from a rejected or failed one. There is no reliable client-side way to detect a Google-side rejection with this technique.
- **This makes it essential to double-check the Google Form's own required-field settings match this modal**: Name, Phone, Email, City, and Course of Interest are required here; Score/Percentile and "How did you hear about us" are optional. If the Form marks something required that this modal doesn't collect as required, Google will reject the submission server-side and the visitor will still see "Thank you," with no way for the site (or the visitor) to know the lead was lost.
- If "Course of Interest" or "How did you hear about us" are dropdown/multiple-choice questions in the Form (not short answer), their defined choices must exactly match the option text this modal sends: `Engineering` / `Management` / `Medical` / `Study Abroad`, and `Instagram` / `WhatsApp` / `Google Search` / `Friend / Family Referral` / `School / College` / `Other`, respectively.
- **Recommended before trusting this live**: submit the popup form yourself once the site is live and confirm the row actually appears in the linked Sheet — don't rely on the on-screen "Thank you" as proof it worked.

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
js/main.js                  Mobile nav, enquiry modal (Google Form submit), predictor logic
assets/                     Favicon, apple-touch-icon, OG/Twitter card image
robots.txt, sitemap.xml    SEO basics
```

## Notes

- The College Predictor only gives route guidance for Engineering/Management in Karnataka and Maharashtra, per the product's current verified data. Every other combination (including Medical anywhere, and Study Abroad) is intentionally routed to "a counsellor will personally review your profile" — this is deliberate, not a gap to fill in with a fake match.
- Canonical URLs, Open Graph tags, and `sitemap.xml` currently point at `https://degreelelo-ux.github.io/degreelelo` (the default GitHub Pages URL for this repo). If you attach a custom domain, update those in bulk (they're the `SITE_URL` constant equivalent — a simple find-and-replace across the HTML files, `robots.txt`, and `sitemap.xml`).
- No JS framework, no build step. Pages are static HTML; the shared header/footer/modal markup is duplicated per page by design (kept in sync via a local generation script during development, not part of the deployed site).
