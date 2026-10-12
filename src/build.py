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
EMAIL = "hello@launchleadgen.io"
YEAR = date.today().year

# ---------------------------------------------------------------- icons
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
    "refresh": '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7l10-5z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "home": '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "wave": '<path d="M2 12c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 17c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 7c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/>',
    "pipe": '<path d="M3 7h10a4 4 0 0 1 4 4v10"/><path d="M3 11h8a2 2 0 0 1 2 2v8"/><path d="M3 5v8M15 21h4"/>',
    "pump": '<rect x="6" y="9" width="12" height="13" rx="2"/><path d="M12 9V3h5"/><path d="M10 14h4"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "wifi": '<path d="M5 12.5a10 10 0 0 1 14 0"/><path d="M8.5 16a5 5 0 0 1 7 0"/><path d="M12 19.5h.01"/><path d="M2 9a15 15 0 0 1 20 0"/>',
    "snow": '<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/>',
    "tool": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5V21h16"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


BRAND_MARK = """<svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="bm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5cc8e6"/><stop offset="1" stop-color="#b8f35a"/></linearGradient></defs><rect width="40" height="40" rx="11" fill="#0f5e6e"/><path d="M20 7s9 9.4 9 16a9 9 0 0 1-18 0c0-6.6 9-16 9-16z" fill="url(#bm)"/><path d="M15.5 25.5 20 21l4.5 4.5M20 21v9" fill="none" stroke="#0a1a24" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

WAVE = '<svg class="hero-wave{cls}" viewBox="0 0 1440 70" preserveAspectRatio="none" aria-hidden="true"><path fill="currentColor" d="M0 40c160-30 320-30 480 0s320 30 480 0 320-30 480 0v30H0z"/></svg>'

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
    links = "".join(
        f'<li><a href="{href}"{current if href == active else ""}>{label}</a></li>'
        for href, label in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header on-dark">
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="/" aria-label="{BRAND} home">{BRAND_MARK}<span>Launch<b>LeadGen</b></span></a>
    <ul class="nav-links" id="nav-links">{links}</ul>
    <div class="nav-cta">
      <a class="btn btn-ghost" href="/contact.html">Talk to us</a>
      <a class="btn btn-primary" href="/contact.html#territory">Check my territory</a>
      <button class="menu-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav-links"><span></span><span></span><span></span></button>
    </div>
  </nav>
</header>"""


FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="/">{BRAND_MARK}<span>Launch<b>LeadGen</b></span></a>
        <p style="margin-top:18px;max-width:340px">Exclusive, verified homeowner leads for drainage and irrigation contractors. Built for crews that want booked jobs, not bidding wars.</p>
        <form class="footer-news" data-news>
          <label class="sr-only" for="news-email">Email</label>
          <input id="news-email" type="email" placeholder="Monthly contractor playbook" required>
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
          <li><a href="/how-it-works.html#quality">Lead quality promise</a></li>
          <li><a href="/contact.html">Contact</a></li>
          <li><a href="/contact.html#territory">Check territory</a></li>
        </ul>
      </div>
      <div>
        <h4>Resources</h4>
        <ul>
          <li><a href="/blog/">Contractor blog</a></li>
          <li><a href="/blog/price-french-drain-jobs.html">Pricing drainage jobs</a></li>
          <li><a href="/blog/irrigation-recurring-revenue.html">Recurring irrigation revenue</a></li>
          <li><a href="/blog/exclusive-vs-shared-leads.html">Exclusive vs. shared leads</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      <span>&copy; {YEAR} {BRAND}. All rights reserved.</span>
      <span>Drainage &amp; irrigation lead generation for contractors in the U.S.</span>
    </div>
  </div>
</footer>
<div class="mobile-cta"><a class="btn btn-primary" href="/contact.html#territory">Check my territory</a></div>"""


def page(path, title, desc, body, active="", extra_head="", schema=None):
    canonical = DOMAIN + ("/" if path == "index.html" else "/" + path.replace("index.html", ""))
    ld = f'<script type="application/ld+json">{json.dumps(schema)}</script>' if schema else ""
    doc = f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#071c25">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,650;12..96,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
{extra_head}{ld}
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
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    PAGES.append(path)


PAGES = []

# ---------------------------------------------------------------- shared blocks
JOB_TYPES = ["French drains", "Yard regrading", "Downspout extensions", "Sump pumps", "Dry wells",
             "Channel drains", "Foundation drainage", "Sprinkler installs", "Irrigation repair",
             "Drip systems", "Smart controllers", "Backflow testing", "Spring start-ups", "Winterization"]


def marquee():
    items = "".join(f"<span>{j}</span>" for j in JOB_TYPES)
    dupe = "".join(f'<span aria-hidden="true">{j}</span>' for j in JOB_TYPES)
    return f'<div class="marquee" aria-label="Lead types we generate"><div class="marquee-track">{items}{dupe}</div></div>'


def faq(items):
    out = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f'<div class="faq">{out}</div>'


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}}
        for q, a in items]}


def cta_band(title="Your ZIP codes might still be open.",
             text="We cap how many contractors we work with in each market, so the leads you get are yours alone. Check your territory in 10 seconds."):
    return f"""<section class="section"><div class="wrap">
  <div class="cta-band reveal" id="territory-check">
    <div>
      <span class="eyebrow" style="color:var(--lime)">Limited territories</span>
      <h2>{title}</h2>
      <p>{text}</p>
      <ul class="hero-proof">
        <li>{icon("check")}No long-term contract</li>
        <li>{icon("check")}Bad-lead credits</li>
        <li>{icon("check")}Live in about a week</li>
      </ul>
    </div>
    <form class="territory" data-territory novalidate>
      <h3>Check territory availability</h3>
      <div class="field"><label for="t-zip">Your main ZIP code</label><input id="t-zip" name="zip" inputmode="numeric" maxlength="5" placeholder="e.g. 37064" autocomplete="postal-code"><span class="err"></span></div>
      <div class="field"><label for="t-svc">Lead type</label><select id="t-svc" name="service"><option value="drainage">Drainage</option><option value="irrigation">Irrigation</option><option value="both">Drainage + irrigation</option></select></div>
      <button class="btn btn-dark btn-block" type="submit">Check availability {icon("arrow")}</button>
      <div class="territory-result" role="status" aria-live="polite"></div>
    </form>
  </div>
