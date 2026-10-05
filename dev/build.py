"""Static site generator for DegreeLelo.

NOT part of the deployed site and NOT run automatically — GitHub Pages
serves the committed .html files directly. Run this manually after any
content/structure change, then commit the regenerated .html files:

    python3 dev/build.py

Requires dev/icons.py (sibling import) and, for the College Directory
page, data/colleges.json (see dev/build_colleges_json.py to regenerate
that from the source spreadsheet).
"""
import os
import sys
import json
from string import Template

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icons import *  # noqa

SITE_URL = "https://degreelelo-ux.github.io/degreelelo"
# Repo root — this script lives at <repo_root>/dev/build.py, and writes
# pages into the repo root itself (where GitHub Pages serves them from).
OUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Bump this on every css/style.css or js/main.js content change so browsers
# and the GitHub Pages CDN are forced to fetch the new file instead of
# serving a stale cached copy.
ASSET_VERSION = "5"

# --------------------------------------------------------------------------
# Shared fragments
# --------------------------------------------------------------------------

HEAD_TMPL = Template("""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title</title>
<meta name="description" content="$description">
<link rel="canonical" href="$canonical">
<meta name="robots" content="$robots">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:title" content="$og_title">
<meta property="og:description" content="$og_description">
<meta property="og:url" content="$canonical">
<meta property="og:image" content="$SITE_URL/assets/og-image.png">
<meta property="og:site_name" content="DegreeLelo">
<meta property="og:locale" content="en_IN">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="$og_title">
<meta name="twitter:description" content="$og_description">
<meta name="twitter:image" content="$SITE_URL/assets/og-image.png">

<link rel="icon" href="assets/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css?v=$ASSET_VERSION">
$extra_head
</head>
""")

def whatsapp_href_placeholder():
    return "#"

def head(title, description, path, og_title=None, og_description=None, extra_head="", robots="index, follow"):
    canonical = f"{SITE_URL}{path}"
    return HEAD_TMPL.substitute(
        title=title,
        description=description,
        canonical=canonical,
        og_title=og_title or title,
        og_description=og_description or description,
        extra_head=extra_head,
        robots=robots,
        SITE_URL=SITE_URL,
        ASSET_VERSION=ASSET_VERSION,
    )

def nav_link(label, href, active_key, key):
    current = ' aria-current="page"' if active_key == key else ""
    return f'<li><a href="{href}"{current}>{label}</a></li>'

# Compass Pin mark: a location pin with a graduation cap where the lens
# would be — "the right place of learning, located." Two colorways matching
# the header-on-white and footer-on-dark contexts (the footer has always
# swapped the brand mark's background to accent/amber; this keeps that).
BRAND_MARK_HEADER = """<svg class="brand-mark" aria-hidden="true" width="38" height="38" viewBox="0 0 100 100">
        <rect width="100" height="100" rx="22" fill="#1E3A8A"/>
        <path d="M50 20 C 64 20 74 30 74 43 C 74 60 50 82 50 82 C 50 82 26 60 26 43 C 26 30 36 20 50 20 Z" fill="#FFFFFF"/>
        <path d="M50 35 L66 43 L50 51 L34 43 Z" fill="#F59E0B"/>
        <line x1="64" y1="44" x2="64" y2="52" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="64" cy="54" r="2.2" fill="#F59E0B"/>
      </svg>"""

BRAND_MARK_FOOTER = """<svg class="brand-mark" aria-hidden="true" width="38" height="38" viewBox="0 0 100 100">
          <rect width="100" height="100" rx="22" fill="#F59E0B"/>
          <path d="M50 20 C 64 20 74 30 74 43 C 74 60 50 82 50 82 C 50 82 26 60 26 43 C 26 30 36 20 50 20 Z" fill="#14275c"/>
          <path d="M50 35 L66 43 L50 51 L34 43 Z" fill="#FFFFFF"/>
          <line x1="64" y1="44" x2="64" y2="52" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
          <circle cx="64" cy="54" r="2.2" fill="#FFFFFF"/>
        </svg>"""

def header(active):
    dropdown_current = ' aria-current="page"' if active in ("engineering", "management", "medical", "study-abroad", "distance-education") else ""
    return f"""<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="container nav-bar">
    <a href="index.html" class="brand" aria-label="DegreeLelo home">
      {BRAND_MARK_HEADER}
      <span class="brand-name-full">DegreeLelo</span>
    </a>

    <button type="button" class="nav-toggle" data-nav-toggle aria-expanded="false" aria-controls="primary-nav" aria-label="Toggle navigation menu">
      {ICON_MENU}
      {ICON_CLOSE}
    </button>

    <nav class="primary-nav" id="primary-nav" data-primary-nav aria-label="Primary">
      <ul class="nav-links">
        {nav_link("Home", "index.html", active, "home")}
        <li>
          <details class="nav-dropdown">
            <summary{dropdown_current}>Programs</summary>
            <div class="nav-dropdown-menu">
              <a href="engineering.html">Engineering</a>
              <a href="management.html">Management</a>
              <a href="medical.html">Medical</a>
              <a href="study-abroad.html">Study Abroad</a>
              <a href="distance-education.html">Distance &amp; Open Education</a>
            </div>
          </details>
        </li>
        {nav_link("College Predictor", "college-predictor.html", active, "predictor")}
        {nav_link("Colleges", "colleges.html", active, "colleges")}
        {nav_link("About", "about.html", active, "about")}
        {nav_link("Blog", "blog.html", active, "blog")}
        {nav_link("FAQ", "faq.html", active, "faq")}
        {nav_link("Contact", "contact.html", active, "contact")}
      </ul>
      <div class="nav-cta">
        <button type="button" class="btn btn-primary" data-modal-trigger>Enquire Now</button>
      </div>
    </nav>
  </div>
</header>
"""

def footer():
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col">
        <div class="footer-brand">
          {BRAND_MARK_FOOTER}
          <span class="footer-brand-name">DegreeLelo</span>
        </div>
        <p>Find the Right College, Not Just Any College. Honest admission guidance for Engineering, Management, Medical, and Study Abroad programs.</p>
        <p style="margin-top:1rem;">
          <a href="mailto:degreelelo@gmail.com" class="text-link" style="color:#C7D2EF; text-decoration-color:#4C5C93;">degreelelo@gmail.com</a>
        </p>
        <div class="footer-social">
          <a href="https://www.linkedin.com/in/degreelelo/" target="_blank" rel="noopener noreferrer" aria-label="DegreeLelo on LinkedIn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="3" width="18" height="18" rx="3"/><line x1="7.5" y1="10" x2="7.5" y2="17"/><circle cx="7.5" cy="6.7" r="0.9" fill="currentColor" stroke="none"/><line x1="11.5" y1="10" x2="11.5" y2="17"/><path d="M11.5 13.2c0-1.8 1.1-3 2.5-3s2.5 1.2 2.5 3V17"/></svg>
          </a>
          <a href="https://www.instagram.com/degreelelo/" target="_blank" rel="noopener noreferrer" aria-label="DegreeLelo on Instagram">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="16.6" cy="7.4" r="0.9" fill="currentColor" stroke="none"/></svg>
          </a>
          <a href="https://x.com/DegreeLelo" target="_blank" rel="noopener noreferrer" aria-label="DegreeLelo on X">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" focusable="false"><line x1="4.5" y1="4.5" x2="19.5" y2="19.5"/><line x1="19.5" y1="4.5" x2="4.5" y2="19.5"/></svg>
          </a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Programs</h4>
        <ul>
          <li><a href="engineering.html">Engineering</a></li>
          <li><a href="management.html">Management</a></li>
          <li><a href="medical.html">Medical</a></li>
          <li><a href="study-abroad.html">Study Abroad</a></li>
          <li><a href="distance-education.html">Distance &amp; Open Education</a></li>
          <li><a href="college-predictor.html">College Predictor</a></li>
          <li><a href="colleges.html">College Directory</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About</a></li>
          <li><a href="blog.html">Blog</a></li>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <ul>
          <li><a href="privacy-policy.html">Privacy Policy</a></li>
          <li><a href="terms.html">Terms &amp; Disclaimer</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> DegreeLelo. All rights reserved.</p>
      <div class="footer-legal">
        <a href="privacy-policy.html">Privacy Policy</a>
        <a href="terms.html">Terms &amp; Disclaimer</a>
      </div>
    </div>
  </div>
