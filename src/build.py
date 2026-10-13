#!/usr/bin/env python3
"""Static site builder for Launch Lead Gen.

Usage: python3 src/build.py
Writes the finished site to site/. No third-party dependencies.
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "site"
DOMAIN = "https://launchleadgen.io"
BRAND = "Launch Lead Gen"
EMAIL = "info@launchleadgen.com"
PHONE = "(210) 441-6650"
PHONE_HREF = "tel:+12104416650"
YEAR = date.today().year
OG_IMAGE = f"{DOMAIN}/assets/og.jpg"
LEGAL_UPDATED = "October 13, 2026"  # change when the policy text changes

# ---------------------------------------------------------------- icons (24px line set)
ICONS = {
    "drop": '<path d="M12 2.7s6 6.4 6 11a6 6 0 0 1-12 0c0-4.6 6-11 6-11z"/>',
    "sprinkler": '<path d="M12 22v-7"/><path d="M8 15h8"/><path d="M12 11c-3-3-7-3-9-2"/><path d="M12 11c3-3 7-3 9-2"/><path d="M12 11V7"/><path d="M9 4c1.5-1 4.5-1 6 0"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "map": '<path d="M9 3 3 6v15l6-3 6 3 6-3V3l-6 3-6-3z"/><path d="M9 3v15M15 6v15"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    "bars": '<path d="M6 20V14M12 20V8M18 20V4"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "refresh": '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7l10-5z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "home": '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "wave": '<path d="M2 12c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 17c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 7c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/>',
    "pipe": '<path d="M3 7h10a4 4 0 0 1 4 4v10"/><path d="M3 11h8a2 2 0 0 1 2 2v8"/><path d="M3 5v8M15 21h4"/>',
    "pump": '<rect x="6" y="9" width="12" height="13" rx="2"/><path d="M12 9V3h5"/><path d="M10 14h4"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "wifi": '<path d="M5 12.5a10 10 0 0 1 14 0"/><path d="M8.5 16a5 5 0 0 1 7 0"/><path d="M12 19.5h.01"/><path d="M2 9a15 15 0 0 1 20 0"/>',
    "snow": '<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/>',
    "tool": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


# ---------------------------------------------------------------- brand mark
# Traced from the brand book: two parallel slashes rising into an arrow.
MARK_LEFT = "7.4,60.2 43.2,27.3 58.5,27.3 22.7,60.2"
MARK_RIGHT = "36.4,60.2 61,37.5 62,27 72.7,16 58,16 70,5 92,5 92,24 80,36 80,23 71.6,31.4 71.6,43 52.8,60.2"


def mark(cls="logo-mark", color="#1268E8"):
    return (f'<svg class="{cls}" viewBox="4 2 92 62" aria-hidden="true"><g fill="{color}">'
            f'<polygon points="{MARK_LEFT}"/><polygon points="{MARK_RIGHT}"/></g></svg>')


def lines(cls="lines"):
    """Outline arrow motif used on navy panels (brand book 'blue line arrows')."""
    shape = f'<polygon points="{MARK_LEFT}"/><polygon points="{MARK_RIGHT}"/>'
    return (f'<svg class="{cls}" viewBox="0 0 100 66" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linejoin="round" aria-hidden="true"><g style="vector-effect:non-scaling-stroke">{shape}</g>'
            f'<g transform="translate(-9 7)" opacity=".55">{shape}</g></svg>').replace(
        "<polygon ", '<polygon vector-effect="non-scaling-stroke" ')


def logo(inverse=False):
    cls = "logo inverse" if inverse else "logo"
    return f'<a class="{cls}" href="/" aria-label="{BRAND} home">{mark()}<span class="logo-word"><b>Launch</b><small>LEAD GEN</small></span></a>'


NAV = [
    ("/drainage-leads.html", "Drainage Leads"),
    ("/irrigation-leads.html", "Irrigation Leads"),
    ("/how-it-works.html", "How It Works"),
    ("/pricing.html", "Pricing"),
    ("/blog/", "Blog"),
]


def esc(s):
    return html.escape(s, quote=True)


def header(active):
    current = ' aria-current="page"'
    links = "".join(f'<li><a href="{h}"{current if h == active else ""}>{t}</a></li>' for h, t in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <nav class="wrap nav" aria-label="Main">
    {logo()}
    <ul class="nav-links" id="nav-links">{links}</ul>
    <div class="nav-cta">
      <a class="nav-phone" href="{PHONE_HREF}">{icon("phone")}<span>{PHONE}</span></a>
      <a class="btn btn-primary" href="/contact.html">Talk to Launch {icon("arrow")}</a>
      <button class="menu-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav-links"><span></span><span></span><span></span></button>
    </div>
  </nav>
</header>"""


FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        {logo(inverse=True)}
        <p class="footer-tag">More drainage jobs.<span>Less chasing leads.</span></p>
        <p style="max-width:340px">Exclusive drainage and irrigation leads for contractors.</p>
        <form class="footer-news" data-news>
          <label class="sr-only" for="news-email">Email</label>
          <input id="news-email" type="email" placeholder="Email for monthly guides" required>
          <button class="btn btn-primary" type="submit">Join</button>
        </form>
      </div>
      <div>
        <h4>Leads</h4>
        <ul>
          <li><a href="/drainage-leads.html">Drainage leads</a></li>
          <li><a href="/drainage-leads.html#jobs">French drain leads</a></li>
          <li><a href="/irrigation-leads.html">Irrigation leads</a></li>
          <li><a href="/irrigation-leads.html#jobs">Sprinkler repair leads</a></li>
          <li><a href="/pricing.html">Pricing</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="/how-it-works.html">How it works</a></li>
          <li><a href="/how-it-works.html#quality">Lead quality</a></li>
          <li><a href="/contact.html">Talk to Launch</a></li>
          <li><a href="{PHONE_HREF}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
      <div>
        <h4>Guides</h4>
        <ul>
          <li><a href="/blog/">All articles</a></li>
          <li><a href="/blog/price-french-drain-jobs.html">Pricing drainage jobs</a></li>
          <li><a href="/blog/qualify-drainage-leads.html">Qualifying drainage leads</a></li>
          <li><a href="/blog/exclusive-vs-shared-leads.html">Exclusive vs. shared leads</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <span>&copy; {YEAR} {BRAND}. All rights reserved.</span>
      <nav aria-label="Legal"><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></nav>
    </div>
  </div>
</footer>
<div class="mobile-cta"><a class="btn btn-navy" href="{PHONE_HREF}">{icon("phone")} Call</a><a class="btn btn-primary" href="/contact.html">Check my area {icon("arrow")}</a></div>"""


PAGES = []


def clean_url(path):
    """site/ file path -> public URL (index.html -> /, pricing.html -> /pricing)."""
    if path.endswith("index.html"):
        return "/" + path[: -len("index.html")]
    return "/" + path[: -len(".html")]


def tighten_periods(m):
    """Plus Jakarta's full stop sits loose at display sizes; pull it in on headings."""
    inner = re.sub(r"\.(?=\s|<|$)", '<span class="dot">.</span>', m.group(2))
    return m.group(1) + inner + m.group(3)