</div></section>"""


def sample_lead(kind="drainage"):
    if kind == "irrigation":
        rows = [("Service", "New sprinkler system, 6 zones"), ("Property", "Single-family · ~0.3 acre"),
                ("Location", "Frisco, TX 75034"), ("Timeline", "Within 30 days"), ("Ownership", "Owner, not renter"),
                ("Budget signal", "Has seen quotes before"), ("Best time to call", "Weekdays after 5pm"), ("Phone", "Verified ✓")]
        head = "Irrigation install request"
    else:
        rows = [("Service", "French drain + downspout tie-in"), ("Problem", "Standing water by patio after rain"),
                ("Location", "Franklin, TN 37064"), ("Timeline", "As soon as possible"), ("Ownership", "Owner, not renter"),
                ("Approx. length", "120–150 ft"), ("Photos", "3 attached"), ("Phone", "Verified ✓")]
        head = "Drainage repair request"
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    return f"""<div class="sample-lead reveal">
  <header><strong>{head}</strong><span class="chip lime">Exclusive</span></header>
  <dl>{dl}</dl>
  <footer><span>Delivered by text, email &amp; CRM</span><span>Sample lead · details changed</span></footer>
</div>"""


QUOTES = [
    ("We stopped racing three other companies to the same homeowner. When the phone rings now, it's our job to lose.", "Owner", "Drainage contractor · Tennessee", "DM"),
    ("Spring start-ups used to be our only busy season. The irrigation repair leads keep two crews working into August.", "Operations manager", "Irrigation company · Texas", "RK"),
    ("Every lead has the problem, the ZIP and the timeline right in the text. My estimator knows what he's walking into.", "Founder", "Landscape &amp; drainage · Georgia", "JT"),
]


def quotes_block():
    cards = "".join(f"""<figure class="quote reveal reveal-d{i}"><span class="sample-tag">Sample</span>
<blockquote>{q}</blockquote><figcaption><span class="avatar">{ini}</span><div><strong>{who}</strong><span>{co}</span></div></figcaption></figure>"""
                    for i, (q, who, co, ini) in enumerate(QUOTES))
    return f"""<section class="section section-sand"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">What contractors want</span><h2>Built around how drainage and irrigation crews actually sell.</h2>
  <p>Placeholder stories show the outcomes we design for. We'll swap in real, approved client reviews as they come in.</p></div>
  <div class="quotes">{cards}</div>
</div></section>"""


def season_chart(caption):
    # Relative, illustrative demand shape (0–10) by month for each vertical.
    drain = [3, 4, 8, 10, 9, 6, 5, 6, 7, 8, 6, 3]
    irr = [1, 2, 6, 10, 10, 9, 8, 7, 5, 6, 3, 1]
    months = "JFMAMJJASOND"
    cols = "".join(
        f'<div class="season-col"><div class="b i" style="height:{i * 4.5}%;transition-delay:{n * 40}ms"></div>'
        f'<div class="b d" style="height:{d * 4.5}%;transition-delay:{n * 40}ms"></div></div>'
        for n, (d, i) in enumerate(zip(drain, irr)))
    labels = "".join(f"<span>{m}</span>" for m in months)
    return f"""<div class="season reveal" role="img" aria-label="Illustrative chart: drainage demand peaks with spring thaw and fall storms; irrigation peaks from spring start-ups through summer.">
  <div class="season-legend"><span><i style="background:var(--water)"></i>Drainage demand</span><span><i style="background:var(--turf)"></i>Irrigation demand</span></div>
  <div class="season-bars">{cols}</div>
  <div class="season-months">{labels}</div>
  <p class="season-caption">{caption}</p>
</div>"""


CALC_PRESETS = {"drainage": dict(leads=25, cost=95, close=30, ticket=4800),
                "irrigation": dict(leads=30, cost=70, close=35, ticket=3600)}


def calculator(kind="drainage"):
    v = CALC_PRESETS[kind]

    def rng(id_, name, label, mn, mx, step, val):
        return f"""<div class="range-row"><label for="{id_}">{label}<output for="{id_}"></output></label>
<input type="range" id="{id_}" name="{name}" min="{mn}" max="{mx}" step="{step}" value="{val}"></div>"""
    return f"""<div class="calc reveal" data-calc>
  <div class="calc-inputs">
    <div class="calc-tabs" role="group" aria-label="Preset">
      <button type="button" data-preset="drainage" aria-pressed="{str(kind == 'drainage').lower()}">Drainage</button>
      <button type="button" data-preset="irrigation" aria-pressed="{str(kind == 'irrigation').lower()}">Irrigation</button>
    </div>
    {rng("c-leads", "leads", "Leads per month", 5, 80, 1, v["leads"])}
    {rng("c-cost", "cost", "Cost per lead", 30, 200, 5, v["cost"])}
    {rng("c-close", "close", "Your close rate", 5, 70, 1, v["close"])}
    {rng("c-ticket", "ticket", "Average job value", 500, 15000, 100, v["ticket"])}
  </div>
  <div class="calc-out" aria-live="polite">
    <span class="calc-label">Estimated monthly revenue</span>
    <div class="calc-big" data-out="revenue">$0</div>
    <dl class="calc-rows">
      <div><dt>Jobs closed</dt><dd data-out="jobs">0</dd></div>
      <div><dt>Lead spend</dt><dd data-out="spend">$0</dd></div>
      <div><dt>Cost per closed job</dt><dd data-out="cpa">$0</dd></div>
      <div><dt>Revenue per $1 spent</dt><dd data-out="roi">0×</dd></div>
    </dl>
    <p class="calc-note">An estimate from your own numbers, not a guarantee. Close rates and job values vary by market, season and how fast you follow up.</p>
  </div>
</div>"""


def compare_table():
    rows = [
        ("Who else gets the lead", "Nobody. One lead, one contractor.", "Often 3–5 companies at once"),
        ("Lead types", "Drainage &amp; irrigation only", "Every trade under one roof"),
        ("Verification", "Phone-verified, service-area checked", "Varies, often unverified forms"),
        ("Territory", "ZIP codes you choose, capped per market", "Open to anyone who pays"),
        ("Contract", "Month to month", "Annual plans and membership fees are common"),
        ("Bad leads", "Credited: wrong numbers, out of area, duplicates", "Dispute processes vary"),
    ]
    body = "".join(
        f'<tr><th scope="row">{a}</th><td class="us"><span class="yes">{icon("check")}{b}</span></td><td><span class="no">{icon("x")}{c}</span></td></tr>'
        for a, b, c in rows)
    return f"""<div class="table-scroll reveal"><table class="compare">