</footer>
"""

MODAL = f"""<div class="modal-overlay" id="enquiry-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" hidden>
  <div class="modal">
    <button type="button" class="modal-close" data-modal-close aria-label="Close enquiry form">
      {ICON_CLOSE_PLAIN}
    </button>
    <h2 id="modal-title">Free College Assessment</h2>
    <p class="lede-sm">Share a few details and a DegreeLelo counsellor will get in touch. No spam, ever.</p>

    <div class="form-status" data-form-status hidden></div>

    <form action="https://script.google.com/macros/s/AKfycbw0VbFqKKRZM7UBFx3DDR-11UU6cioS4jWPLb7XWKcc7O0TZ_B11D2T6no9HRSJFIPQWw/exec" method="POST">
      <div class="field">
        <label for="enq-name">Full name</label>
        <input type="text" id="enq-name" name="entry.207722185" autocomplete="name" required>
      </div>
      <div class="field-row field-row-2">
        <div class="field">
          <label for="enq-phone">Phone number</label>
          <input type="tel" id="enq-phone" name="entry.804843000" autocomplete="tel" inputmode="tel" required>
        </div>
        <div class="field">
          <label for="enq-email">Email address</label>
          <input type="email" id="enq-email" name="entry.15042384" autocomplete="email" required>
        </div>
      </div>
      <div class="field-row field-row-2">
        <div class="field">
          <label for="enq-city">City</label>
          <input type="text" id="enq-city" name="entry.287878406" autocomplete="address-level2" required>
        </div>
        <div class="field">
          <label for="enq-course">Course of interest</label>
          <select id="enq-course" name="entry.922132532" required>
            <option value="">Select one</option>
            <option value="Engineering">Engineering</option>
            <option value="Management">Management</option>
            <option value="Medical">Medical</option>
            <option value="Study Abroad">Study Abroad</option>
            <option value="Distance & Open Education">Distance &amp; Open Education</option>
          </select>
        </div>
      </div>
      <div class="field-row field-row-2">
        <div class="field">
          <label for="enq-score">Score / percentile <span class="hint">(if known)</span></label>
          <input type="text" id="enq-score" name="entry.1558959334" placeholder="e.g. 92.4 percentile">
        </div>
        <div class="field">
          <label for="enq-source">How did you hear about us?</label>
          <select id="enq-source" name="entry.1372671113">
            <option value="">Select one</option>
            <option value="Instagram">Instagram</option>
            <option value="WhatsApp">WhatsApp</option>
            <option value="Google Search">Google Search</option>
            <option value="Friend / Family Referral">Friend / Family Referral</option>
            <option value="School / College">School / College</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>
      <button type="submit" class="btn btn-primary btn-block btn-lg">Submit Enquiry</button>
    </form>

    <div class="modal-success" data-form-success hidden>
      {ICON_CHECK_CIRCLE}
      <h3>Thank you — we've got it!</h3>
      <p>A DegreeLelo counsellor will reach out to you shortly. You can also message us directly on WhatsApp for a faster response.</p>
    </div>
  </div>
</div>
"""

SCRIPTS = f'<script src="js/main.js?v={ASSET_VERSION}"></script>'

def page(slug, title, description, active, main_html, og_title=None, og_description=None, extra_head="", robots="index, follow"):
    path = "/" if slug == "index" else f"/{slug}.html"
    html = head(title, description, path, og_title, og_description, extra_head, robots)
    html += "<body>\n"
    html += header(active)
    html += f'<main id="main">\n{main_html}\n</main>\n'
    html += footer()
    html += MODAL
    html += SCRIPTS + "\n</body>\n</html>\n"
    return html

def write(slug, content):
    fname = "index.html" if slug == "index" else f"{slug}.html"
    with open(os.path.join(OUT_DIR, fname), "w") as f:
        f.write(content)
    print("wrote", fname)

# --------------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------------

HOME_SCHEMA = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "DegreeLelo",
  "url": "https://degreelelo-ux.github.io/degreelelo/",
  "description": "DegreeLelo is an Indian admission counselling service helping students and parents navigate Engineering, Management, Medical, and Study Abroad admissions with honest, personalised guidance.",
  "slogan": "Find the Right College, Not Just Any College.",
  "email": "degreelelo@gmail.com",
  "areaServed": "IN",
  "sameAs": []
}
</script>"""

home_main = f"""
<section class="hero">
  <div class="container hero-inner">
    <span class="eyebrow">Admission Guidance, Done Honestly</span>
    <h1>Find the Right College, Not Just Any College.</h1>
    <p class="lede">DegreeLelo helps Indian students and parents make sense of Engineering, Management, Medical, and Study Abroad admissions &mdash; with plain-language guidance on eligibility, exams, and realistic pathways.</p>
    <div class="cta-row">
      <a href="college-predictor.html" class="btn btn-primary btn-lg">Check Your College Options</a>
    </div>
    <ul class="hero-trust">
      <li>{ICON_CHECK} Personalised guidance, not mass advice</li>
      <li>{ICON_CHECK} We never guarantee admission or bypass eligibility rules</li>
      <li>{ICON_CHECK} Engineering &middot; Management &middot; Medical &middot; Study Abroad</li>
    </ul>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">How It Works</span>
      <h2>Four steps to a realistic shortlist</h2>
      <p class="lede">No jargon, no guesswork &mdash; just a clear process from where you are today to a college that actually fits.</p>
    </div>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <h3>Profile Analysis</h3>
        <p>We understand your academics, exam scores, budget, and preferences in detail.</p>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <h3>Eligibility Check</h3>
        <p>We map your profile against real exam and counselling requirements &mdash; no assumptions.</p>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <h3>College Shortlist</h3>
        <p>You get an honest, realistic shortlist based on your actual eligibility.</p>
      </div>
      <div class="step">
        <div class="step-num">4</div>
        <h3>Admission Execution</h3>
        <p>We guide you through forms, counselling rounds, and documentation, step by step.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Programs We Guide</span>
      <h2>Guidance across four admission paths</h2>
    </div>
    <div class="grid grid-4">
      <article class="card">
        <div class="card-icon">{ICON_CAP}</div>
        <h3>Engineering</h3>
        <p>JEE, COMEDK, and MHT-CET pathways explained in plain language.</p>
        <a href="engineering.html" class="card-link">Explore Engineering {ICON_CHEVRON_RIGHT}</a>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_BRIEFCASE}</div>
        <h3>Management</h3>
        <p>CAT, CMAT, MAT, and MAH-CET routes to management colleges.</p>
        <a href="management.html" class="card-link">Explore Management {ICON_CHEVRON_RIGHT}</a>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_MEDICAL}</div>
        <h3>Medical</h3>
        <p>NEET counselling guidance, explained honestly &mdash; no guarantees, just clarity.</p>
        <a href="medical.html" class="card-link">Explore Medical {ICON_CHEVRON_RIGHT}</a>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_GLOBE}</div>
        <h3>Study Abroad</h3>
        <p>USA, UK, Canada, Australia &amp; Germany &mdash; application systems, tests, and visas explained plainly.</p>
        <a href="study-abroad.html" class="card-link">Explore Study Abroad {ICON_CHEVRON_RIGHT}</a>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container text-center">
    <h2>Ready to see where you stand?</h2>
    <p class="lede" style="margin-inline:auto; max-width:560px;">Use our free College Predictor to get an honest first read on your options &mdash; it takes less than a minute.</p>
    <div class="cta-row" style="justify-content:center; margin-top:1.5rem;">
      <a href="college-predictor.html" class="btn btn-primary btn-lg">Check Your College Options</a>
    </div>
  </div>
</section>
"""

write("index", page(
    "index",
    "DegreeLelo — Find the Right College, Not Just Any College",
    "DegreeLelo helps Indian students and parents navigate Engineering, Management, Medical, and Study Abroad admissions with honest, personalised counselling. Check your college options today.",
    "home",
    home_main,
    extra_head=HOME_SCHEMA,
))