def page(path, title, desc, body, active="", schema=None, noindex=False):
    canonical = DOMAIN + clean_url(path)
    ld = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    doc = f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#102A43">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
{ld}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{FOOTER}
<script src="/assets/main.js" defer></script>
</body>
</html>
"""
    doc = re.sub(r"(<h[12][^>]*>)(.*?)(</h[12]>)", tighten_periods, doc, flags=re.S)
    # Cloudflare serves /pricing for pricing.html, so link to clean URLs directly.
    doc = re.sub(r'((?:href|action)=")(/[^"#?]*?)\.html', r"\1\2", doc)
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    PAGES.append((path, noindex))


# ---------------------------------------------------------------- shared blocks
def eyebrow(num, label):
    return f'<span class="eyebrow"><i>{num}</i>/<span>{label}</span></span>'


def faq(items):
    return '<div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div>"


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}}
        for q, a in items]}


def cta_band(title='Check if your area <span class="accent">is open.</span>',
             text="We work with a limited number of contractors in each market. Enter your main ZIP code and we'll confirm availability and pricing within one business day."):
    return f"""<section class="section"><div class="wrap">
  <div class="cta on-navy reveal">
    {lines()}
    <div style="position:relative">
      {eyebrow("→", "Territory check")}
      <h2>{title}</h2>
      <p>{text}</p>
      <ul class="check-row"><li>{icon("check")}No setup fee</li><li>{icon("check")}Month to month</li><li>{icon("check")}Bad leads credited</li></ul>
      <p style="margin-top:22px">Rather talk? Call <a style="color:#fff;font-weight:700" href="{PHONE_HREF}">{PHONE}</a></p>
    </div>
    <form class="territory" data-territory novalidate>
      <h3>Is my area open?</h3>
      <div class="field"><label for="t-zip">Your main ZIP code</label><input id="t-zip" name="zip" inputmode="numeric" maxlength="5" placeholder="e.g. 37064" autocomplete="postal-code"><span class="err"></span></div>
      <div class="field"><label for="t-svc">Lead type</label><select id="t-svc" name="service"><option value="drainage">Drainage</option><option value="irrigation">Irrigation</option><option value="both">Drainage + irrigation</option></select></div>
      <button class="btn btn-primary btn-block" type="submit">Check availability {icon("arrow")}</button>
      <div class="territory-result" role="status" aria-live="polite"></div>
    </form>
  </div>
</div></section>"""


def sample_lead(kind="drainage"):
    if kind == "irrigation":
        rows = [("Service", "New sprinkler system, 6 zones"), ("Property", "Single-family · ~0.3 acre"),
                ("Location", "Frisco, TX 75034"), ("Timeline", "Within 30 days"), ("Ownership", "Owner"),
                ("Notes", "Has seen quotes before"), ("Best time", "Weekdays after 5pm")]
        head, ic = "Irrigation install request", "sprinkler"
    else:
        rows = [("Service", "French drain + downspout tie-in"), ("Problem", "Standing water by patio"),
                ("Location", "Franklin, TN 37064"), ("Timeline", "As soon as possible"), ("Ownership", "Owner"),
                ("Approx. length", "120–150 ft"), ("Photos", "3 attached")]
        head, ic = "Drainage repair request", "drop"
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + '<dt>Phone</dt><dd class="ok">Verified ✓</dd>'
    return f"""<div class="sample-lead reveal">
  <header><strong>{icon(ic)}{head}</strong><span class="tag orange">Exclusive</span></header>
  <dl>{dl}</dl>
  <footer><span>Delivered by text, email &amp; CRM</span><span>Sample lead · details changed</span></footer>
</div>"""


def season_chart(caption):
    # Relative, illustrative demand shape (0–10) by month for each vertical.
    drain = [3, 4, 8, 10, 9, 6, 5, 6, 7, 8, 6, 3]
    irr = [1, 2, 6, 10, 10, 9, 8, 7, 5, 6, 3, 1]
    cols = "".join(
        f'<div class="season-col"><div class="b d" style="height:{d * 10}%;transition-delay:{n * 40}ms"></div>'
        f'<div class="b i" style="height:{i * 10}%;transition-delay:{n * 40 + 20}ms"></div></div>'
        for n, (d, i) in enumerate(zip(drain, irr)))
    labels = "".join(f"<span>{m}</span>" for m in "JFMAMJJASOND")
    return f"""<div class="season reveal" role="img" aria-label="Illustrative chart: drainage demand peaks with spring thaw and fall storms; irrigation peaks from spring start-ups through summer.">
  <div class="season-legend"><span><i style="background:var(--navy)"></i>Drainage</span><span><i style="background:var(--blue)"></i>Irrigation</span></div>
  <div class="season-bars">{cols}</div>
  <div class="season-months">{labels}</div>
  <p class="season-caption">{caption}</p>
</div>"""


CALC_PRESETS = {"drainage": dict(leads=25, cost=95, close=30, ticket=4800),
                "irrigation": dict(leads=30, cost=70, close=35, ticket=3600)}


def calculator(kind="drainage"):
    v = CALC_PRESETS[kind]

    def rng(id_, name, label, mn, mx, step):
        return f"""<div class="range-row"><label for="{id_}">{label}<output for="{id_}"></output></label>
<input type="range" id="{id_}" name="{name}" min="{mn}" max="{mx}" step="{step}" value="{v[name]}"></div>"""
    return f"""<div class="calc reveal" data-calc>
  <div class="calc-inputs">
    <div class="seg" role="group" aria-label="Preset">
      <button type="button" data-preset="drainage" aria-pressed="{str(kind == 'drainage').lower()}">Drainage</button>
      <button type="button" data-preset="irrigation" aria-pressed="{str(kind == 'irrigation').lower()}">Irrigation</button>
    </div>
    {rng("c-leads", "leads", "Leads per month", 5, 80, 1)}
    {rng("c-cost", "cost", "Cost per lead", 30, 200, 5)}
    {rng("c-close", "close", "Your close rate", 5, 70, 1)}
    {rng("c-ticket", "ticket", "Average job value", 500, 15000, 100)}
  </div>
  <div class="calc-out" aria-live="polite">
    {lines()}
    <span class="calc-label">Estimated monthly revenue</span>
    <div class="calc-big" data-out="revenue">$0</div>
    <dl class="calc-rows">
      <div><dt>Jobs closed</dt><dd data-out="jobs">0</dd></div>
      <div><dt>Lead spend</dt><dd data-out="spend">$0</dd></div>
      <div><dt>Cost per closed job</dt><dd data-out="cpa">$0</dd></div>
      <div class="hl"><dt>Revenue per $1 spent</dt><dd data-out="roi">0×</dd></div>
    </dl>
    <p class="calc-note">An estimate from your own numbers, not a guarantee. Close rates and job values vary by market, season and how fast you follow up.</p>
  </div>