<thead><tr><th scope="col"></th><th scope="col" class="us">Launch Lead Gen</th><th scope="col">Typical shared-lead marketplace</th></tr></thead>
<tbody>{body}</tbody></table></div>"""


def steps_block():
    steps = [
        ("Pick your turf", "Choose the ZIP codes, job types and weekly volume you want. Want French drains but not sump pumps? Done."),
        ("We launch local campaigns", "Search, social and landing pages written for homeowners with soggy yards and broken sprinklers, in your area only."),
        ("Every request is screened", "We verify the phone number, confirm the address is in your territory, and capture the problem, timeline and photos."),
        ("Your phone buzzes", "The lead lands by text, email and your CRM in under a minute, so you can call while they're still thinking about it."),
    ]
    out = "".join(f'<div class="step reveal reveal-d{n}"><div class="step-num">{n + 1}</div><h3>{t}</h3><p>{d}</p></div>'
                  for n, (t, d) in enumerate(steps))
    return f'<div class="steps">{out}</div>'


# ---------------------------------------------------------------- posts
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
    return posts


CAT_STYLE = {"Drainage": ("drainage", "drop"), "Irrigation": ("irrigation", "sprinkler"), "Lead Strategy": ("strategy", "chart")}


def nice_date(d):
    y, m, dd = map(int, d.split("-"))
    return date(y, m, dd).strftime("%b %-d, %Y")


def post_card(p, feature=False, cls=""):
    art, ic = CAT_STYLE.get(p["category"], ("strategy", "book"))
    chip = "turf" if art == "irrigation" else ""
    return f"""<a class="post-card {cls}{' post-feature' if feature else ''}" href="/blog/{p['slug']}.html" data-post-cat="{esc(p['category'])}">
  <div class="post-art {art}">{icon(ic)}</div>
  <div class="post-body"><span class="chip {chip}">{esc(p['category'])}</span><h3>{esc(p['title'])}</h3><p>{esc(p['excerpt'])}</p>
  <div class="post-meta"><span>{nice_date(p['date'])}</span><span>·</span><span>{esc(p['readTime'])}</span></div></div>
</a>"""


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub("<[^>]+>", "", s).lower()).strip("-")[:60]


# ================================================================ PAGES
def build_home(posts):
    home_faq = [
        ("Are the leads really exclusive?", "Yes. Each homeowner request goes to one contractor in that territory. We don't resell it, split it or post it to a marketplace."),
        ("What counts as a drainage or irrigation lead?", "A homeowner in your ZIP codes asking for help with a specific job: French drains, regrading, downspouts, sump pumps, dry wells, sprinkler installs, repairs, drip conversions, controllers, start-ups and winterizations. You choose which job types you want."),
        ("How fast do leads arrive?", "Leads are pushed by text and email the moment the homeowner finishes the request, and can post straight into most CRMs. Calling within the first few minutes makes a real difference to booking rates, so we build for speed."),
        ("What if a lead is bad?", "Wrong numbers, duplicates, renters without authority, and addresses outside your territory are credited back. Report it from the lead notification and we review it within one business day."),
        ("Do I have to sign a long contract?", "No. Plans are month to month. We ask for a short ramp-up window so campaigns can learn your market, but you can pause or cancel any time after that."),
        ("How quickly can I start?", "Most territories go live in about a week: a short onboarding call, ZIP and job-type setup, CRM or text routing, then campaigns launch."),
    ]
    latest = "".join(post_card(p, cls="reveal") for p in posts[:3])
    body = f"""
<section class="hero on-dark">
  <div class="wrap hero-grid">
    <div class="reveal">
      <span class="chip dark" style="margin-bottom:22px"><span class="dot"></span>Now onboarding drainage &amp; irrigation pros</span>
      <h1>Exclusive <span class="grad-text">drainage &amp; irrigation</span> leads that ring your phone, not your competitor's.</h1>
      <p class="lede">We run hyper-local campaigns for homeowners with soggy yards, flooded basements and broken sprinklers, then send every verified request to one contractor only: you.</p>
      <div class="hero-ctas">
        <a class="btn btn-primary btn-lg" href="/contact.html#territory">Check my territory {icon("arrow")}</a>
        <a class="btn btn-ghost btn-lg" href="/how-it-works.html">See how it works</a>
      </div>
      <ul class="hero-proof">
        <li>{icon("lock")}100% exclusive</li>
        <li>{icon("shield")}Phone-verified</li>
        <li>{icon("map")}Your ZIP codes only</li>
        <li>{icon("refresh")}Month to month</li>
      </ul>
    </div>
    <div class="feed reveal reveal-d2">
      <div class="feed-float two">{icon("zap")}<div>Delivered in &lt;60s<small>Text · email · CRM</small></div></div>
      <div class="feed-panel">
        <div class="feed-top"><strong><span class="dot"></span>Incoming leads</strong><span>Sample feed</span></div>
        <div class="feed-list" data-feed aria-live="off"></div>
        <p class="feed-note">Sample requests for illustration. Names and contact details are never shown publicly.</p>
      </div>
      <div class="feed-float one">{icon("check")}<div>Booked: site visit<small>Thu 4:30pm · Franklin, TN</small></div></div>
    </div>
  </div>
  {WAVE.format(cls="")}
</section>
{marquee()}

<section class="section"><div class="wrap">
  <div class="stats reveal">
    <div class="stat"><strong>1</strong><span>contractor per lead. Never shared, never resold.</span></div>
    <div class="stat"><strong>&lt;60s</strong><span>from homeowner request to your phone</span></div>
    <div class="stat"><strong>14</strong><span>drainage &amp; irrigation job types you can pick from</span></div>
    <div class="stat"><strong>$0</strong><span>setup fees on month-to-month plans</span></div>
  </div>
</div></section>