# --------------------------------------------------------------------------
# ABOUT
# --------------------------------------------------------------------------

about_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">About DegreeLelo</span>
    <h1>Honest guidance, built for Indian families</h1>
    <p class="lede">We started DegreeLelo because too many students sign up with agents who promise guaranteed seats &mdash; and too many families only find out later that isn't how admissions work.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="grid grid-2" style="align-items:start;">
      <div class="prose">
        <h2>Why we started DegreeLelo</h2>
        <p>Every year, thousands of students across India choose a college in a rush &mdash; often based on incomplete information, pressure from agents, or advice that sounds confident but isn't grounded in how admission and counselling processes actually work.</p>
        <p>DegreeLelo was built to close that gap. Instead of pushing students toward whichever college pays the highest commission, we start with the student's actual profile &mdash; their scores, their exam results, their budget, their goals &mdash; and work backward to routes that are genuinely open to them.</p>
        <h2>Our brand promise</h2>
        <ul>
          <li>We explain the &ldquo;why&rdquo; behind every recommendation, not just the &ldquo;what&rdquo;.</li>
          <li>We never claim to guarantee admission or bypass eligibility rules.</li>
          <li>We only point families toward exam and counselling routes that genuinely apply to their profile.</li>
          <li>The final decision always stays with the student and their family &mdash; we advise, we don't decide for you.</li>
        </ul>
      </div>
      <div class="prose">
        <h2>What you can expect from us</h2>
        <div class="stack">
          <div class="notice notice-success">
            {ICON_CHECK_CIRCLE}
            <div>
              <strong>Transparent process</strong>
              <p>Every recommendation is explained in plain language, with the reasoning behind it.</p>
            </div>
          </div>
          <div class="notice notice-info">
            {ICON_SHIELD}
            <div>
              <strong>No false guarantees</strong>
              <p>We will never tell you a seat is guaranteed or that eligibility rules can be bypassed.</p>
            </div>
          </div>
          <div class="notice">
            {ICON_INFO}
            <div>
              <strong>Privacy respected</strong>
              <p>Your academic and personal details are used only to guide your admission &mdash; see our <a href="privacy-policy.html" class="text-link">Privacy Policy</a>.</p>
            </div>
          </div>
        </div>
        <div class="cta-row mt-6">
          <button type="button" class="btn btn-primary btn-lg" data-modal-trigger>Free College Assessment</button>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">What We Help With</span>
      <h2>One counsellor, every step of the process</h2>
      <p class="lede">From choosing a stream to accepting a seat, our counsellors stay involved across all of it &mdash; not just the one exam you happen to be prepping for right now.</p>
    </div>
    <div class="grid grid-3">
      <article class="card">
        <div class="card-icon">{ICON_CHAT}</div>
        <h3>Career Counselling &amp; Stream Selection</h3>
        <p>One-on-one conversations to help you and your family choose a stream based on your interests and strengths &mdash; not guesswork or peer pressure.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_CHECK_CIRCLE}</div>
        <h3>Aptitude Assessment</h3>
        <p>Structured assessments that surface where you're naturally strong, so stream and course decisions rest on evidence rather than assumption.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_CAP}</div>
        <h3>Indian College Admissions</h3>
        <p>Guidance across IITs, NITs, IIMs, AIIMS, and state universities &mdash; how each admission and counselling process actually works, and what's realistically open to your profile.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_GLOBE}</div>
        <h3>Foreign University Admissions</h3>
        <p>Support exploring universities in the USA, UK, Canada, Australia, and Germany, including how each country's application process and requirements differ.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_SHIELD}</div>
        <h3>Scholarship Identification &amp; Support</h3>
        <p>We help you find scholarships you may genuinely qualify for, and walk you through what each application actually requires.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_BRIEFCASE}</div>
        <h3>Student Visa &amp; Documentation</h3>
        <p>Help understanding visa requirements and getting your documentation in order for the country and programme you're applying to.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_INFO}</div>
        <h3>Test Preparation Guidance</h3>
        <p>Direction on what to prepare for and when, across JEE, NEET, CUET, SAT, IELTS, TOEFL, GRE, and GMAT &mdash; the right resources and timeline, not generic advice.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_ARROW_RIGHT}</div>
        <h3>End-to-End Admission Support</h3>
        <p>From your first shortlist to the day you accept a seat, we stay involved through forms, counselling rounds, and documentation deadlines.</p>
      </article>
      <article class="card">
        <div class="card-icon">{ICON_MAIL}</div>
        <h3>Free Initial Counselling Session</h3>
        <p>Your first conversation with a DegreeLelo counsellor costs nothing &mdash; it's how we understand your profile before recommending anything.</p>
      </article>
    </div>
    <div class="cta-row mt-8" style="justify-content:center;">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger>Book Your Free Session</button>
    </div>
  </div>
</section>
"""

write("about", page(
    "about",
    "About DegreeLelo — Honest Admission Guidance for Indian Students",
    "Learn about DegreeLelo's mission to give Indian students and parents honest, personalised admission guidance across Engineering, Management, Medical, and Study Abroad programs.",
    "about",
    about_main,
))

# --------------------------------------------------------------------------
# ENGINEERING
# --------------------------------------------------------------------------

engineering_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Engineering Admissions</span>
    <h1>B.Tech Admission Guidance: JEE, COMEDK &amp; MHT-CET</h1>
    <p class="lede">Engineering admission in India runs through several parallel exam systems. Here's what each one means for you, in plain language.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="section-head">
      <h2>Understanding your pathways</h2>
      <p>Which exam matters most for you depends on your state, your target colleges, and your exam scores. We help you understand all three before you commit time and money anywhere.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">JEE Main &amp; Advanced</span>
      <h3>The national route</h3>
      <p>JEE Main is the entry point for NITs, IIITs, and other centrally-funded technical institutes, and also qualifies top scorers for JEE Advanced &mdash; the exam for admission to the IITs. Seats are allotted through centralised counselling (JoSAA/CSAB).</p>
      <ul>
        <li>Best suited if you're aiming for NITs, IIITs, GFTIs, or IITs.</li>
        <li>Counselling is rank-based and happens over multiple rounds.</li>
        <li>We help you understand realistic rank bands and how choice-filling actually works.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">COMEDK</span>
      <h3>Karnataka's private engineering route</h3>
      <p>COMEDK UGET is the common entrance test for admission to private engineering colleges across Karnataka. It's a strong option if your JEE rank doesn't open the doors you want, but you're specifically interested in Karnataka.</p>
      <ul>
        <li>Open to students from any state, not just Karnataka residents.</li>
        <li>Separate application and counselling process from JEE/JoSAA.</li>
        <li>We help you understand which colleges and branches are realistically within reach.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">MHT-CET</span>
      <h3>Maharashtra's state entrance exam</h3>
      <p>MHT-CET is the state-level exam used for admission to engineering (and pharmacy) colleges across Maharashtra, conducted by the state CET cell. It runs alongside JEE for students focused on Maharashtra institutions.</p>
      <ul>
        <li>Relevant mainly for Maharashtra-based colleges and, in many cases, domicile-linked quotas.</li>
        <li>Counselling and seat allotment are handled by the Maharashtra state CET cell.</li>
        <li>We help you understand category, quota, and home-university considerations specific to Maharashtra.</li>
      </ul>
    </div>

    <p class="mt-8"><a href="colleges.html?category=Engineering" class="text-link">Browse Engineering colleges in our directory &rarr;</a></p>

    <div class="cta-row mt-6">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger data-prefill-course="Engineering">Check Your College Options</button>
    </div>
  </div>
</section>
"""

write("engineering", page(
    "engineering",
    "B.Tech Admission Through JEE, COMEDK & MHT-CET | DegreeLelo",
    "Understand B.Tech admission through JEE Main/Advanced, COMEDK, and MHT-CET. Plain-language guidance on engineering entrance exam pathways from DegreeLelo.",
    "engineering",
    engineering_main,
))

# --------------------------------------------------------------------------
# MANAGEMENT
# --------------------------------------------------------------------------