</div>"""


def compare_table():
    rows = [
        ("Who else gets the lead", "Nobody. One lead, one contractor.", "Often several companies at once"),
        ("Lead types", "Drainage &amp; irrigation only", "Every trade from one funnel"),
        ("Verification", "Phone-verified, service area checked", "Varies; often unverified forms"),
        ("Territory", "ZIP codes you choose, capped per market", "Open to anyone who pays"),
        ("Contract", "Month to month", "Annual plans and membership fees are common"),
        ("Bad leads", "Credited: wrong numbers, out of area, duplicates", "Dispute processes vary"),
    ]
    body = "".join(
        f'<tr><th scope="row">{a}</th><td class="us"><span class="mark yes">{icon("check")}{b}</span></td>'
        f'<td><span class="mark no">{icon("x")}{c}</span></td></tr>' for a, b, c in rows)
    return f"""<div class="table-scroll reveal"><table class="compare">
<thead><tr><th scope="col"><span class="sr-only">Feature</span></th><th scope="col" class="us">Launch Lead Gen</th><th scope="col">Typical shared-lead marketplace</th></tr></thead>
<tbody>{body}</tbody></table></div>"""


STEPS = [
    ("Choose your area", "Pick your ZIP codes, the job types you want and a weekly lead cap."),
    ("We run local ads", "Search and social campaigns reach homeowners in your area who need drainage or irrigation work."),
    ("We screen each request", "We verify the phone number, confirm the address is in your area, and record the problem and timeline."),
    ("You get the lead", "It arrives by text, email and CRM within a minute, so you can call while the homeowner is still available."),
]


def steps_block():
    return '<div class="steps">' + "".join(
        f'<div class="step reveal d{n}"><span class="n">{n + 1}</span><h3>{t}</h3><p>{d}</p></div>'
        for n, (t, d) in enumerate(STEPS)) + "</div>"


def banner():
    return f"""<div class="banner on-navy reveal">
  <div class="banner-copy">
    {lines()}
    {eyebrow("→", "Talk to Launch")}
    <h2>Great at drainage? <span class="accent">Let's get you more calls.</span></h2>
    <p>Tell us where you work and which jobs you want. We'll confirm your area is open and send pricing within one business day.</p>
    <div><a class="btn btn-primary btn-lg" href="/contact.html">Talk to Launch {icon("arrow")}</a></div>
  </div>
  <div class="banner-photo"><img src="/assets/img/foreman.jpg" alt="Drainage contractor in a Launch Lead Gen cap on a job site" width="412" height="816"></div>
</div>"""


# ---------------------------------------------------------------- posts
COVER_TITLES = {
    "price-french-drain-jobs": "Pricing French drain jobs",
    "qualify-drainage-leads": "Qualifying drainage leads",
    "drainage-demand-calendar": "Drainage demand by month",
    "irrigation-recurring-revenue": "Recurring irrigation revenue",
    "smart-controller-upsell": "Smart controllers and drip",
    "exclusive-vs-shared-leads": "Exclusive vs. shared leads",
}
VARIANTS = ["v-navy", "v-blue", "v-ice"]


def load_posts():
    posts = []
    for f in sorted((SRC / "posts").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*(.*)", raw, re.S)
        meta = json.loads(m.group(1))
        meta["slug"] = f.stem
        meta["body"] = m.group(2)
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)
    for n, p in enumerate(posts):
        p["variant"] = VARIANTS[n % 3]
    return posts


def nice_date(d):
    y, m, dd = map(int, d.split("-"))
    return date(y, m, dd).strftime("%b %-d, %Y")


def cover(p):
    title = COVER_TITLES.get(p["slug"], p["title"])
    return (f'<div class="cover {p["variant"]}" aria-hidden="true">{lines()}<span class="cover-cat">{esc(p["category"])}</span>'
            f'<span class="cover-title">{esc(title)}</span></div>')


def post_card(p, feature=False, cls=""):
    return f"""<a class="post-card {cls}{' post-feature' if feature else ''}" href="/blog/{p['slug']}.html" data-post-cat="{esc(p['category'])}">
  {cover(p)}
  <div class="post-body"><h3>{esc(p['title'])}</h3><p>{esc(p['excerpt'])}</p>
  <div class="post-meta"><span>{nice_date(p['date'])}</span><span>·</span><span>{esc(p['readTime'])}</span></div></div>
</a>"""


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub("<[^>]+>", "", s).lower()).strip("-")[:60]


# ================================================================ PAGES
def build_home(posts):
    home_faq = [
        ("Are the leads really exclusive?", "Yes. Each homeowner request goes to one contractor in that territory. We don't resell it, split it or post it to a marketplace."),
        ("What counts as a drainage or irrigation lead?", "A homeowner in your ZIP codes asking for help with a specific job: French drains, regrading, downspouts, sump pumps, dry wells, sprinkler installs, repairs, drip conversions, controllers, start-ups and winterizations. You pick which job types you want."),
        ("How fast do leads arrive?", "By text and email as soon as the homeowner submits the request, and in your CRM if you connect one. The sooner you call, the more likely you are to book the visit."),
        ("What if a lead is bad?", "Wrong numbers, duplicates, renters without authority and addresses outside your territory are credited back. Flag it from the lead notification and we review it within one business day."),
        ("Do I have to sign a long contract?", "No. Plans are month to month. We ask for a short ramp-up period while campaigns settle in your market. After that you can pause or cancel any time."),
        ("How quickly can I start?", "Most territories go live in about a week: a short onboarding call, ZIP and job-type setup, routing to your phone or CRM, then campaigns launch."),
    ]
    latest = "".join(post_card(p, cls=f"reveal d{n}") for n, p in enumerate(posts[:3]))
    body = f"""
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy reveal">
      {eyebrow("01", "Drainage &amp; irrigation leads")}
      <h1>More drainage jobs. <span class="accent">Less chasing leads.</span></h1>
      <p class="lede">We run local ads for homeowners who need drainage or irrigation work, verify each request by phone, and send it to one contractor in the area. You pay per lead, month to month.</p>
      <form class="hero-form" action="/contact.html" method="get">
        <label class="sr-only" for="h-zip">Your main ZIP code</label>
        <input id="h-zip" name="zip" inputmode="numeric" maxlength="5" pattern="[0-9]{{5}}" placeholder="Your ZIP code" autocomplete="postal-code" required>
        <button class="btn btn-primary btn-lg" type="submit">Check my area {icon("arrow")}</button>
      </form>
      <ul class="hero-trust"><li>{icon("check")}No setup fee</li><li>{icon("check")}Month to month</li><li>{icon("check")}Bad leads credited</li></ul>
      <p class="hero-note">{icon("phone")}Prefer to talk? Call <a href="{PHONE_HREF}">{PHONE}</a></p>
    </div>
  </div>
  <div class="hero-media">
    <div class="hero-photo"><img src="/assets/img/crew.jpg" alt="Drainage crew laying perforated pipe in a gravel trench" width="1132" height="811" fetchpriority="high"></div>
    <div class="hero-slash">{lines("")}</div>
    <div class="lead-pop">
      <div class="ic">{icon("drop")}</div>
      <div><span class="live">New lead</span><strong>French drain, backyard pooling</strong><span>Franklin, TN · Verified · Sample</span></div>
    </div>
  </div>