<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Two specialties. Nothing else.</span>
  <h2>We only do water. That's why the leads are better.</h2>
  <p>General lead marketplaces sell roofers, plumbers and painters from the same funnel. Our ads, landing pages and screening questions are written for one thing: getting homeowners with water problems to the right contractor.</p></div>
  <div class="grid-2">
    <article class="vertical drain reveal">
      <svg class="art" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1">{ICONS["drop"]}</svg>
      <span class="chip dark" style="align-self:flex-start;margin-bottom:18px">{icon("drop")} Drainage</span>
      <h3>Drainage leads</h3>
      <p>Homeowners with standing water, eroding beds, wet basements and foundation worries. High-ticket, urgent, and usually ready to book after the next storm.</p>
      <ul><li>French drains</li><li>Regrading</li><li>Downspouts</li><li>Sump pumps</li><li>Dry wells</li><li>Channel drains</li></ul>
      <div class="ticket"><div><small>Typical job size*</small><strong>$2.5k – $12k+</strong></div><a class="btn btn-primary" href="/drainage-leads.html">Drainage leads {icon("arrow")}</a></div>
    </article>
    <article class="vertical irr reveal reveal-d1">
      <svg class="art" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1">{ICONS["sprinkler"]}</svg>
      <span class="chip dark" style="align-self:flex-start;margin-bottom:18px">{icon("sprinkler")} Irrigation</span>
      <h3>Irrigation leads</h3>
      <p>New installs, repairs and water-saving upgrades, plus the seasonal service work that turns one customer into years of start-ups and winterizations.</p>
      <ul><li>Sprinkler installs</li><li>Repairs</li><li>Drip systems</li><li>Smart controllers</li><li>Backflow</li><li>Winterization</li></ul>
      <div class="ticket"><div><small>Typical job size*</small><strong>$250 – $8k+</strong></div><a class="btn btn-primary" href="/irrigation-leads.html">Irrigation leads {icon("arrow")}</a></div>
    </article>
  </div>
  <p style="font-size:.82rem;color:var(--muted);margin-top:14px">*Broad ranges seen across many U.S. markets. Your prices depend on region, site conditions and scope.</p>
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Why switch</span><h2>Stop buying a seat in a <span class="mark">bidding war</span>.</h2>
  <p>When the same homeowner gets four calls in ten minutes, the cheapest bid wins and everyone else paid for nothing. Exclusive leads change the math.</p></div>
  {compare_table()}
  <p style="margin-top:20px"><a href="/blog/exclusive-vs-shared-leads.html">Read: Exclusive vs. shared leads, the real math →</a></p>
</div></section>

<section class="section section-dark on-dark" id="how"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">How it works</span><h2>From soggy yard to booked estimate in four steps.</h2>
  <p>You focus on the work. We handle the ads, the landing pages, the screening and the delivery.</p></div>
  {steps_block()}
  <div style="margin-top:56px" class="reveal"><a class="btn btn-ghost" href="/how-it-works.html">The full process {icon("arrow")}</a></div>
</div></section>

<section class="section"><div class="wrap anatomy">
  {sample_lead()}
  <div class="reveal">
    <span class="eyebrow">Anatomy of a lead</span>
    <h2>Everything you need before you dial.</h2>
    <p style="color:var(--muted);font-size:1.1rem">No more "someone wants a quote" with a dead phone number. Each lead arrives with the details your estimator needs to qualify, price and book on the first call.</p>
    <ul class="checklist">
      <li>{icon("check")}<div><strong>The actual problem</strong><span>Pooling, wet basement, broken heads, new install: in the homeowner's words, plus photos when they have them.</span></div></li>
      <li>{icon("check")}<div><strong>Verified contact &amp; ownership</strong><span>Phone number confirmed. Renters and out-of-area requests are filtered out.</span></div></li>
      <li>{icon("check")}<div><strong>Timeline &amp; scope signals</strong><span>How soon, rough size, and whether they've had other quotes.</span></div></li>
    </ul>
    <a class="btn btn-dark" href="/blog/qualify-drainage-leads.html">Our first-call playbook {icon("arrow")}</a>
  </div>
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">ROI calculator</span><h2>Run your numbers.</h2>
  <p>Drag the sliders to match your business. The math is simple: lead spend in, closed jobs out.</p></div>
  {calculator()}
</div></section>

<section class="section"><div class="wrap">
  <div class="grid-2" style="align-items:center;gap:clamp(32px,5vw,72px)">
    <div class="reveal">
      <span class="eyebrow">Year-round pipeline</span>
      <h2>Two seasons that cover each other.</h2>
      <p style="color:var(--muted);font-size:1.1rem">Drainage demand jumps with spring thaw and fall storms. Irrigation runs hot from start-ups through summer repairs. Run both and your crews stay booked when one side slows down.</p>
      <a class="btn btn-ghost" href="/blog/drainage-demand-calendar.html">The drainage demand calendar {icon("arrow")}</a>
    </div>
    {season_chart("Illustrative shape only. Timing shifts with your climate: earlier in the South, later in the North.")}
  </div>
</div></section>

{quotes_block()}

<section class="section"><div class="wrap">
  <div class="section-head reveal" style="display:flex;justify-content:space-between;align-items:end;gap:24px;max-width:none;flex-wrap:wrap">
    <div style="max-width:640px"><span class="eyebrow">Contractor playbook</span><h2>Grow beyond the lead.</h2><p>Pricing, qualifying, seasonal planning and recurring revenue guides for drainage and irrigation owners.</p></div>
    <a class="btn btn-ghost" href="/blog/">All articles {icon("arrow")}</a>
  </div>
  <div class="posts">{latest}</div>
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">FAQ</span><h2>Questions contractors ask us.</h2></div>
  {faq(home_faq)}
</div></section>