management_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Management Admissions</span>
    <h1>MBA Admission Guidance: CAT, CMAT, MAT &amp; MAH-CET</h1>
    <p class="lede">Management admissions in India run through several exams, each opening different sets of colleges. Here's how they compare.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="section-head">
      <h2>Understanding your pathways</h2>
      <p>Your ideal exam depends on your target colleges, your timeline, and how your profile fits each exam's pattern. We walk you through the realistic options.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">CAT</span>
      <h3>The national benchmark exam</h3>
      <p>CAT (Common Admission Test) is the most widely recognised management entrance exam in India, used by the IIMs and a large number of other CAT-accepting B-schools.</p>
      <ul>
        <li>Best suited if you're aiming for IIMs or top CAT-accepting institutes.</li>
        <li>Selection typically involves the exam score plus academic profile, work experience, and interview rounds.</li>
        <li>We help you build a realistic list of CAT-accepting colleges based on your expected score band.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">CMAT</span>
      <h3>A widely accepted alternative</h3>
      <p>CMAT (Common Management Admission Test), conducted by NTA, is accepted by a large number of government and private B-schools, including several institutes in Karnataka and Maharashtra.</p>
      <ul>
        <li>Good option if you want broad acceptance without narrowing to only the top-tier institutes.</li>
        <li>We map your CMAT score against colleges genuinely open to that score range.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">MAT</span>
      <h3>Flexible, multiple-session exam</h3>
      <p>MAT is conducted in multiple sessions through the year and is accepted by a wide network of private B-schools, giving you more than one attempt to improve your score.</p>
      <ul>
        <li>Useful if you want flexibility in timing your best attempt.</li>
        <li>We help you understand which of your target colleges actually accept MAT scores.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">MAH-CET</span>
      <h3>Maharashtra's state management exam</h3>
      <p>MAH-CET (for MBA/MMS) is the state-level exam used for admission to management colleges across Maharashtra, with counselling conducted by the state CET cell.</p>
      <ul>
        <li>Relevant mainly if you're targeting Maharashtra state colleges.</li>
        <li>Domicile and category rules affect seat allocation &mdash; we help you understand where you stand.</li>
      </ul>
    </div>

    <p class="mt-8"><a href="colleges.html?category=Management" class="text-link">Browse Management colleges in our directory &rarr;</a></p>

    <div class="cta-row mt-6">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger data-prefill-course="Management">Check Your College Options</button>
    </div>
  </div>
</section>
"""

write("management", page(
    "management",
    "MBA Colleges Accepting CMAT, CAT, MAT & MAH-CET | DegreeLelo",
    "Explore MBA admission pathways through CAT, CMAT, MAT, and MAH-CET. Honest, plain-language guidance on management entrance exams from DegreeLelo.",
    "management",
    management_main,
))

# --------------------------------------------------------------------------
# MEDICAL
# --------------------------------------------------------------------------

medical_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Medical Admissions</span>
    <h1>NEET Counselling Guidance for MBBS Admission</h1>
    <p class="lede">NEET-UG is the single mandatory entrance exam for MBBS and BDS admission across India. The counselling process that follows it is where most students and parents need the most support.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="notice" style="margin-bottom:2rem;">
      {ICON_INFO}
      <div>
        <strong>Important note</strong>
        <p>We do not guarantee admission or bypass eligibility rules. Our counsellors review your NEET score and category personally before giving any guidance &mdash; we don't auto-generate matches.</p>
      </div>
    </div>

    <div class="section-head">
      <h2>How NEET counselling works</h2>
      <p>Once NEET-UG results are declared, admission happens through a structured counselling process &mdash; not a direct application to a college.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">All India Quota (AIQ)</span>
      <h3>15% of seats, open nationwide</h3>
      <p>A portion of seats in government medical colleges is reserved under the All India Quota and counselled centrally, open to candidates from any state.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">State Quota</span>
      <h3>Counselled by your home state authority</h3>
      <p>The remaining government seats, along with private and deemed university seats in many states, are counselled by the respective state authority, usually with domicile requirements.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Counselling Rounds</span>
      <h3>Multiple rounds, real deadlines</h3>
      <p>Counselling typically runs across Round 1, Round 2, a mop-up round, and sometimes a stray vacancy round &mdash; each with its own choice-filling window, document verification step, and seat acceptance deadline.</p>
      <ul>
        <li>Missing a document deadline can cost you a round entirely &mdash; we help you track every date.</li>
        <li>Choice-filling strategy affects your outcome as much as your score does.</li>
        <li>We explain what documents you'll need and when, so nothing is a last-minute scramble.</li>
      </ul>
    </div>

    <p class="mt-8"><a href="colleges.html?category=Medical" class="text-link">Browse Medical colleges in our directory &rarr;</a></p>

    <div class="cta-row mt-6">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger data-prefill-course="Medical">Check Your College Options</button>
    </div>
  </div>
</section>
"""

write("medical", page(
    "medical",
    "NEET Counselling Guidance for MBBS Admission | DegreeLelo",
    "Get plain-language guidance on NEET counselling, MBBS admission rounds, and eligibility. DegreeLelo does not guarantee admission or bypass eligibility rules.",
    "medical",
    medical_main,
))

# --------------------------------------------------------------------------
# STUDY ABROAD
# --------------------------------------------------------------------------