</section>

<div class="proof"><div class="wrap"><div class="proof-card reveal">
  <div class="proof-item">{icon("lock")}<div><strong>Exclusive</strong><span>One contractor per lead, never resold</span></div></div>
  <div class="proof-item">{icon("phone")}<div><strong>Phone-verified</strong><span>Checked before it reaches you</span></div></div>
  <div class="proof-item">{icon("map")}<div><strong>Your ZIP codes</strong><span>You choose the area and job types</span></div></div>
  <div class="proof-item">{icon("calendar")}<div><strong>Month to month</strong><span>No setup fee, pause any time</span></div></div>
</div></div></div>

<section class="section"><div class="wrap">
  <div class="section-head reveal">{eyebrow("02", "What we do")}
    <h2>Drainage and irrigation <span class="accent">leads only.</span></h2>
    <p>We don't sell roofing, plumbing or painting leads. Our ads, landing pages and screening questions are written for homeowners with drainage and irrigation problems, so each request arrives with the details you need to quote.</p></div>
  <div class="grid-2">
    <article class="vertical drain reveal">
      {lines()}
      <span class="tag navy" style="align-self:flex-start;background:rgba(255,255,255,.1);margin-bottom:20px">{icon("drop")} Drainage</span>
      <h3>Drainage leads</h3>
      <p>Homeowners with standing water, erosion or a wet basement. These are larger jobs, and demand rises after heavy rain.</p>
      <ul>{"".join(f"<li>{icon('check')}{j}</li>" for j in ["French drains", "Regrading", "Downspouts", "Sump pumps", "Dry wells", "Channel drains"])}</ul>
      <div class="foot"><div><small>Typical job size*</small><strong>$2.5k – $12k+</strong></div><a class="btn btn-white" href="/drainage-leads.html">Drainage leads {icon("arrow")}</a></div>
    </article>
    <article class="vertical irr reveal d1">
      {lines()}
      <span class="tag" style="align-self:flex-start;background:rgba(255,255,255,.16);color:#fff;margin-bottom:20px">{icon("sprinkler")} Irrigation</span>
      <h3>Irrigation leads</h3>
      <p>New systems, repairs and water-saving upgrades, plus start-ups and winterizations that bring the same customer back every year.</p>
      <ul>{"".join(f"<li>{icon('check')}{j}</li>" for j in ["Sprinkler installs", "Repairs", "Drip systems", "Smart controllers", "Backflow", "Winterization"])}</ul>
      <div class="foot"><div><small>Typical job size*</small><strong>$250 – $8k+</strong></div><a class="btn btn-white" href="/irrigation-leads.html">Irrigation leads {icon("arrow")}</a></div>
    </article>
  </div>
  <p class="fine">*Broad ranges seen across many U.S. markets. Your prices depend on region, site conditions and scope.</p>
</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="section-head reveal">{eyebrow("03", "Why Launch")}
    <h2>Why contractors switch <span class="accent">from shared leads.</span></h2>
    <p>On shared-lead marketplaces the same request often goes to several companies at once, and the lowest bid tends to win. Our leads go to one contractor, so you compete on your quote and your service.</p></div>
  {compare_table()}
  <p style="margin-top:22px"><a class="link-arrow" href="/blog/exclusive-vs-shared-leads.html">Compare cost per job: exclusive vs. shared leads {icon("arrow")}</a></p>
</div></section>

<section class="section section-navy on-navy"><div class="wrap">
  <div class="head-row">
    <div class="section-head reveal">{eyebrow("04", "How it works")}
      <h2>Live in your area <span class="accent">in about a week.</span></h2>
      <p>We handle the ads, landing pages, screening and delivery. You call the homeowner and quote the job.</p></div>
    <a class="btn btn-outline reveal" href="/how-it-works.html">How it works {icon("arrow")}</a>
  </div>
  {steps_block()}
</div></section>

<section class="section"><div class="wrap split">
  {sample_lead()}
  <div class="reveal d1">
    {eyebrow("05", "What you receive")}
    <h2>What's in <span class="accent">every lead.</span></h2>
    <p class="big">Each lead includes the details your estimator needs to qualify the job and book a site visit on the first call.</p>
    <ul class="checklist">
      <li>{icon("check")}<div><strong>The problem</strong><span>Described by the homeowner, with photos when they have them.</span></div></li>
      <li>{icon("check")}<div><strong>Verified phone and ownership</strong><span>Renters and out-of-area requests are filtered out.</span></div></li>
      <li>{icon("check")}<div><strong>Timeline and size</strong><span>When they want the work done, the rough scope, and whether they have other quotes.</span></div></li>
    </ul>
    <a class="link-arrow" href="/blog/qualify-drainage-leads.html">How to qualify a drainage lead on the first call {icon("arrow")}</a>
  </div>
</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="section-head center reveal">{eyebrow("06", "Estimate your return")}
    <h2>What leads could be worth <span class="accent">to your business.</span></h2>
    <p>Enter your close rate and average job value to see monthly lead spend, jobs closed and revenue.</p></div>
  {calculator()}
</div></section>

<section class="section"><div class="wrap split">
  <div class="reveal">
    {eyebrow("07", "Seasonality")}
    <h2>Drainage and irrigation <span class="accent">peak at different times.</span></h2>
    <p class="big">Drainage requests rise with spring thaw and fall storms. Irrigation is busiest from spring start-ups through summer repairs. Contractors who offer both keep crews busy for more of the year.</p>
    <a class="link-arrow" href="/blog/drainage-demand-calendar.html">Month-by-month drainage demand {icon("arrow")}</a>
  </div>
  {season_chart("Illustrative shape only. Timing shifts with climate: earlier in the South, later in the North.")}
</div></section>

<section class="section" style="padding-top:0"><div class="wrap">{banner()}</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="head-row">
    <div class="section-head reveal">{eyebrow("08", "Guides")}
      <h2>Guides for drainage and <span class="accent">irrigation owners.</span></h2>
      <p>Pricing, qualifying calls, seasonal planning and maintenance plans.</p></div>
    <a class="btn btn-outline reveal" href="/blog/">All articles {icon("arrow")}</a>
  </div>
  <div class="posts">{latest}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head center reveal">{eyebrow("09", "FAQ")}<h2>Common questions</h2></div>
  {faq(home_faq)}
</div></section>