{cta_band()}
"""
    schema = [{"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": DOMAIN, "email": EMAIL,
               "description": "Exclusive drainage and irrigation lead generation for contractors."}, faq_schema(home_faq)]
    page("index.html", "Exclusive Drainage & Irrigation Leads for Contractors | Launch Lead Gen",
         "Exclusive, phone-verified drainage and irrigation leads delivered in real time to one contractor per territory. French drains, sprinklers, sump pumps and more.",
         body, "/", schema=schema)


def service_page(kind, posts):
    if kind == "drainage":
        slug, title, eyebrow, ic = "drainage-leads.html", "Drainage Leads", "Drainage lead generation", "drop"
        h1 = 'Drainage leads from homeowners <span class="grad-text">who need it fixed now.</span>'
        lede = "French drains, regrading, downspouts, sump pumps and foundation drainage. Exclusive requests from homeowners in your ZIP codes, delivered the minute they ask."
        jobs = [
            ("pipe", "French drain installation", "Backyard pooling, soggy lawns and runoff toward the house. Usually the highest-ticket request we send."),
            ("wave", "Yard grading &amp; regrading", "Negative slope, low spots and erosion. Often bundled with drains or downspout work."),
            ("drop", "Downspout &amp; gutter drainage", "Buried extensions, pop-up emitters and tie-ins. Quick wins that open the door to bigger jobs."),
            ("pump", "Sump pumps &amp; basement drainage", "Wet basements, failed pumps and interior drains. Urgent, high-intent and storm-driven."),
            ("layers", "Dry wells &amp; catch basins", "Where water needs somewhere to go. Common in clay soils and tight lots."),
            ("grid", "Channel &amp; trench drains", "Driveways, patios and garage entries that flood every time it rains."),
        ]
        qa = [
            ("Do you send foundation repair or waterproofing leads?", "We focus on exterior and basement drainage. If a homeowner mentions structural cracks or major waterproofing, we flag it in the lead so you can decide whether to refer it."),
            ("Can I exclude certain job types?", "Yes. Many crews skip sump pumps or interior drains. Pick exactly the drainage jobs you want and we'll only target and send those."),
            ("What happens after a big storm?", "Drainage requests usually spike after heavy rain. You set a weekly cap so you never get more leads than your crews can handle, and we can raise it temporarily if you want the surge."),
            ("How do you verify drainage leads?", "Every phone number is verified, the address is checked against your territory, and the homeowner answers screening questions about the problem, the timeline and whether they own the home."),
        ]
        season = "Drainage requests usually build with spring thaw and rain, ease in midsummer, then rise again with fall storms. Illustrative shape only."
        cat = "Drainage"
    else:
        slug, title, eyebrow, ic = "irrigation-leads.html", "Irrigation Leads", "Irrigation lead generation", "sprinkler"
        h1 = 'Irrigation leads that turn into <span class="grad-text">10-year customers.</span>'
        lede = "New sprinkler systems, repairs, drip conversions and smart controllers, plus the seasonal service calls that build recurring revenue. Exclusive to you, in your ZIP codes."
        jobs = [
            ("sprinkler", "New sprinkler system installs", "New builds, sod installs and homeowners finally done dragging hoses. Your highest-value irrigation request."),
            ("tool", "Sprinkler &amp; irrigation repair", "Broken heads, leaks, dead zones and low pressure. Fast to close and a great door into a service plan."),
            ("drop", "Drip irrigation &amp; conversions", "Beds, gardens and water-wise landscapes. Popular wherever watering limits apply."),
            ("wifi", "Smart controller upgrades", "Weather-based controllers and Wi-Fi timers. Easy upsell and often rebate-eligible locally."),
            ("shield", "Backflow testing &amp; repair", "Annual testing where required and device repairs. Recurring by nature."),
            ("snow", "Spring start-ups &amp; winterization", "Seasonal service that fills the calendar and builds a route of repeat customers."),
        ]
        qa = [
            ("Do you send commercial irrigation leads?", "Our campaigns target homeowners. Occasionally a small commercial or HOA request comes through; we label it clearly and you can opt in or out."),
            ("Can I get only repair leads, or only installs?", "Yes. Choose any mix: installs only, repairs only, seasonal service only, or all of it. Many companies start with repairs because they close fast and lead to service plans."),
            ("Will I get leads in winter?", "Irrigation slows in the off-season in colder climates. That's why many of our contractors pair irrigation with drainage leads, which pick up with fall and late-winter rain."),
            ("How do you verify irrigation leads?", "Every phone number is verified, the address is checked against your territory, and the homeowner tells us what they need, the system size and their timeline."),
        ]
        season = "Irrigation requests usually jump with spring start-ups, stay strong through summer repairs, and finish with fall winterizations. Illustrative shape only."
        cat = "Irrigation"

    cards = "".join(f"""<article class="card reveal reveal-d{n % 3}"><div class="icon{' turf' if kind == 'irrigation' else ''}">{icon(i)}</div><h3>{t}</h3><p>{d}</p></article>"""
                    for n, (i, t, d) in enumerate(jobs))
    related = [p for p in posts if p["category"] == cat][:2] + [p for p in posts if p["category"] == "Lead Strategy"][:1]
    rel = "".join(post_card(p, cls="reveal") for p in related)
    other = ("irrigation", "/irrigation-leads.html", "Irrigation leads") if kind == "drainage" else ("drainage", "/drainage-leads.html", "Drainage leads")
    body = f"""
<section class="hero hero-sub on-dark">
  <div class="wrap hero-grid">
    <div class="reveal">
      <div class="breadcrumb"><a href="/">Home</a> / {title}</div>
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <div class="hero-ctas">
        <a class="btn btn-primary btn-lg" href="/contact.html?service={kind}#territory">Check my territory {icon("arrow")}</a>
        <a class="btn btn-ghost btn-lg" href="/pricing.html">See pricing</a>
      </div>
      <ul class="hero-proof"><li>{icon("lock")}Exclusive</li><li>{icon("shield")}Verified</li><li>{icon("target")}Pick your job types</li></ul>
    </div>
    <div class="reveal reveal-d2">{sample_lead(kind)}</div>
  </div>
  {WAVE.format(cls="")}
</section>

<section class="section" id="jobs"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Job types</span><h2>Choose the {kind} jobs you actually want.</h2>
  <p>Turn each job type on or off. We only target, screen and send the work that fits your crews and equipment.</p></div>
  <div class="grid-3">{cards}</div>
</div></section>