study_abroad_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Study Abroad</span>
    <h1>Studying Abroad: USA, UK, Canada, Australia &amp; Germany</h1>
    <p class="lede">Admission abroad runs through a different system in every country &mdash; different tests, different application platforms, different deadlines. Here's what each one actually involves, before you commit time or money to any of them.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="notice" style="margin-bottom:2rem;">
      {ICON_INFO}
      <div>
        <strong>Important note</strong>
        <p>We don't yet carry verified, institution-specific listings for Study Abroad in our College Directory, the way we do for Engineering, Management, and Medical. Requirements below differ by country and change often, so a counsellor reviews your profile personally rather than us auto-generating a college list. We never guarantee admission or bypass a university's own eligibility and visa rules.</p>
      </div>
    </div>

    <div class="section-head">
      <h2>Understanding your pathways</h2>
      <p>Which system matters most for you depends on your target country, your course level, and your timeline. We help you understand all of it before you apply anywhere.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">United States</span>
      <h3>Mostly direct, university-by-university applications</h3>
      <p>Undergraduate admission in the US is usually direct to each university (often via the Common Application or a university's own portal), evaluated holistically alongside test scores, essays, and recommendations. Postgraduate admission typically runs directly through each university's own department, with no shared national process.</p>
      <ul>
        <li>Undergraduate applicants are commonly asked for SAT or ACT scores, plus an English-proficiency score (IELTS or TOEFL) if you weren't educated in English.</li>
        <li>Postgraduate applicants are often asked for GRE (general programmes) or GMAT (business programmes), alongside an English-proficiency score.</li>
        <li>Each university sets its own deadlines and requirements &mdash; there's no single national counselling process like JEE or NEET.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">United Kingdom</span>
      <h3>One shared application system for undergraduate study</h3>
      <p>Undergraduate admission to UK universities runs through UCAS, a single portal where you apply to up to five courses with one application and one personal statement. Postgraduate admission is usually direct to each university instead.</p>
      <ul>
        <li>An English-proficiency score (IELTS or TOEFL) is required for most international applicants.</li>
        <li>UCAS runs on fixed yearly cycles with real deadlines &mdash; missing one can mean waiting for the next cycle.</li>
        <li>We help you understand how UCAS offers, conditions, and firm/insurance choices actually work.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Canada, Australia &amp; Germany</span>
      <h3>Direct-to-university systems, each with its own rules</h3>
      <p>These work similarly to the US in that you generally apply directly to each university, but intakes, test requirements, and visa processes differ meaningfully by country.</p>
      <ul>
        <li>An English-proficiency score (IELTS or TOEFL) is required almost everywhere; some German programmes also require German-language proficiency.</li>
        <li>Intake seasons and deadlines vary by country and by university &mdash; we help you track the ones relevant to you.</li>
        <li>Visa and proof-of-funds requirements differ significantly by country; we walk you through what's genuinely needed, not a generic checklist.</li>
      </ul>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <div class="section-head">
      <h2>What you'll typically be asked for</h2>
      <p>The exact list depends on your target country and course, but most applications draw from the same core set of documents.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Common requirements</span>
      <h3>Across most countries and application systems</h3>
      <ul>
        <li>Academic transcripts and certificates, often with official translations.</li>
        <li>A statement of purpose or personal statement, specific to each application.</li>
        <li>Letters of recommendation from teachers or employers.</li>
        <li>Standardised test scores where required (SAT/ACT, GRE/GMAT, IELTS/TOEFL) &mdash; see the pathways above for which apply to you.</li>
        <li>Proof of funds and visa documentation, once you have an offer.</li>
      </ul>
    </div>

    <div class="cta-row mt-6">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger data-prefill-course="Study Abroad">Check Your Study Abroad Options</button>
    </div>
  </div>
</section>
"""

write("study-abroad", page(
    "study-abroad",
    "Study Abroad Guidance: USA, UK, Canada, Australia & Germany | DegreeLelo",
    "Understand how admission works for studying abroad — UCAS, the Common Application, SAT/ACT, IELTS/TOEFL, GRE/GMAT, and visa requirements — explained plainly. Honest guidance from DegreeLelo, no guaranteed outcomes.",
    "study-abroad",
    study_abroad_main,
))

# --------------------------------------------------------------------------
# DISTANCE & OPEN EDUCATION
# --------------------------------------------------------------------------

distance_education_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Distance &amp; Open Education</span>
    <h1>Distance, Online &amp; Open Schooling Guidance</h1>
    <p class="lede">Not every student's path runs through a regular, full-time campus &mdash; and that's fine, as long as the programme you choose is genuinely recognised. Here's how distance education, online degrees, and open schooling actually work.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="section-head">
      <h2>Choosing how you study</h2>
      <p>Distance, online, and regular programmes each suit a different situation. We help you understand what each one actually involves before you commit time or money to any of them.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Distance Education</span>
      <h3>Study at your own pace, from anywhere</h3>
      <p>Distance-mode programmes let you work toward a degree without attending regular classroom sessions &mdash; a genuine option if you're working, managing family responsibilities, or simply not near a campus that offers your course.</p>
      <ul>
        <li>Best suited if you need flexibility around a job, family, or location.</li>
        <li>Recognition depends entirely on the awarding university's own approval for that specific programme &mdash; we help you verify this before you enrol.</li>
        <li>We help you tell genuinely recognised distance programmes apart from ones that are simply marketed as one.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Online Education</span>
      <h3>Structured coursework, delivered digitally</h3>
      <p>Online degree programmes are delivered through live sessions, recorded lectures, and online assessments, run by universities that hold specific approval to offer that programme in online mode &mdash; a separate approval from their regular or distance offerings.</p>
      <ul>
        <li>Suits students comfortable with self-directed, screen-based learning.</li>
        <li>Not everything sold as &ldquo;online&rdquo; carries a valid online-mode approval &mdash; this is exactly what we check before recommending one.</li>
        <li>We verify the university's approval for its online programmes specifically, not just its on-campus ones.</li>
      </ul>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Regular Education</span>
      <h3>The traditional full-time campus route</h3>
      <p>Regular, on-campus programmes remain the standard route for most students &mdash; in-person classes, labs, and campus life. If flexibility isn't a constraint for you, it's usually still the most widely recognised and employer-familiar option.</p>
      <ul>
        <li>Best if you can commit to full-time, in-person study.</li>
        <li>Our <a href="engineering.html" class="text-link">Engineering</a>, <a href="management.html" class="text-link">Management</a>, and <a href="medical.html" class="text-link">Medical</a> guidance covers admission into this mode.</li>
      </ul>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="container">
    <div class="section-head">
      <h2>Open schooling for Class 10 and Class 12</h2>
      <p>Open schooling boards let you complete Class 10 or Class 12 outside the regular school structure &mdash; a genuine option if you've had a gap year, are resuming study after a break, or need an exam schedule a regular school can't offer.</p>
    </div>

    <div class="pathway">
      <span class="pathway-tag">Who it's for</span>
      <h3>Flexible schooling, for a real range of situations</h3>
      <ul>
        <li>Students who've had a gap year and want to complete Class 10 or 12 without repeating a full academic year.</li>
        <li>Students resuming education after dropping out, at any age.</li>
        <li>Students who need to combine study with work, sport, or another serious commitment.</li>
        <li>Adult learners completing school-level education later in life.</li>
      </ul>
    </div>

    <div class="notice" style="margin-top:2rem;">
      {ICON_INFO}
      <div>
        <strong>Verify recognition before you enrol</strong>
        <p>Whether a specific board's certificate is accepted for a college admission, a competitive exam, or a job depends on that board's recognition status, its rules for the year you enrol, and how the specific admission or exam authority treats it. Passing the exam itself does not automatically guarantee acceptance everywhere. We help you verify a board's recognition before you commit &mdash; not after.</p>
      </div>
    </div>

    <p class="mt-8"><a href="colleges.html?category=Distance%20%26%20Open%20Education" class="text-link">Browse Distance &amp; Open Education institutions in our directory &rarr;</a></p>

    <div class="cta-row mt-6">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger data-prefill-course="Distance & Open Education">Check Your Options</button>
    </div>
  </div>
</section>
"""

write("distance-education", page(
    "distance-education",
    "Distance, Online & Open Schooling Guidance | DegreeLelo",
    "Understand distance education, online degrees, and open schooling for Class 10 and 12 — how each works, who it suits, and what to verify before you enrol. Honest guidance from DegreeLelo.",
    "distance-education",
    distance_education_main,
))

# --------------------------------------------------------------------------
# COLLEGE PREDICTOR
# --------------------------------------------------------------------------

predictor_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Free Tool</span>
    <h1>College Predictor</h1>
    <p class="lede">A quick, honest starting point &mdash; tell us your state, course, and score. Where we have verified route data, we'll show it. Where we don't, we say so, and a counsellor reviews your profile personally.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="predictor-card" style="max-width:640px; margin-inline:auto;">
      <form id="predictor-form">
        <div class="field">
          <label for="state">State</label>
          <select id="state" name="state" required>
            <option value="">Select your state</option>
            <option value="Karnataka">Karnataka</option>
            <option value="Maharashtra">Maharashtra</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div class="field">
          <label for="course">Course type</label>
          <select id="course" name="course" required>
            <option value="">Select a course type</option>
            <option value="Engineering">Engineering</option>
            <option value="Management">Management</option>
            <option value="Medical">Medical</option>
          </select>
        </div>
        <div class="field">
          <label for="score">Your score / percentile</label>
          <input type="text" id="score" name="score" placeholder="e.g. 91.2 percentile or rank 4500" required>
          <span class="hint">Enter whatever figure you have &mdash; exam rank, percentile, or marks.</span>
        </div>
        <button type="submit" class="btn btn-primary btn-block btn-lg">Check My Options</button>
      </form>

      <div id="predictor-result" class="predictor-result" hidden></div>
    </div>

    <p class="text-center" style="max-width:560px; margin:2rem auto 0; font-size:var(--text-sm); color:var(--color-text-soft);">
      This tool currently gives verified route guidance only for Engineering and Management in Karnataka and Maharashtra. For every other combination, our counsellors personally review your profile &mdash; we never generate a college list we can't stand behind. You can also browse our full <a href="colleges.html" class="text-link">College Directory</a> any time.
    </p>
  </div>
</section>
"""

write("college-predictor", page(
    "college-predictor",
    "Free College Predictor — Check Your Admission Options | DegreeLelo",
    "Use DegreeLelo's free college predictor to check realistic engineering, management, and medical admission routes based on your state, course, and score.",
    "predictor",
    predictor_main,
))

# --------------------------------------------------------------------------
# COLLEGE DIRECTORY
# --------------------------------------------------------------------------

with open(os.path.join(OUT_DIR, "data", "colleges.json")) as _f:
    _colleges = json.load(_f)

_states = sorted({c["state"] for c in _colleges if c.get("state")})
_categories = sorted({c["category"] for c in _colleges})
_courses = sorted({course for c in _colleges for course in c.get("courses", [])})

_state_options = "\n".join(f'            <option value="{s}">{s}</option>' for s in _states)
_category_options = "\n".join(f'            <option value="{c}">{c}</option>' for c in _categories)
_course_options = "\n".join(f'            <option value="{c}">{c}</option>' for c in _courses)

directory_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">College Directory</span>
    <h1>College Directory</h1>
    <p class="lede">{len(_colleges)} institutions across Engineering, Management, Medical, Law, and Design, compiled from our own verified research and our partner counselling network. Filter by state, category, or course, or search by name.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="directory-controls">
      <div class="field">
        <label for="dir-search">Search</label>
        <input type="search" id="dir-search" placeholder="College or city name">
      </div>
      <div class="field">
        <label for="dir-state">State</label>
        <select id="dir-state">
          <option value="">All states</option>
{_state_options}
        </select>
      </div>
      <div class="field">
        <label for="dir-category">Category</label>
        <select id="dir-category">
          <option value="">All categories</option>
{_category_options}
        </select>
      </div>
      <div class="field">
        <label for="dir-course">Course</label>
        <select id="dir-course">
          <option value="">All courses</option>
{_course_options}
        </select>
        <span class="hint">Only shown where the specific degree is stated in our data.</span>
      </div>
    </div>

    <p id="directory-count" class="directory-count">Loading colleges&hellip;</p>
    <div id="directory-list" class="directory-list"></div>
    <div id="directory-empty" class="empty-state" hidden>
      {ICON_INFO}
      <h2 style="font-size:var(--text-xl);">No colleges match those filters</h2>
      <p>Try a different state, category, or search term &mdash; or talk to a counsellor directly.</p>
      <div class="cta-row" style="justify-content:center; margin-top:1.5rem;">
        <button type="button" class="btn btn-primary" data-modal-trigger>Enquire Now</button>
      </div>
    </div>

    <p class="text-center" style="max-width:640px; margin:2.5rem auto 0; font-size:var(--text-sm); color:var(--color-text-soft);">
      Fees and entrance-exam details shown here are indicative, sourced from our own research or our partner network, and can change. Nothing here is a guarantee of admission or of eligibility &mdash; a counsellor confirms current details before you apply.
    </p>
  </div>
</section>
"""

write("colleges", page(
    "colleges",
    "College Directory — Engineering, Management, Medical & Law Colleges | DegreeLelo",
    f"Browse {len(_colleges)} colleges across India for Engineering, Management, Medical, Law, and Design admissions. Filter by state and category, with verified and partner-network institutions clearly marked.",
    "colleges",
    directory_main,
))

# --------------------------------------------------------------------------
# BLOG
# --------------------------------------------------------------------------

BLOG_POSTS = [
    {
        "slug": "blog-josaa-vs-csab-jee-counselling",
        "category": "Engineering",
        "icon": ICON_CAP,
        "title": "JoSAA vs CSAB: What's the Difference in JEE Counselling?",
        "lede": "JEE counselling runs through two separate, sequential bodies, not one. Mixing them up costs students real seats.",
        "excerpt": "JoSAA and CSAB aren't the same process with two names. Here's what each one actually handles, and why the distinction matters.",
        "vertical_href": "engineering.html",
        "vertical_label": "Engineering",
        "prefill_course": "Engineering",
        "body": f"""
      <h2>What JoSAA handles</h2>
      <p>JoSAA (Joint Seat Allocation Authority) conducts the centralised counselling for admission to the IITs, NITs, IIITs, and other Centrally Funded Technical Institutes (CFTIs), based on JEE Main and JEE Advanced ranks. It runs multiple rounds of seat allotment, each with its own choice-filling, seat-acceptance, and document-verification window.</p>

      <h2>What CSAB handles</h2>
      <p>CSAB (Central Seat Allocation Board) conducts a separate, later counselling process &mdash; primarily for NITs, IIITs, and CFTIs &mdash; covering seats that remain vacant after JoSAA's rounds conclude, plus special rounds for specific categories. It uses your JEE Main rank, but registration and counselling are distinct from JoSAA's process.</p>

      <h2>Why the distinction matters</h2>
      <ul>
        <li>Missing JoSAA doesn't automatically roll you into CSAB &mdash; you generally need to register separately once CSAB opens.</li>
        <li>Choice-filling strategy differs between the two, since CSAB works with a narrower, different set of vacant seats.</li>
        <li>Deadlines for each are set independently and can shift from year to year.</li>
      </ul>

      <div class="notice notice-info">
        {ICON_INFO}
        <div>
          <strong>Confirm current details yourself</strong>
          <p>Exact seat availability, rounds, and deadlines are set by JoSAA and CSAB each year and can change &mdash; always check josaa.nic.in and csab.nic.in directly rather than relying on a previous year's numbers. We track this live with you rather than from memory.</p>
        </div>
      </div>
""",
    },
    {
        "slug": "blog-neet-counselling-documents-checklist",
        "category": "Medical",
        "icon": ICON_MEDICAL,
        "title": "NEET Counselling Documents Checklist: What to Carry to Every Round",
        "lede": "Missing one document can cost you a counselling round entirely. Here's what's typically asked for, and why 'typically' still means you verify it yourself.",
        "excerpt": "A practical rundown of what NEET-UG counselling authorities commonly ask for at each round — and why you shouldn't rely on last year's list.",
        "vertical_href": "medical.html",
        "vertical_label": "Medical",
        "prefill_course": "Medical",
        "body": f"""
      <h2>Documents counselling authorities commonly ask for</h2>
      <ul>
        <li>NEET-UG admit card and scorecard/rank letter</li>
        <li>Class 10 and Class 12 mark sheets and certificates, for age and eligibility proof</li>
        <li>A valid government photo ID (Aadhaar, passport, etc.)</li>
        <li>Category certificate, if applicable (caste, EWS, PwD, and so on), issued in the format and validity window the authority specifies</li>
        <li>Domicile or residence certificate, for state quota counselling</li>
        <li>Passport-size photographs in the specified format</li>
        <li>Counselling registration receipt and fee-payment proof</li>
      </ul>

      <h2>Why &ldquo;typically&rdquo; still means verify</h2>
      <p>Exact document lists and accepted formats differ between the All India Quota counselling (run by the MCC) and each state's own counselling authority, and can change from one counselling cycle to the next. A document accepted last year in one format isn't guaranteed to be accepted the same way this year.</p>

      <div class="notice notice-info">
        {ICON_INFO}
        <div>
          <strong>We check the current notification, not last year's</strong>
          <p>We don't guess which documents you need &mdash; we confirm the current official notification for your specific quota and state before telling you what to carry.</p>
        </div>
      </div>
""",
    },
    {
        "slug": "blog-cat-vs-cmat-vs-mat",
        "category": "Management",
        "icon": ICON_BRIEFCASE,
        "title": "CAT vs CMAT vs MAT: Which MBA Entrance Exam Actually Fits You?",
        "lede": "Three different exams, three different rhythms. Here's how to decide which one(s) are actually worth your prep time.",
        "excerpt": "Instead of attempting all three exams by default, start from your target college list and work backward to the exam that actually opens those doors.",
        "vertical_href": "management.html",
        "vertical_label": "Management",
        "prefill_course": "Management",
        "body": f"""
      <h2>CAT &mdash; for IIMs and top CAT-accepting institutes</h2>
      <p>CAT is a single-attempt, high-stakes exam held once a year, primarily relevant if you're targeting the IIMs or other institutes that weight CAT scores heavily in their own selection process.</p>

      <h2>CMAT &mdash; broader acceptance, NTA-conducted</h2>
      <p>CMAT is accepted by a wide range of government and private B-schools, including many AICTE-approved institutes, and tends to have a broader acceptance net than CAT.</p>

      <h2>MAT &mdash; multiple sessions a year</h2>
      <p>MAT runs in multiple sessions through the year, giving you more than one shot at your best score, and is accepted by a large number of private B-schools.</p>

      <h2>How to actually decide</h2>
      <ul>
        <li>Start from your target institutes' list, not the exam calendar &mdash; check which exams your shortlisted colleges actually accept before committing prep time to any of them.</li>
        <li>If your shortlist is IIM-heavy, CAT preparation should be the priority; don't spread yourself across three exams for institutes that only need one.</li>
        <li>If you want more attempts or scheduling flexibility, MAT's multiple sessions can be a genuine advantage over a single high-stakes exam.</li>
      </ul>

      <div class="notice notice-info">
        {ICON_INFO}
        <div>
          <strong>We map your actual shortlist, not a generic list</strong>
          <p>We check which exams your specific target colleges accept, instead of recommending every exam &ldquo;just in case.&rdquo;</p>
        </div>
      </div>
""",
    },
    {
        "slug": "blog-study-abroad-application-documents",
        "category": "Study Abroad",
        "icon": ICON_GLOBE,
        "title": "7 Documents Every Study-Abroad Application Will Ask For",
        "lede": "Whether you're applying through UCAS, the Common Application, or directly to a university, most applications draw from the same core document set.",
        "excerpt": "A closer look at the seven documents nearly every study-abroad application needs, and why some of them take weeks to arrange.",
        "vertical_href": "study-abroad.html",
        "vertical_label": "Study Abroad",
        "prefill_course": "Study Abroad",
        "body": f"""
      <h2>1. Academic transcripts and certificates</h2>
      <p>Official records of your coursework and grades &mdash; often needing certified or official English translations if your original records aren't in English.</p>

      <h2>2. Statement of purpose or personal statement</h2>
      <p>A written piece specific to each application, explaining your interest in that course and institution &mdash; not something that can be reused word-for-word across applications.</p>

      <h2>3. Letters of recommendation</h2>
      <p>From teachers, professors, or employers who can speak to your academic or professional ability. These typically take weeks to arrange, so request them early.</p>

      <h2>4. Standardised test scores</h2>
      <p>SAT or ACT for US undergraduate programmes, GRE or GMAT for postgraduate programmes, where required &mdash; see our <a href="study-abroad.html" class="text-link">Study Abroad guide</a> for which applies to your target country and level.</p>

      <h2>5. English-proficiency scores</h2>
      <p>IELTS or TOEFL, required by nearly every English-medium programme if you weren't educated in English, with each university setting its own minimum score.</p>

      <h2>6. Proof of funds</h2>
      <p>Evidence that you (or your sponsor) can cover tuition and living costs &mdash; usually required once you have a conditional offer, before a visa application can proceed.</p>

      <h2>7. Visa documentation</h2>
      <p>Requirements differ significantly by destination country, and usually can't be finalised until you have a confirmed offer in hand.</p>

      <div class="notice notice-info">
        {ICON_INFO}
        <div>
          <strong>Start the slow documents first</strong>
          <p>Recommendation letters and certified transcripts take the longest to arrange &mdash; starting those early is usually what actually determines whether you make a deadline, not last-minute effort on the statement of purpose.</p>
        </div>
      </div>
""",
    },
    {
        "slug": "blog-open-schooling-vs-regular-schooling",
        "category": "Distance & Open Education",
        "icon": ICON_SHIELD,
        "title": "Open Schooling vs Regular Schooling: Will Your Certificate Be Accepted?",
        "lede": "Open schooling is a genuine, recognised option for completing Class 10 or 12 outside a regular classroom &mdash; but “recognised” depends on specifics worth checking before you enrol, not after.",
        "excerpt": "Acceptance isn't a single yes or no. Here's the three separate things that actually decide whether an open-schooling certificate works for your next step.",
        "vertical_href": "distance-education.html",
        "vertical_label": "Distance &amp; Open Education",
        "prefill_course": "Distance & Open Education",
        "body": f"""
      <h2>What makes open schooling different</h2>
      <p>Open schooling boards let students complete Class 10 or Class 12 through flexible study and examination schedules, without mandatory daily classroom attendance &mdash; useful for gap-year students, dropouts resuming study, or anyone combining study with work.</p>

      <h2>Where &ldquo;will it be accepted&rdquo; actually gets decided</h2>
      <p>Acceptance isn't a single yes-or-no question. It depends on three separate things: whether the specific board is recognised by the relevant education authority, the rules of the college or exam body you're applying to next (which can treat open-schooling certificates differently from regular-board ones), and the specific year's rules in force when you enrol, which can change.</p>

      <ul>
        <li>A board's general recognition doesn't automatically mean every college or competitive exam treats its certificate identically to a regular board's.</li>
        <li>Some admissions or exams specify minimum subject combinations or a minimum number of subjects passed in one sitting &mdash; open schooling's flexible structure can interact with these rules in ways worth checking in advance.</li>
        <li>Recognition rules can change between academic years, so check current status rather than what was true when a friend or sibling enrolled.</li>
      </ul>

      <div class="notice notice-info">
        {ICON_INFO}
        <div>
          <strong>We verify it for your specific next step</strong>
          <p>We check a specific board's recognition status against your specific next step &mdash; a college, an exam, a job &mdash; before you enrol, not after.</p>
        </div>
      </div>
""",
    },
]

def blog_post_main(post):
    return f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">{post['category']}</span>
    <h1>{post['title']}</h1>
    <p class="lede">{post['lede']}</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="prose-card prose" style="max-width:760px; margin-inline:auto;">
{post['body']}
    </div>

    <div class="cta-row mt-8" style="justify-content:center; max-width:760px; margin-inline:auto;">
      <a href="{post['vertical_href']}" class="btn btn-outline">Read our {post['vertical_label']} guide</a>
      <button type="button" class="btn btn-primary" data-modal-trigger data-prefill-course="{post['prefill_course']}">Enquire Now</button>
    </div>

    <p class="text-center mt-6"><a href="blog.html" class="text-link">&larr; Back to all articles</a></p>
  </div>
</section>
"""

for _post in BLOG_POSTS:
    write(_post["slug"], page(
        _post["slug"],
        f"{_post['title']} | DegreeLelo",
        _post["excerpt"],
        "blog",
        blog_post_main(_post),
    ))

_blog_cards = "\n".join(f"""      <article class="card">
        <div class="card-icon">{p['icon']}</div>
        <span class="pathway-tag">{p['category']}</span>
        <h3>{p['title']}</h3>
        <p>{p['excerpt']}</p>
        <a href="{p['slug']}.html" class="card-link">Read article {ICON_CHEVRON_RIGHT}</a>
      </article>""" for p in BLOG_POSTS)

blog_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Blog</span>
    <h1>Admission Tips &amp; Updates</h1>
    <p class="lede">Guidance on exams, counselling, and admission timelines &mdash; written in plain language, covering every programme we guide students through.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="grid grid-3">
{_blog_cards}
    </div>
    <div class="cta-row mt-8" style="justify-content:center;">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger>Check Your College Options</button>
    </div>
  </div>
</section>
"""

write("blog", page(
    "blog",
    "Blog — Admission Tips & Updates | DegreeLelo",
    "Plain-language articles on JEE, NEET, CAT/CMAT/MAT counselling, studying abroad, and open schooling — honest guidance from DegreeLelo, no guesswork.",
    "blog",
    blog_main,
))

# --------------------------------------------------------------------------
# FAQ
# --------------------------------------------------------------------------

faqs = [
    ("Am I eligible even if my score or percentile is on the lower side?",
     "Eligibility depends on the exam, your category, and the state you're applying in &mdash; there's no single cutoff that applies to everyone. Rather than judge you against a fixed number, we review your actual profile and tell you honestly which routes are realistically open to you."),
    ("What does DegreeLelo charge for its services?",
     "Our fees depend on the scope of guidance you need, so we discuss them directly and transparently with each client rather than listing a fixed number here. You'll know exactly what you're paying for before you commit to anything."),
    ("How does the counselling process actually work?",
     "After your exam result, you register for counselling with the relevant authority, fill in your college and course choices in order of preference, and seats are allotted round by round based on your rank/score, category, and choices. Each round has its own document verification and seat-acceptance deadline &mdash; we help you stay on top of all of it."),
    ("What's the admission timeline I should expect?",
     "Most exams are conducted once a year, with counselling running over the following weeks to months. Exact dates are announced by the respective exam and counselling authorities and can shift year to year &mdash; we track them and keep you updated so you never miss a deadline."),
    ("Do you guarantee a seat at a particular college?",
     "No. We do not guarantee admission to any institution, and we never offer to bypass eligibility rules. Final admission decisions always rest with the institutions and the relevant exam or counselling authority &mdash; our role is to guide you to the best genuinely available options."),
    ("Which programs does DegreeLelo currently support?",
     "We currently guide students through Engineering, Management, Medical (NEET counselling), Study Abroad (USA, UK, Canada, Australia &amp; Germany), and Distance &amp; Open Education admissions."),
]

faq_items = "\n".join(f"""    <details class="faq-item">
      <summary><span>{q}</span><span class="faq-icon" aria-hidden="true"></span></summary>
      <p>{a}</p>
    </details>""" for q, a in faqs)

faq_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">FAQ</span>
    <h1>Frequently Asked Questions</h1>
    <p class="lede">Straight answers on eligibility, fees, counselling, and timelines.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="prose-card" style="max-width:760px; margin-inline:auto;">
{faq_items}
    </div>
    <div class="cta-row text-center mt-8" style="justify-content:center;">
      <button type="button" class="btn btn-primary btn-lg" data-modal-trigger>Check Your College Options</button>
    </div>
  </div>
</section>
"""

write("faq", page(
    "faq",
    "FAQs — Admission Eligibility, Fees & Counselling Process | DegreeLelo",
    "Answers to common questions about admission eligibility, fees, how counselling works, and application timelines. Get in touch with DegreeLelo for personalised guidance.",
    "faq",
    faq_main,
))

# --------------------------------------------------------------------------
# CONTACT
# --------------------------------------------------------------------------

contact_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Contact</span>
    <h1>Talk to a DegreeLelo Counsellor</h1>
    <p class="lede">Whichever way you reach out, a real counsellor reads and responds &mdash; not a bot, not a script.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="grid grid-2" style="align-items:start;">
      <div class="prose-card">
        <h2>Get in touch</h2>
        <p>Fill in the enquiry form and a counsellor will get back to you personally, or message us directly on WhatsApp if you'd rather chat right away.</p>
        <div class="cta-row mt-6">
          <button type="button" class="btn btn-primary btn-lg" data-modal-trigger>Enquire Now</button>
          <a href="https://wa.me/917304305424" data-whatsapp-link class="btn btn-whatsapp btn-lg" target="_blank" rel="noopener">
            {ICON_CHAT} Chat with us on WhatsApp
          </a>
        </div>
      </div>
      <div class="prose-card">
        <h2>Other ways to reach us</h2>
        <div class="stack">
          <div class="notice notice-info">
            {ICON_MAIL}
            <div>
              <strong>Email</strong>
              <p><a href="mailto:degreelelo@gmail.com" class="text-link">degreelelo@gmail.com</a></p>
            </div>
          </div>
          <div class="notice notice-info">
            {ICON_PIN}
            <div>
              <strong>Serving students across India</strong>
              <p>Guidance for Engineering, Management, Medical, and Study Abroad admissions &mdash; wherever you're applying from.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
"""

write("contact", page(
    "contact",
    "Contact DegreeLelo — Book a Free College Assessment",
    "Get in touch with DegreeLelo for personalised admission guidance. Fill the enquiry form or chat with us directly on WhatsApp.",
    "contact",
    contact_main,
))

# --------------------------------------------------------------------------
# PRIVACY POLICY
# --------------------------------------------------------------------------

privacy_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Legal</span>
    <h1>Privacy Policy</h1>
    <p class="lede">Last updated: September 2026. Plain language, no legal boilerplate &mdash; here's exactly what we do with your information.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="prose-card prose" style="max-width:760px; margin-inline:auto;">
      <h2>What we collect</h2>
      <p>When you use our enquiry form or College Predictor, or message us on WhatsApp or email, we may collect your name, phone number, email address, city, course of interest, and academic scores or exam percentiles that you choose to share.</p>

      <h2>Why we collect it</h2>
      <p>We use this information for one purpose: to provide you with admission counselling. That means understanding your eligibility, matching you with realistic routes and institutions, and following up with guidance relevant to your profile.</p>

      <h2>How we use it</h2>
      <p>Your details are used internally by our counselling team, and shared with educational institutions or admission partners only where it's directly part of helping you apply or get counselled &mdash; never for unrelated marketing by third parties.</p>

      <h2>We don't sell your data</h2>
      <p>We do not sell your personal information to third parties outside the admission process. Any sharing with institutions or partners happens only in service of your own admission guidance.</p>

      <h2>Data from students under 18</h2>
      <p>Many of our users are school students applying to undergraduate programs. If you're a parent or guardian of a student under 18, you're welcome to contact us at any time to review what information we hold about your child, or to request that it be deleted.</p>

      <h2>Your rights</h2>
      <p>You can ask us to show you what data we hold about you, correct it, or delete it, at any time. Write to us at <a href="mailto:degreelelo@gmail.com" class="text-link">degreelelo@gmail.com</a> and we'll act on it personally &mdash; there's no automated process to navigate.</p>
    </div>
  </div>
</section>
"""

write("privacy-policy", page(
    "privacy-policy",
    "Privacy Policy | DegreeLelo",
    "Read DegreeLelo's privacy policy — what personal data we collect, why we collect it, how it's used for admission counselling, and how to request access or deletion.",
    "privacy",
    privacy_main,
))

# --------------------------------------------------------------------------
# TERMS & DISCLAIMER
# --------------------------------------------------------------------------

terms_main = f"""
<div class="page-header">
  <div class="container">
    <span class="eyebrow">Legal</span>
    <h1>Terms &amp; Disclaimer</h1>
    <p class="lede">Last updated: September 2026. A short, honest statement of what DegreeLelo is &mdash; and isn't.</p>
  </div>
</div>

<section class="section">
  <div class="container">
    <div class="prose-card prose" style="max-width:760px; margin-inline:auto;">
      <h2>What DegreeLelo is</h2>
      <p>DegreeLelo is an admission counselling and advisory service. We help students and parents understand eligibility, exams, and realistic admission pathways across Engineering, Management, Medical, and Study Abroad programs.</p>

      <h2>Not a guarantee of admission</h2>
      <p>Nothing on this website, or discussed with our counsellors, is a guarantee of admission to any institution. We provide guidance based on your profile and publicly available exam and counselling rules &mdash; we do not control admission outcomes.</p>

      <h2>Decisions rest with institutions and authorities</h2>
      <p>Final admission decisions rest entirely with the relevant institutions and the applicable exam or counselling authority (such as JoSAA, CSAB, COMEDK, state CET cells, or NEET counselling bodies). DegreeLelo has no authority over, and does not influence, those decisions.</p>

      <h2>We do not bypass eligibility rules</h2>
      <p>We do not offer, and will not attempt, to bypass eligibility criteria, reservation rules, or any other admission requirement set by an institution or exam authority. Any pathway we recommend is one that is genuinely open to you under the applicable rules.</p>

      <h2>Terms of engagement</h2>
      <p>The specific scope of services and fees for any counselling engagement are agreed directly with each client before work begins. These terms may be updated from time to time; the version on this page is the one currently in effect.</p>

      <h2>Questions</h2>
      <p>If anything here is unclear, write to us at <a href="mailto:degreelelo@gmail.com" class="text-link">degreelelo@gmail.com</a> and we'll explain in plain language.</p>
    </div>
  </div>
</section>
"""

write("terms", page(
    "terms",
    "Terms & Disclaimer | DegreeLelo",
    "DegreeLelo's terms of service and admission disclaimer — we provide counselling and advisory support; final admission decisions rest with institutions and exam authorities.",
    "terms",
    terms_main,
))

# --------------------------------------------------------------------------
# 404
# --------------------------------------------------------------------------

error_main = f"""
<div class="container error-page">
  <div class="error-code">404</div>
  <h1>Page Not Found</h1>
  <p class="lede" style="max-width:480px; margin-inline:auto;">The page you're looking for doesn't exist or may have moved. Let's get you back on track.</p>
  <div class="cta-row" style="justify-content:center; margin-top:2rem;">
    <a href="index.html" class="btn btn-primary btn-lg">Back to Home</a>
  </div>
</div>
"""

write("404", page(
    "404",
    "Page Not Found | DegreeLelo",
    "The page you're looking for doesn't exist. Return to the DegreeLelo homepage to continue exploring admission guidance.",
    "",
    error_main,
    robots="noindex, follow",
))

print("\\nAll pages generated.")