{cta_band()}
"""
    schema = [{"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": DOMAIN, "email": EMAIL,
               "logo": f"{DOMAIN}/assets/apple-touch-icon.png",
               "description": "Exclusive drainage and irrigation lead generation for contractors."}, faq_schema(home_faq)]
    page("index.html", "Exclusive Drainage & Irrigation Leads for Contractors | Launch Lead Gen",
         "Exclusive, phone-verified drainage and irrigation leads in your ZIP codes. One contractor per lead, pay per lead, month to month.",
         body, "/", schema=schema)


def service_page(kind, posts):
    if kind == "drainage":
        slug, title, ic = "drainage-leads.html", "Drainage Leads", "drop"
        h1 = 'Exclusive drainage leads <span class="accent">in your ZIP codes.</span>'
        lede = "Requests for French drains, regrading, downspouts, sump pumps and dry wells from homeowners in your area. Each lead goes to you only and arrives within a minute."
        jobs = [
            ("pipe", "French drain installation", "Backyard pooling, wet lawns and runoff toward the house. Usually the largest drainage job we send."),
            ("wave", "Yard grading &amp; regrading", "Negative slope, low spots and erosion. Often bundled with drains or downspout work."),
            ("drop", "Downspout &amp; gutter drainage", "Buried extensions, pop-up emitters and tie-ins. Smaller jobs that often lead to larger ones."),
            ("pump", "Sump pumps &amp; basement drainage", "Wet basements, failed pumps and interior drains. Usually urgent, especially after storms."),
            ("layers", "Dry wells &amp; catch basins", "Common on clay soils and small lots where water has nowhere to drain."),
            ("grid", "Channel &amp; trench drains", "Driveways, patios and garage entries that flood every time it rains."),
        ]
        qa = [
            ("Do you send foundation repair or waterproofing leads?", "We focus on exterior and basement drainage. If a homeowner mentions structural cracks or major waterproofing, we flag it in the lead so you can decide whether to take it or refer it."),
            ("Can I exclude certain job types?", "Yes. Many crews skip sump pumps or interior drains. Choose the drainage jobs you want and we only advertise for and send those."),
            ("What happens after a big storm?", "Drainage requests usually rise after heavy rain. Your weekly cap keeps volume at what your crews can handle, and we can raise it for a few weeks if you want more."),
            ("How do you verify drainage leads?", "Every phone number is verified, the address is checked against your territory, and the homeowner answers questions about the problem, the timeline and whether they own the home."),
        ]
        season = "Drainage requests usually build with spring thaw and rain, ease in midsummer, then rise again with fall storms."
        cat = "Drainage"
    else:
        slug, title, ic = "irrigation-leads.html", "Irrigation Leads", "sprinkler"
        h1 = 'Exclusive irrigation leads <span class="accent">in your ZIP codes.</span>'
        lede = "Requests for new sprinkler systems, repairs, drip conversions, smart controllers and seasonal service from homeowners in your area. Each lead goes to you only."
        jobs = [
            ("sprinkler", "New sprinkler system installs", "New builds, new sod and homeowners replacing hoses. The largest irrigation job we send."),
            ("tool", "Sprinkler &amp; irrigation repair", "Broken heads, leaks, dry zones and low pressure. Quick to close and a good way to sign up service-plan customers."),
            ("drop", "Drip irrigation &amp; conversions", "Beds, gardens and water-wise landscapes. Popular wherever watering limits apply."),
            ("wifi", "Smart controller upgrades", "Weather-based controllers and Wi-Fi timers. Many local utilities offer rebates."),
            ("shield", "Backflow testing &amp; repair", "Annual testing where required, plus device repairs. Recurring by nature."),
            ("snow", "Spring start-ups &amp; winterization", "Seasonal service calls that turn into repeat customers every year."),
        ]
        qa = [
            ("Do you send commercial irrigation leads?", "Our campaigns target homeowners. Occasionally a small commercial or HOA request comes through; we label it clearly and you can opt in or out."),
            ("Can I get only repair leads, or only installs?", "Yes. Choose installs, repairs, seasonal service or any combination. Many companies start with repairs because they close quickly and lead to service plans."),
            ("Will I get leads in winter?", "Irrigation slows in the off-season in colder climates. That's why many contractors pair irrigation with drainage, which picks up with fall and late-winter rain."),
            ("How do you verify irrigation leads?", "Every phone number is verified, the address is checked against your territory, and the homeowner tells us what they need, the system size and their timeline."),
        ]
        season = "Irrigation requests usually rise with spring start-ups, stay steady through summer repairs, and finish with fall winterizations."
        cat = "Irrigation"

    cards = "".join(f'<article class="card reveal d{n % 3}"><div class="ic">{icon(i)}</div><h3>{t}</h3><p>{d}</p></article>'
                    for n, (i, t, d) in enumerate(jobs))
    related = [p for p in posts if p["category"] == cat][:2] + [p for p in posts if p["category"] == "Lead Strategy"][:1]
    rel = "".join(post_card(p, cls=f"reveal d{n}") for n, p in enumerate(related))
    other = ("irrigation", "/irrigation-leads.html", "Irrigation leads") if kind == "drainage" else ("drainage", "/drainage-leads.html", "Drainage leads")
    body = f"""
<section class="page-hero on-navy">
  {lines()}
  <div class="wrap page-hero-grid">
    <div class="reveal">
      <div class="crumbs"><a href="/">Home</a> / {title}</div>
      {eyebrow("→", title)}
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <div class="hero-ctas" style="margin-bottom:28px">
        <a class="btn btn-primary btn-lg" href="/contact.html?service={kind}">Check my area {icon("arrow")}</a>
        <a class="btn btn-outline btn-lg" href="/pricing.html">See pricing</a>
      </div>
      <ul class="check-row"><li>{icon("check")}Exclusive</li><li>{icon("check")}Phone-verified</li><li>{icon("check")}Month to month</li></ul>
    </div>
    <div class="reveal d2">{sample_lead(kind)}</div>
  </div>
</section>

<section class="section" id="jobs"><div class="wrap">
  <div class="section-head reveal">{eyebrow("01", "Job types")}
    <h2>Choose the {kind} jobs <span class="accent">you want.</span></h2>
    <p>Turn each job type on or off. We only advertise for, screen and send the work that fits your crews and equipment.</p></div>
  <div class="grid-3">{cards}</div>
</div></section>

<section class="section section-ice"><div class="wrap split">
  <div class="reveal">
    {eyebrow("02", "Lead quality")}
    <h2>What every lead <span class="accent">has to pass.</span></h2>
    <ul class="checklist">
      <li>{icon("check")}<div><strong>Inside your territory</strong><span>Address checked against the ZIP codes you chose.</span></div></li>
      <li>{icon("check")}<div><strong>Verified phone number</strong><span>No fake numbers, no bots, no test submissions.</span></div></li>
      <li>{icon("check")}<div><strong>Owner or decision-maker</strong><span>Renters without authority are filtered out.</span></div></li>
      <li>{icon("check")}<div><strong>A specific job and timeline</strong><span>The homeowner has described the problem and when they want it fixed.</span></div></li>
    </ul>
  </div>
  <div class="card reveal d1" style="padding:36px">
    <div class="ic">{icon("refresh")}</div>
    <h3>Bad-lead credit policy</h3>
    <p>If a lead slips through with a wrong number, a duplicate, a renter or an out-of-area address, flag it from the notification. We review it within one business day and credit it back.</p>
  </div>
</div></section>

<section class="section"><div class="wrap split">
  <div class="reveal">
    {eyebrow("03", "Seasonality")}
    <h2>When {kind} <span class="accent">demand peaks.</span></h2>
    <p class="big">{season}</p>
  </div>
  {season_chart("Relative demand by month.")}