<section class="section section-dark on-dark"><div class="wrap anatomy">
  <div class="reveal">
    <span class="eyebrow">What qualifies</span>
    <h2>Only real homeowners with real projects.</h2>
    <ul class="checklist">
      <li>{icon("check")}<div><strong>Inside your territory</strong><span>Address checked against the ZIP codes you chose.</span></div></li>
      <li>{icon("check")}<div><strong>Verified phone number</strong><span>No fake numbers, no bots, no "test" submissions.</span></div></li>
      <li>{icon("check")}<div><strong>Owner or authorized decision-maker</strong><span>Renters without authority are filtered out.</span></div></li>
      <li>{icon("check")}<div><strong>A specific job and timeline</strong><span>Not "just browsing." They told us what's wrong and when they want it fixed.</span></div></li>
    </ul>
  </div>
  <div class="reveal reveal-d1">
    <div class="card" style="padding:34px">
      <div class="icon">{icon("refresh")}</div>
      <h3>Bad-lead credit policy</h3>
      <p>If a lead slips through with a wrong number, a duplicate, a renter or an out-of-area address, flag it from the notification. We review it within one business day and credit it back.</p>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">Seasonality</span><h2>Plan your crews around demand.</h2></div>
  <div style="max-width:880px;margin-inline:auto">{season_chart(season)}</div>
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">ROI</span><h2>What could {kind} leads be worth to you?</h2></div>
  {calculator(kind)}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">From the blog</span><h2>Win more {kind} jobs.</h2></div>
  <div class="posts">{rel}</div>
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">FAQ</span><h2>{title}: common questions</h2></div>
  {faq(qa)}
  <p style="text-align:center;margin-top:32px">Also run {other[0]}? <a href="{other[1]}">See {other[2]} →</a></p>
</div></section>

{cta_band()}
"""
    page(slug, f"Exclusive {title} for Contractors | Launch Lead Gen",
         f"Exclusive, verified {kind} leads for contractors. Choose your ZIP codes and job types; leads arrive by text, email and CRM in under a minute.",
         body, "/" + slug, schema=faq_schema(qa))


def build_how():
    quality = [
        ("shield", "Phone verification", "Every number is checked before the lead is sent. Disconnected and fake numbers never reach you."),
        ("map", "Territory matching", "Addresses are matched to your ZIP codes. Out-of-area requests are dropped, not dumped on you."),
        ("home", "Ownership screening", "We ask if they own the home or are authorized to approve the work."),
        ("target", "Intent questions", "Problem, scope, timeline and photos, so you can tell a $300 repair from a $9,000 drain job before you call."),
        ("lock", "One contractor only", "No reselling, no splitting, no auction. The lead is yours."),
        ("refresh", "Credits for bad leads", "Wrong numbers, duplicates, renters and out-of-area addresses are credited after review."),
    ]
    qcards = "".join(f'<article class="card reveal reveal-d{n % 3}"><div class="icon">{icon(i)}</div><h3>{t}</h3><p>{d}</p></article>' for n, (i, t, d) in enumerate(quality))
    onboarding = [
        ("Day 1", "Strategy call", "We map your ZIP codes, job types, crew capacity, average ticket and the jobs you don't want."),
        ("Days 2–4", "Build &amp; routing", "Local landing pages, ad campaigns and screening questions go up. Leads get routed to your phone, inbox and CRM."),
        ("Days 5–7", "Go live", "Campaigns launch with a weekly lead cap you control. First leads typically land in the first days."),
        ("Ongoing", "Tune &amp; scale", "Tell us which leads closed. We shift budget toward the ZIPs and job types that make you the most money."),
    ]
    tl = "".join(f'<div class="card reveal reveal-d{n}"><span class="chip">{d}</span><h3 style="margin-top:14px">{t}</h3><p>{x}</p></div>' for n, (d, t, x) in enumerate(onboarding))
    body = f"""
<section class="hero hero-sub on-dark">
  <div class="wrap" style="position:relative;max-width:900px">
    <div class="reveal">
      <div class="breadcrumb"><a href="/">Home</a> / How it works</div>
      <span class="eyebrow">How it works</span>
      <h1>We find the homeowners. <span class="grad-text">You win the jobs.</span></h1>
      <p class="lede">Launch Lead Gen is a done-for-you lead engine for drainage and irrigation contractors: local ads, landing pages, screening and instant delivery, all built around your territory.</p>
      <div class="hero-ctas"><a class="btn btn-primary btn-lg" href="/contact.html#territory">Check my territory {icon("arrow")}</a></div>
    </div>
  </div>
  {WAVE.format(cls="")}
</section>

<section class="section section-dark on-dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The engine</span><h2>Four steps, running every day.</h2></div>
  {steps_block()}
</div></section>

<section class="section" id="quality"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Lead quality promise</span><h2>Six filters before a lead ever reaches you.</h2>
  <p>Cheap leads are expensive when half of them are junk. Here's what every request has to pass.</p></div>
  <div class="grid-3">{qcards}</div>
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Onboarding</span><h2>Live in about a week.</h2></div>
  <div class="grid-4">{tl}</div>
</div></section>

<section class="section"><div class="wrap anatomy">
  <div class="reveal">
    <span class="eyebrow">Delivery</span>
    <h2>Leads go wherever you already work.</h2>
    <p style="color:var(--muted);font-size:1.1rem">Speed wins jobs. Every lead is pushed instantly so whoever's on call can dial first.</p>
    <ul class="checklist">
      <li>{icon("phone")}<div><strong>Text alerts</strong><span>To one phone or a rotation across your sales team.</span></div></li>
      <li>{icon("book")}<div><strong>Email with full details</strong><span>Easy to forward to an estimator or office manager.</span></div></li>
      <li>{icon("layers")}<div><strong>CRM posting</strong><span>Connect to the field-service or CRM tool you already use, via native integration or webhook where available.</span></div></li>
      <li>{icon("chart")}<div><strong>Close-loop reporting</strong><span>Mark leads booked, sold or lost so we can tune targeting toward your best jobs.</span></div></li>
    </ul>
  </div>
  {sample_lead()}
</div></section>

{cta_band("Ready to own your market?", "Tell us your ZIP codes and the jobs you want. We'll confirm availability and walk you through a launch plan.")}
"""
    page("how-it-works.html", "How It Works: Exclusive Drainage & Irrigation Leads | Launch Lead Gen",
         "How Launch Lead Gen finds, verifies and delivers exclusive drainage and irrigation leads to contractors in under a minute. Live in about a week.",
         body, "/how-it-works.html")


def build_pricing():
    def li(items):
        return "".join(f"<li>{icon('check')}<span>{x}</span></li>" for x in items)
    plans = f"""
