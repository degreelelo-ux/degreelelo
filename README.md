# DegreeLelo

Lead-generation website for DegreeLelo, an Indian education admission consultancy covering Engineering, Management, Medical, and Study Abroad guidance.

Plain HTML/CSS/JS, no build step, no framework. Deployable as-is on GitHub Pages.

## Before going live

Two things are stubbed with placeholders and must be filled in before this site collects real leads:

1. **Formspree form ID** — the enquiry popup (present on every page) posts to Formspree so submissions land in an inbox with no backend.
   - Create a form at [formspree.io](https://formspree.io) pointed at `degreelelo@gmail.com`.
   - Open `js/main.js` and replace `YOUR_FORMSPREE_ID` in `DEGREELELO_CONFIG.formspreeFormId` with your real form ID (the part after `/f/` in your Formspree endpoint).

2. **WhatsApp Business number** — the "Chat with us on WhatsApp" button on the Contact page.
   - Open `js/main.js` and replace `911234567890` in `DEGREELELO_CONFIG.whatsappNumber` with your real number in international format, digits only (no `+`, spaces, or dashes).

Both are declared at the top of `js/main.js` and nowhere else, so there's one place to edit.

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
js/main.js                  Mobile nav, enquiry modal, Formspree submit, predictor logic
assets/                     Favicon, apple-touch-icon, OG/Twitter card image
robots.txt, sitemap.xml    SEO basics
```

## Notes

- The College Predictor only gives route guidance for Engineering/Management in Karnataka and Maharashtra, per the product's current verified data. Every other combination (including Medical anywhere, and Study Abroad) is intentionally routed to "a counsellor will personally review your profile" — this is deliberate, not a gap to fill in with a fake match.
- Canonical URLs, Open Graph tags, and `sitemap.xml` currently point at `https://degreelelo-ux.github.io/degreelelo` (the default GitHub Pages URL for this repo). If you attach a custom domain, update those in bulk (they're the `SITE_URL` constant equivalent — a simple find-and-replace across the HTML files, `robots.txt`, and `sitemap.xml`).
- No JS framework, no build step. Pages are static HTML; the shared header/footer/modal markup is duplicated per page by design (kept in sync via a local generation script during development, not part of the deployed site).