</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="section-head center reveal">{eyebrow("04", "Estimate your return")}<h2>What {kind} leads could <span class="accent">be worth to you.</span></h2></div>
  {calculator(kind)}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head reveal">{eyebrow("05", "Guides")}<h2>Guides for {kind} contractors</h2></div>
  <div class="posts">{rel}</div>
</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="section-head center reveal">{eyebrow("06", "FAQ")}<h2>{title}: common questions</h2></div>
  {faq(qa)}
  <p style="text-align:center;margin-top:32px">Also run {other[0]}? <a class="link-arrow" href="{other[1]}">See {other[2]} {icon("arrow")}</a></p>
</div></section>

{cta_band()}
"""
    page(slug, f"Exclusive {title} for Contractors | {BRAND}",
         f"Exclusive, verified {kind} leads for contractors. Choose your ZIP codes and job types; leads arrive by text, email and CRM within a minute.",
         body, "/" + slug, schema=faq_schema(qa))


def build_how():
    quality = [
        ("shield", "Phone verification", "Every number is checked before the lead is sent. Disconnected and fake numbers never reach you."),
        ("map", "Territory matching", "Addresses are matched to your ZIP codes. Out-of-area requests are dropped, not dumped on you."),
        ("home", "Ownership screening", "We ask whether they own the home or can approve the work."),
        ("target", "Job details", "Problem, scope, timeline and photos, so you know whether it's a small repair or a full drain system before you call."),
        ("lock", "One contractor only", "We never resell or split a lead."),
        ("refresh", "Credits for bad leads", "Wrong numbers, duplicates, renters and out-of-area addresses are credited after review."),
    ]
    qcards = "".join(f'<article class="card reveal d{n % 3}"><div class="ic">{icon(i)}</div><h3>{t}</h3><p>{d}</p></article>' for n, (i, t, d) in enumerate(quality))
    onboarding = [
        ("Day 1", "Strategy call", "We map your ZIP codes, job types, crew capacity, average ticket and the jobs you don't want."),
        ("Days 2–4", "Setup", "We build your landing pages, campaigns and screening questions, and route leads to your phone, inbox and CRM."),
        ("Days 5–7", "Go live", "Campaigns launch with a weekly lead cap you control."),
        ("Ongoing", "Adjust", "Tell us which leads closed. We move budget toward the ZIP codes and job types that pay best."),
    ]
    tl = "".join(f'<div class="card reveal d{n}"><span class="num">{d.upper()}</span><h3>{t}</h3><p>{x}</p></div>' for n, (d, t, x) in enumerate(onboarding))
    body = f"""
<section class="page-hero on-navy">
  {lines()}
  <div class="wrap reveal">
    <div class="crumbs"><a href="/">Home</a> / How it works</div>
    {eyebrow("→", "How it works")}
    <h1>How Launch Lead Gen <span class="accent">works.</span></h1>
    <p class="lede">We run local ad campaigns for your service area, screen every homeowner request, and send the ones that qualify to you within a minute.</p>
    <a class="btn btn-primary btn-lg" href="/contact.html">Talk to Launch {icon("arrow")}</a>
  </div>
</section>

<section class="section section-navy on-navy" style="padding-top:0"><div class="wrap">{steps_block()}</div></section>

<section class="section" id="quality"><div class="wrap">
  <div class="section-head reveal">{eyebrow("01", "Lead quality")}
    <h2>Six checks on <span class="accent">every lead.</span></h2>
    <p>A request has to pass all six before we send it to you.</p></div>
  <div class="grid-3">{qcards}</div>
</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="section-head reveal">{eyebrow("02", "Onboarding")}<h2>Live in <span class="accent">about a week.</span></h2></div>
  <div class="grid-4">{tl}</div>
</div></section>

<section class="section"><div class="wrap split">
  <div class="reveal">
    {eyebrow("03", "Delivery")}
    <h2>Delivered to <span class="accent">your phone and CRM.</span></h2>
    <p class="big">Leads are sent the moment they pass screening, so whoever is on call can phone the homeowner right away.</p>
    <ul class="checklist">
      <li>{icon("phone")}<div><strong>Text alerts</strong><span>To one phone or a rotation across your sales team.</span></div></li>
      <li>{icon("mail")}<div><strong>Email with full details</strong><span>Easy to forward to an estimator or office manager.</span></div></li>
      <li>{icon("layers")}<div><strong>CRM posting</strong><span>Connect the field-service or CRM tool you already use, by native integration or webhook where available.</span></div></li>
      <li>{icon("chart")}<div><strong>Close-loop reporting</strong><span>Mark leads booked, sold or lost so we can tune toward your best jobs.</span></div></li>
    </ul>
  </div>
  {sample_lead()}
</div></section>

<section class="section" style="padding-top:0"><div class="wrap">{banner()}</div></section>

{cta_band()}
"""
    page("how-it-works.html", f"How It Works | {BRAND}",
         "How Launch Lead Gen finds, verifies and delivers exclusive drainage and irrigation leads to contractors. Live in about a week.",
         body, "/how-it-works.html")


def build_pricing():
    def li(items):
        return "".join(f"<li>{icon('check')}<span>{x}</span></li>" for x in items)
    plans = f"""
<div class="plans">
  <article class="plan reveal">
    <h3>Launch</h3><p>For owner-operators adding a steady stream of jobs.</p>
    <div class="price"><span data-price data-drainage="$89" data-irrigation="$69">$89</span><small> / lead</small></div>
    <p class="price-note">Starting price · 10–20 leads / month</p>
    <ul>{li(["One lead type: drainage <em>or</em> irrigation", "Up to 5 ZIP codes", "Text + email delivery", "Weekly lead cap you control", "Bad-lead credits"])}</ul>
    <a class="btn btn-outline btn-block" href="/contact.html?plan=launch">Start with Launch</a>
  </article>
  <article class="plan featured reveal d1">
    <span class="tag orange flag">Most popular</span>
    <h3>Growth</h3><p>For multi-crew companies that want both seasons covered.</p>
    <div class="price"><span data-price data-drainage="$79" data-irrigation="$59">$79</span><small> / lead</small></div>
    <p class="price-note">Starting price · 20–60 leads / month</p>
    <ul>{li(["Drainage <em>and</em> irrigation", "Up to 15 ZIP codes", "CRM posting + team rotation", "Monthly close-rate review", "Priority storm-surge volume", "Bad-lead credits"])}</ul>
    <a class="btn btn-primary btn-block" href="/contact.html?plan=growth">Choose Growth {icon("arrow")}</a>
  </article>
  <article class="plan reveal d2">
    <h3>Territory Lock</h3><p>Exclusive rights to your ZIP codes. No other contractor can buy leads there.</p>
    <div class="price">Custom</div>
    <p class="price-note">Monthly territory fee + reduced per-lead rate</p>
    <ul>{li(["Exclusive ZIP code lockout", "All 14 job types available", "Dedicated campaign manager", "Landing pages with your brand", "Quarterly expansion plan"])}</ul>
    <a class="btn btn-navy btn-block" href="/contact.html?plan=territory">Talk about Territory Lock</a>
  </article>