<div class="plans">
  <article class="plan reveal">
    <h3>Launch</h3><p>For owner-operators adding a steady stream of jobs.</p>
    <div class="price"><span data-price data-drainage="$89" data-irrigation="$69">$89</span><small> / lead</small></div>
    <p class="price-note" data-price-note data-note-drainage="Starting price · 10–20 leads / month" data-note-irrigation="Starting price · 10–20 leads / month">Starting price · 10–20 leads / month</p>
    <ul>{li(["1 lead type: drainage <em>or</em> irrigation", "Up to 5 ZIP codes", "Text + email delivery", "Weekly lead cap you control", "Bad-lead credits"])}</ul>
    <a class="btn btn-ghost btn-block" href="/contact.html?plan=launch#territory">Start with Launch</a>
  </article>
  <article class="plan featured reveal reveal-d1">
    <span class="chip lime plan-flag">Most popular</span>
    <h3>Growth</h3><p>For multi-crew companies that want both seasons covered.</p>
    <div class="price"><span data-price data-drainage="$79" data-irrigation="$59">$79</span><small> / lead</small></div>
    <p class="price-note" data-price-note data-note-drainage="Starting price · 20–60 leads / month" data-note-irrigation="Starting price · 20–60 leads / month">Starting price · 20–60 leads / month</p>
    <ul>{li(["Drainage <em>and</em> irrigation", "Up to 15 ZIP codes", "CRM posting + team rotation", "Monthly close-rate review call", "Priority storm-surge volume", "Bad-lead credits"])}</ul>
    <a class="btn btn-primary btn-block" href="/contact.html?plan=growth#territory">Choose Growth</a>
  </article>
  <article class="plan reveal reveal-d2">
    <h3>Territory Lock</h3><p>Own your market. We stop selling your ZIPs to anyone else.</p>
    <div class="price">Custom</div>
    <p class="price-note">Monthly territory fee + reduced per-lead rate</p>
    <ul>{li(["Exclusive ZIP code lockout", "All 14 job types available", "Dedicated campaign manager", "Custom landing pages with your brand", "Quarterly market expansion plan"])}</ul>
    <a class="btn btn-ghost btn-block" href="/contact.html?plan=territory#territory">Talk about Territory Lock</a>
  </article>
</div>"""
    pfaq = [
        ("Why does the price change by market?", "Lead cost depends on local competition, population density and the job types you pick. We quote your exact per-lead rate after we look at your ZIP codes. The prices above are starting points."),
        ("Is there a setup fee or contract?", "No setup fee on Launch and Growth, and plans are month to month. Territory Lock has a monthly territory fee because we stop selling those ZIP codes to anyone else."),
        ("How do I pay?", "You pre-fund a lead balance or pay a monthly invoice, whichever works better for your cash flow. You're only billed for leads that pass our filters."),
        ("Can I pause during the off-season?", "Yes. Pause or lower your weekly cap any time. Many irrigation contractors in colder regions pause in winter or shift budget to drainage."),
        ("What does a bad-lead credit cover?", "Wrong or disconnected numbers, duplicates, renters without authority and addresses outside your territory. Flag it from the notification and we review it within one business day."),
    ]
    body = f"""
<section class="hero hero-sub on-dark">
  <div class="wrap" style="position:relative;max-width:860px;text-align:center">
    <div class="reveal">
      <span class="eyebrow" style="justify-content:center">Pricing</span>
      <h1>Pay for leads, <span class="grad-text">not promises.</span></h1>
      <p class="lede" style="margin-inline:auto">Simple per-lead pricing, no setup fees, month to month. Your exact rate depends on your market and job mix.</p>
    </div>
  </div>
  {WAVE.format(cls=" sand")}
</section>
<section class="section section-sand" style="padding-top:40px"><div class="wrap" style="text-align:center">
  <div class="price-toggle" role="group" aria-label="Lead type" data-price-toggle>
    <button type="button" data-mode="drainage" aria-pressed="true">Drainage leads</button>
    <button type="button" data-mode="irrigation" aria-pressed="false">Irrigation leads</button>
  </div>
  <div style="text-align:left">{plans}</div>
  <p style="font-size:.88rem;color:var(--muted);margin-top:28px">Starting prices shown. Your final per-lead rate is confirmed after a territory review and depends on location, competition and job types.</p>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">Do the math</span><h2>What's a closed job worth to you?</h2></div>
  {calculator()}
</div></section>

<section class="section section-sand"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">FAQ</span><h2>Pricing questions</h2></div>
  {faq(pfaq)}
</div></section>
{cta_band()}
"""
    page("pricing.html", "Pricing: Drainage & Irrigation Leads | Launch Lead Gen",
         "Simple per-lead pricing for exclusive drainage and irrigation leads. No setup fees, month to month, bad-lead credits. Check your territory.",
         body, "/pricing.html", schema=faq_schema(pfaq))


def build_contact():
    choice = lambda v, l: f'<label class="choice"><input type="checkbox" name="services" value="{v}">{l}</label>'
    body = f"""
<section class="hero hero-sub on-dark">
  <div class="wrap hero-grid" style="align-items:start">
    <div class="reveal">
      <div class="breadcrumb"><a href="/">Home</a> / Contact</div>
      <span class="eyebrow">Check your territory</span>
      <h1>Let's see if your market is <span class="grad-text">still open.</span></h1>
      <p class="lede">We limit how many contractors we work with in each area. Tell us where you work and what jobs you want. We'll confirm availability and send a launch plan within one business day.</p>
      <ul class="checklist" style="margin-top:32px">
        <li>{icon("check")}<div><strong style="color:#fff">Territory check</strong><span style="color:var(--muted-on-dark)">We confirm which of your ZIP codes are available.</span></div></li>
        <li>{icon("check")}<div><strong style="color:#fff">Lead estimate</strong><span style="color:var(--muted-on-dark)">Expected volume and per-lead pricing for your area.</span></div></li>
        <li>{icon("check")}<div><strong style="color:#fff">No pressure</strong><span style="color:var(--muted-on-dark)">A 20-minute call. If it's not a fit, we'll tell you.</span></div></li>
      </ul>
      <p style="color:var(--muted-on-dark);margin-top:28px">Prefer email? <a style="color:var(--lime)" href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
    <form class="form-card reveal reveal-d1" id="territory" data-contact data-endpoint="" novalidate>
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
      <div class="field"><label for="f-msg">Anything else? <span style="font-weight:400;color:var(--muted)">(optional)</span></label><textarea id="f-msg" name="message" placeholder="Crew size, jobs you don't want, current lead sources…"></textarea></div>
      <button class="btn btn-primary btn-lg btn-block" type="submit">Check my territory {icon("arrow")}</button>
      <div class="form-status" role="status" aria-live="polite"></div>
      <p class="form-fine">We'll only use your details to respond to this request.</p>
    </form>
  </div>
  {WAVE.format(cls="")}
</section>
"""
    page("contact.html", "Check Your Territory | Launch Lead Gen",
         "Check whether exclusive drainage and irrigation leads are available in your ZIP codes. Get a lead estimate and launch plan within one business day.",
         body, "/contact.html")


def build_blog(posts):
    cats = ["all"] + sorted({p["category"] for p in posts})
    filt = "".join(f'<button type="button" data-cat="{c}" aria-pressed="{str(c == "all").lower()}">{"All articles" if c == "all" else c}</button>' for c in cats)
    feature = post_card(posts[0], feature=True, cls="reveal")
    rest = "".join(post_card(p) for p in posts[1:])
    body = f"""
<section class="hero hero-sub on-dark">
  <div class="wrap" style="position:relative;max-width:900px">
    <div class="reveal">
      <span class="eyebrow">The contractor playbook</span>
      <h1>Grow a <span class="grad-text">drainage &amp; irrigation</span> business that books itself.</h1>
      <p class="lede">Pricing, sales scripts, seasonal planning and recurring-revenue guides for owners and estimators. No fluff, just what works in the field.</p>
    </div>
  </div>
  {WAVE.format(cls="")}
</section>
<section class="section" style="padding-top:40px"><div class="wrap">
  <div class="filters" role="group" aria-label="Filter articles" data-filters>{filt}</div>
  {feature}
  <div class="posts">{rest}</div>
</div></section>
{cta_band("Turn these playbooks into booked jobs.", "Great follow-up needs great leads. Check whether exclusive drainage and irrigation leads are available in your area.")}
"""
    page("blog/index.html", "Contractor Blog: Drainage & Irrigation Growth Playbooks | Launch Lead Gen",
         "Practical guides for drainage and irrigation contractors: pricing French drains, qualifying leads, seasonal planning, maintenance plans and lead strategy.",
         body, "/blog/")

    for p in posts:
        body_html = p["body"]
        toc = []

        def add_id(m):
            text = m.group(1)
            sid = slugify(text)
            toc.append((sid, re.sub("<[^>]+>", "", text)))
            return f'<h2 id="{sid}">{text}</h2>'
        body_html = re.sub(r"<h2>(.*?)</h2>", add_id, body_html)
        toc_html = "".join(f'<li><a href="#{sid}">{esc(html.unescape(t))}</a></li>' for sid, t in toc)
        related = [x for x in posts if x["slug"] != p["slug"] and x["category"] == p["category"]]
        related += [x for x in posts if x["slug"] != p["slug"] and x not in related]
        rel = "".join(post_card(x) for x in related[:3])
        art, _ = CAT_STYLE.get(p["category"], ("strategy", "book"))
        svc = "irrigation" if art == "irrigation" else "drainage"
        schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
                  "datePublished": p["date"], "author": {"@type": "Organization", "name": BRAND},
                  "publisher": {"@type": "Organization", "name": BRAND}, "mainEntityOfPage": f"{DOMAIN}/blog/{p['slug']}.html"}
        body = f"""
<div class="progress" aria-hidden="true"></div>
<section class="hero article-hero on-dark">
  <div class="wrap" style="position:relative">
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a> / {esc(p['category'])}</div>
    <h1>{esc(p['title'])}</h1>
    <p class="lede-dek">{esc(p['excerpt'])}</p>
    <div class="article-meta"><span class="chip dark">{esc(p['category'])}</span><span>{nice_date(p['date'])}</span><span>·</span><span>{esc(p['readTime'])}</span><span>·</span><span>By the {BRAND} team</span></div>
  </div>
  {WAVE.format(cls="")}
</section>
<section class="section" style="padding-top:48px"><div class="wrap article-layout">
  <article class="prose">{body_html}</article>
  <aside class="aside-sticky">
    <nav class="toc" aria-label="On this page"><h4>On this page</h4><ol>{toc_html}</ol></nav>
    <div class="aside-cta"><h4>Want leads like these?</h4><p>Exclusive, verified {svc} leads in your ZIP codes. One contractor per lead.</p><a class="btn btn-primary btn-block" href="/contact.html?service={svc}#territory">Check my territory</a></div>
  </aside>
</div></section>
<section class="section section-sand"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Keep reading</span><h2>More from the playbook</h2></div>
  <div class="posts">{rel}</div>
</div></section>
"""
        page(f"blog/{p['slug']}.html", f"{p['title']} | {BRAND}", p["description"], body, "/blog/", schema=schema)


def build_404():
    body = f"""<section class="hero on-dark" style="min-height:70vh;display:grid;place-items:center;text-align:center">
<div class="wrap" style="position:relative"><span class="eyebrow" style="justify-content:center">404</span><h1>This page drained away.</h1>
<p class="lede" style="margin-inline:auto">The page you're looking for doesn't exist. Try one of these instead.</p>
<div class="hero-ctas" style="justify-content:center"><a class="btn btn-primary" href="/">Home</a><a class="btn btn-ghost" href="/blog/">Blog</a></div></div>{WAVE.format(cls="")}</section>"""
    page("404.html", "Page not found | Launch Lead Gen", "Page not found.", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    posts = load_posts()
    build_home(posts)
    service_page("drainage", posts)
    service_page("irrigation", posts)
    build_how()
    build_pricing()
    build_contact()
    build_blog(posts)
    build_404()
    urls = "".join(
        f"<url><loc>{DOMAIN}/{'' if p == 'index.html' else p.replace('index.html', '')}</loc></url>"
        for p in PAGES if p != "404.html")
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