</div>"""
    pfaq = [
        ("Why does the price change by market?", "Lead cost depends on local competition, population density and the job types you pick. We quote your exact per-lead rate after we look at your ZIP codes. The prices above are starting points."),
        ("Is there a setup fee or contract?", "No setup fee on Launch and Growth, and plans are month to month. Territory Lock has a monthly territory fee because we stop selling those ZIP codes to anyone else."),
        ("How do I pay?", "Pre-fund a lead balance or pay a monthly invoice, whichever suits your cash flow. You're only billed for leads that pass our filters."),
        ("Can I pause during the off-season?", "Yes. Pause or lower your weekly cap any time. Many irrigation contractors in colder regions pause in winter or shift budget to drainage."),
        ("What does a bad-lead credit cover?", "Wrong or disconnected numbers, duplicates, renters without authority and addresses outside your territory. Flag it from the notification and we review it within one business day."),
    ]
    body = f"""
<section class="page-hero on-navy">
  {lines()}
  <div class="wrap reveal" style="text-align:center">
    {eyebrow("→", "Pricing")}
    <h1 style="margin-inline:auto">Simple <span class="accent">per-lead pricing.</span></h1>
    <p class="lede" style="margin-inline:auto">No setup fee and no long-term contract. Your exact rate depends on your market and the jobs you choose.</p>
  </div>
</section>
<section class="section section-ice"><div class="wrap">
  <div class="price-switch"><div class="seg" role="group" aria-label="Lead type" data-price-toggle>
    <button type="button" data-mode="drainage" aria-pressed="true">Drainage leads</button>
    <button type="button" data-mode="irrigation" aria-pressed="false">Irrigation leads</button>
  </div></div>
  {plans}
  <p class="fine" style="text-align:center;margin-top:28px">Starting prices shown. Your final per-lead rate is confirmed after a territory review and depends on location, competition and job types.</p>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head center reveal">{eyebrow("01", "Estimate your return")}<h2>See what your numbers <span class="accent">look like.</span></h2></div>
  {calculator()}
</div></section>

<section class="section section-ice"><div class="wrap">
  <div class="section-head center reveal">{eyebrow("02", "FAQ")}<h2>Pricing questions</h2></div>
  {faq(pfaq)}
</div></section>
{cta_band()}
"""
    page("pricing.html", f"Pricing: Drainage & Irrigation Leads | {BRAND}",
         "Simple per-lead pricing for exclusive drainage and irrigation leads. No setup fees, month to month, bad-lead credits.",
         body, "/pricing.html", schema=faq_schema(pfaq))


def build_contact():
    def choice(v, l):
        return f'<label class="choice"><input type="checkbox" name="services" value="{v}">{l}</label>'
    body = f"""
<section class="page-hero on-navy">
  {lines()}
  <div class="wrap page-hero-grid" style="align-items:start">
    <div class="reveal">
      <div class="crumbs"><a href="/">Home</a> / Talk to Launch</div>
      {eyebrow("→", "Talk to Launch")}
      <h1>Check if your area <span class="accent">is open.</span></h1>
      <p class="lede">We work with a limited number of contractors in each market. Tell us where you work and which jobs you want, and we'll reply within one business day with availability and pricing.</p>
      <ul class="checklist">
        <li>{icon("check")}<div><strong>Territory check</strong><span>We confirm which of your ZIP codes are open.</span></div></li>
        <li>{icon("check")}<div><strong>Lead estimate</strong><span>Expected volume and per-lead pricing for your area.</span></div></li>
        <li>{icon("check")}<div><strong>A short call</strong><span>About 20 minutes. If we're not a fit for your area, we'll say so.</span></div></li>
      </ul>
      <p>Prefer to talk? Call <a style="color:#fff;font-weight:700" href="{PHONE_HREF}">{PHONE}</a> or email <a style="color:#fff" href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </div>
    <form class="form-card reveal d1" id="territory" data-contact data-endpoint="/api/inquiry" novalidate>
      <h2>Check my area</h2>
      <div class="field-row">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name"><span class="err"></span></div>
        <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization"><span class="err"></span></div>
      </div>
      <div class="field-row">
        <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email"><span class="err"></span></div>
        <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"><span class="err"></span></div>
      </div>
      <fieldset class="field services-field"><legend>Lead types you want</legend>
        <div class="choice-grid">{choice("drainage", "Drainage")}{choice("irrigation", "Irrigation")}</div><span class="err"></span>
      </fieldset>
      <div class="field"><label for="f-zips">ZIP codes you serve</label><input id="f-zips" name="zips" placeholder="37064, 37067, 37027"><span class="err"></span></div>
      <div class="field-row">
        <div class="field"><label for="f-plan">Plan interest</label><select id="f-plan" name="plan"><option value="">Not sure yet</option><option value="launch">Launch</option><option value="growth">Growth</option><option value="territory">Territory Lock</option></select></div>
        <div class="field"><label for="f-vol">Leads per month</label><select id="f-vol" name="volume"><option>10–20</option><option>20–40</option><option>40–60</option><option>60+</option></select></div>
      </div>
      <div class="field"><label for="f-msg">Anything else? <span style="font-weight:500;color:var(--muted)">(optional)</span></label><textarea id="f-msg" name="message" placeholder="Crew size, jobs you don't want, current lead sources…"></textarea></div>
      <div class="hp" aria-hidden="true"><label for="f-website">Website</label><input id="f-website" name="website" tabindex="-1" autocomplete="off"></div>
      <label class="check-consent"><input type="checkbox" name="smsConsent"><span>I consent to receive SMS notifications, alerts and occasional marketing messages from {BRAND}. Message frequency varies. Message and data rates may apply. Reply STOP to unsubscribe at any time. (Optional)</span></label>
      <button class="btn btn-primary btn-lg btn-block" type="submit">Check my area {icon("arrow")}</button>
      <div class="form-status" role="status" aria-live="polite"></div>
      <p class="consent">We'll use your details to reply to this request. See our <a href="/privacy.html">Privacy Policy</a>.</p>
    </form>
  </div>
</section>
"""
    page("contact.html", f"Talk to Launch | {BRAND}",
         "Check whether exclusive drainage and irrigation leads are available in your ZIP codes. Get a lead estimate and launch plan within one business day.",
         body, "/contact.html")


def build_blog(posts):
    cats = ["all"] + sorted({p["category"] for p in posts})
    filt = "".join(f'<button type="button" data-cat="{c}" aria-pressed="{str(c == "all").lower()}">{"All articles" if c == "all" else c}</button>' for c in cats)
    feature = post_card(posts[0], feature=True, cls="reveal")
    rest = "".join(post_card(p) for p in posts[1:])
    body = f"""
<section class="page-hero on-navy">
  {lines()}
  <div class="wrap reveal">
    {eyebrow("→", "Guides")}
    <h1>Guides for drainage and <span class="accent">irrigation contractors.</span></h1>
    <p class="lede">Pricing, phone scripts, seasonal planning and maintenance plans for owners and estimators.</p>
  </div>
</section>
<section class="section"><div class="wrap">
  <div class="filters" role="group" aria-label="Filter articles" data-filters>{filt}</div>
  {feature}
  <div class="posts">{rest}</div>
</div></section>
{cta_band()}
"""
    page("blog/index.html", f"Guides for Drainage & Irrigation Contractors | {BRAND}",
         "Practical guides for drainage and irrigation contractors: pricing French drains, qualifying leads, seasonal planning, maintenance plans and lead strategy.",
         body, "/blog/")

    for p in posts:
        toc = []

        def add_id(m):
            text = m.group(1)
            sid = slugify(text)
            toc.append((sid, re.sub("<[^>]+>", "", text)))
            return f'<h2 id="{sid}">{text}</h2>'
        body_html = re.sub(r"<h2>(.*?)</h2>", add_id, p["body"])
        toc_html = "".join(f'<li><a href="#{sid}">{esc(html.unescape(t))}</a></li>' for sid, t in toc)
        related = [x for x in posts if x["slug"] != p["slug"] and x["category"] == p["category"]]
        related += [x for x in posts if x["slug"] != p["slug"] and x not in related]
        rel = "".join(post_card(x) for x in related[:3])
        svc = "irrigation" if p["category"] == "Irrigation" else "drainage"
        schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
                  "datePublished": p["date"], "author": {"@type": "Organization", "name": BRAND},
                  "publisher": {"@type": "Organization", "name": BRAND}, "image": OG_IMAGE,
                  "mainEntityOfPage": f"{DOMAIN}/blog/{p['slug']}"}
        body = f"""
<div class="progress" aria-hidden="true"></div>
<section class="page-hero article-hero on-navy">
  {lines()}
  <div class="wrap">
    <div class="crumbs"><a href="/">Home</a> / <a href="/blog/">Guides</a> / {esc(p['category'])}</div>
    <h1>{esc(p['title'])}</h1>
    <p class="dek">{esc(p['excerpt'])}</p>
    <div class="article-meta"><span class="tag navy" style="background:var(--blue)">{esc(p['category'])}</span><span>{nice_date(p['date'])}</span><span>·</span><span>{esc(p['readTime'])}</span><span>·</span><span>By the {BRAND} team</span></div>
  </div>
</section>
<section class="section" style="padding-top:56px"><div class="wrap article-layout">
  <article class="prose">{body_html}</article>
  <aside class="aside-sticky">
    <nav class="toc" aria-label="On this page"><h4>On this page</h4><ol>{toc_html}</ol></nav>
    <div class="aside-cta on-navy"><h4>Get {svc} leads in your area</h4><p>Exclusive, phone-verified, one contractor per lead.</p><a class="btn btn-primary btn-block" href="/contact.html?service={svc}">Talk to Launch {icon("arrow")}</a></div>
  </aside>
</div></section>
<section class="section section-ice"><div class="wrap">
  <div class="section-head">{eyebrow("→", "Guides")}<h2>More guides</h2></div>
  <div class="posts">{rel}</div>
</div></section>
"""
        page(f"blog/{p['slug']}.html", f"{p['title']} | {BRAND}", p["description"], body, "/blog/", schema=schema)


def legal_page(path, title, updated, sections):
    secs = "".join(f"<h2>{h}</h2>{b}" for h, b in sections)
    body = f"""
<section class="page-hero on-navy">{lines()}<div class="wrap"><div class="crumbs"><a href="/">Home</a> / {title}</div><h1>{title}</h1><p class="lede">Last updated {updated}</p></div></section>
<section class="section"><div class="wrap"><div class="prose legal">{secs}</div></div></section>
"""
    page(path, f"{title} | {BRAND}", f"{BRAND} {title.lower()}.", body)


def build_legal():
    updated = LEGAL_UPDATED
    legal_page("privacy.html", "Privacy Policy", updated, [
        ("What we collect", f"<p>When you use the forms on this site we collect what you enter: your name, company, email, phone number, the ZIP codes you serve, the lead types and plan you're interested in, and any message. Like most websites, our hosting provider may log basic technical data such as your IP address and browser type.</p>"),
        ("How we use it", "<p>We use your details to respond to your request, check territory availability, prepare a quote and, if you become a client, deliver and support the service. We may contact you by phone, text or email about your request. You can opt out of texts by replying STOP, and out of emails using the link in any message.</p>"),
        ("Sharing", "<p>We share your details only with service providers that help us run the business (for example email, CRM and hosting providers) and when required by law. We do not sell the contact details you submit through this site.</p>"),
        ("Third-party services", "<p>This site loads fonts from Google Fonts, which receives your IP address when the page loads. If we add analytics or advertising tools, we'll list them here.</p>"),
        ("Your choices", f"<p>To access, correct or delete the information you've sent us, email <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p>"),
        ("Changes", "<p>We'll post any updates to this policy on this page with a new date.</p>"),
    ])
    legal_page("terms.html", "Terms of Use", updated, [
        ("Using this site", f"<p>This website describes the services offered by {BRAND}. By using it you agree to these terms. If you don't agree, please don't use the site.</p>"),
        ("Information on this site", "<p>Prices on this site are starting points. Your actual rate, lead volume and terms are set in a written agreement after a territory review. Calculator results and articles are estimates and general guidance, not guarantees of results.</p>"),
        ("Service agreements", "<p>Lead delivery, billing, credits and cancellation are governed by the agreement you sign with us, which takes priority over anything on this site.</p>"),
        ("Content", f"<p>The text, design and graphics on this site belong to {BRAND}. You're welcome to share links to our articles; please don't republish them in full without permission.</p>"),
        ("Liability", "<p>The site is provided as is. To the extent the law allows, we aren't liable for losses arising from use of the site or reliance on its content.</p>"),
        ("Contact", f"<p>Questions about these terms: <a href=\"mailto:{EMAIL}\">{EMAIL}</a>.</p>"),
    ])


def build_404():
    body = f"""<section class="page-hero on-navy" style="min-height:62vh;display:grid;align-items:center">{lines()}
<div class="wrap">{eyebrow("404", "Page not found")}<h1>Page not found</h1>
<p class="lede">This page doesn't exist or has moved.</p>
<div class="hero-ctas"><a class="btn btn-primary" href="/">Home {icon("arrow")}</a><a class="btn btn-outline" href="/blog/">Guides</a></div></div></section>"""
    page("404.html", f"Page not found | {BRAND}", "Page not found.", body, noindex=True)


def write_favicon():
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#102A43"/>'
           f'<g transform="translate(6 12) scale(.56)" fill="#1268E8"><polygon points="{MARK_LEFT}"/><polygon points="{MARK_RIGHT}"/></g></svg>')
    (OUT / "assets" / "favicon.svg").write_text(svg)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    write_favicon()
    shutil.copy(SRC / "headers.txt", OUT / "_headers")
    posts = load_posts()
    build_home(posts)
    service_page("drainage", posts)
    service_page("irrigation", posts)
    build_how()
    build_pricing()
    build_contact()
    build_blog(posts)
    build_legal()
    build_404()
    urls = "".join(f"<url><loc>{DOMAIN}{clean_url(p)}</loc></url>" for p, noindex in PAGES if not noindex)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
