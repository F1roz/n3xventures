"""Shared chrome: <head>, header + mega menus, mobile drawer, footer, JSON-LD."""
import json, html
from registry import *

E = html.escape
LOGO = "/assets/brand/n3x-ventures-logo.webp"
LOGO_PNG = "/assets/brand/n3x-ventures-logo.png"
REALTY_LOGO = "/assets/brand/n3x-realty-logo.webp"
ARROW = lambda: icon("arrow-right", "i-arrow")
ORG_ID = BASE + "/#organization"


def org_schema():
    return {
        "@type": ["Organization", "ProfessionalService"],
        "@id": ORG_ID,
        "name": "N3X Ventures",
        "alternateName": ["N3X", "N3X Ventures Agency"],
        "url": BASE + "/",
        "logo": {"@type": "ImageObject", "url": BASE + LOGO_PNG, "width": 783, "height": 184},
        "image": BASE + "/assets/brand/og-image.jpg",
        "description": "N3X Ventures is an AI-powered growth marketing agency that builds AI automation, paid ads, SEO & GEO, lead generation, websites, branding and content systems for US businesses across 25+ industries.",
        "foundingDate": "2022",
        "telephone": PHONE_E164,
        "email": EMAIL,
        "priceRange": "$$",
        "areaServed": [{"@type": "Country", "name": "United States"}, {"@type": "Country", "name": "United Arab Emirates"}],
        "address": {"@type": "PostalAddress", "addressLocality": "Lubbock", "addressRegion": "TX", "addressCountry": "US"},
        "location": [{"@type": "Place", "name": l} for l in LOCATIONS],
        "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE_E164, "contactType": "sales", "email": EMAIL, "areaServed": "US", "availableLanguage": ["English"]}],
        "sameAs": list(SOCIAL.values()),
        "parentOrganization": {"@type": "Organization", "name": "N3X"},
        "subOrganization": {"@type": "Organization", "name": "N3X Realty", "url": REALTY_URL},
        "knowsAbout": ["AI automation", "Generative Engine Optimization", "Search engine optimization", "Answer engine optimization", "Google Ads", "Meta Ads", "Lead generation", "Web design", "Branding", "Content marketing", "LinkedIn marketing", "Video editing"],
    }


def website_schema():
    return {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "N3X Ventures", "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}


def crumbs_schema(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + (u if u != "/" else "/")} for i, (n, u) in enumerate(trail)]}


def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in items]}


def head(title, desc, path, extra_schema=(), og_image="/assets/brand/og-image.jpg", og_type="website", robots="index, follow, max-image-preview:large", preload=None, article_meta=""):
    url = BASE + (path if path != "/" else "/")
    graph = [org_schema(), website_schema()] + [s for s in extra_schema if s]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">\n' if preload else ""
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
{GA}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="author" content="N3X Ventures">
<meta name="theme-color" content="#101118">
<meta name="color-scheme" content="dark light">
<meta property="og:site_name" content="N3X Ventures">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}{og_image}">
<meta property="og:image:alt" content="{E(title)}">
<meta property="og:locale" content="en_US">
{article_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{BASE}{og_image}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/brand/favicon-192.png">
<link rel="apple-touch-icon" href="/assets/brand/favicon-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="N3X Ventures Blog" href="/blog/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Instrument+Sans:wght@400..700&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400&display=swap">
<link rel="preload" as="image" href="{LOGO}">
{pre}<link rel="stylesheet" href="/assets/css/n3x.css?v=2">
<script type="application/ld+json">{ld}</script>
</head>"""


def mega_services():
    groups = {"Growth": [], "Build & Automate": []}
    for s in SERVICES:
        sv = SVC[s[0]]
        groups[sv["group"]].append(
            f'<a class="mega-link" href="/services/{sv["slug"]}"><span class="ico">{icon(sv["icon"])}</span><span><strong>{E(sv["name"])}</strong><span>{E(sv["blurb"])}</span></span></a>')
    cols = "".join(f'<div>{"".join(v)}</div>' for v in groups.values())
    return f"""<div class="mega" role="region" aria-label="Services">
  <div class="mega-grid">{cols}
    <a class="mega-feature" href="/services/seo-geo"><img src="/assets/img/svc-seo-geo-sm.webp" alt="" loading="lazy" width="800" height="533"><span class="tag no-dot">New for 2026</span><h4>Get recommended by ChatGPT &amp; Gemini</h4><p>Our SEO + GEO program makes your business the answer AI search engines cite.</p><span class="link-arrow">Explore SEO &amp; GEO {ARROW()}</span></a>
  </div>
  <div class="mega-foot"><span>Every service is month-to-month. Start with one, add more when it works.</span><a class="link-arrow" href="/services">All services {ARROW()}</a></div>
</div>"""


def mega_industries():
    cols = []
    for c in CATS:
        links = [f'<a href="{niche_url(n[0])}">{icon(n[4])}{E(n[1])}</a>' for n in NICHES if n[3] == c]
        if c == "B2B & Online":
            links.insert(3, f'<a href="/coaches">{icon("graduation-cap")}Coaches &amp; Consultants</a>')
        cols.append(f'<div><h5>{E(c)}</h5>{"".join(links)}</div>')
    return f"""<div class="mega mega--industries" role="region" aria-label="Industries">
  <div class="mega-ind">{"".join(cols)}</div>
  <div class="mega-foot"><span>Real estate agent or brokerage? <a class="link-arrow" href="{REALTY_URL}" target="_blank" rel="noopener">Visit N3X Realty {icon("arrow-up-right")}</a></span><a class="link-arrow" href="/industries">All 25 industries {ARROW()}</a></div>
</div>"""


def header(active=""):
    def cur(k):
        return ' aria-current="page"' if active == k else ""
    chev = icon("chevron-down", "chev")
    svc_links = "".join(f'<a href="/services/{s[0]}">{E(s[1])}</a>' for s in SERVICES)
    ind_links = "".join(f'<a href="{niche_url(n[0])}">{E(n[1])}</a>' for n in NICHES[:11])
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar">
  <div class="container">
    <a class="topbar-sister" href="{REALTY_URL}" target="_blank" rel="noopener" aria-label="Visit our sister brand N3X Realty for real estate growth">
      <span class="hide-sm">Real estate pro?</span> <img src="{REALTY_LOGO}" alt="N3X Realty" width="102" height="26" loading="eager"> <b class="hide-sm">Growth systems for agents</b> {icon("arrow-up-right")}
    </a>
    <div class="topbar-meta">
      <a href="mailto:{EMAIL}">{icon("mail")} {EMAIL}</a>
      <a href="tel:{PHONE_E164}">{icon("phone")} {PHONE}</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="container nav">
    <a class="brand" href="/" aria-label="N3X Ventures — home"><img src="{LOGO}" alt="N3X Ventures" width="162" height="38"></a>
    <nav aria-label="Primary">
      <ul class="nav-menu">
        <li class="nav-item has-mega"><a class="nav-link" href="/services" aria-expanded="false" aria-haspopup="true"{cur("services")}>Services {chev}</a>{mega_services()}</li>
        <li class="nav-item has-mega"><a class="nav-link" href="/industries" aria-expanded="false" aria-haspopup="true"{cur("industries")}>Industries {chev}</a>{mega_industries()}</li>
        <li class="nav-item"><a class="nav-link" href="/coaches"{cur("coaches")}>Coaches</a></li>
        <li class="nav-item"><a class="nav-link" href="/blog"{cur("blog")}>Blog</a></li>
        <li class="nav-item"><a class="nav-link" href="/about"{cur("about")}>About</a></li>
        <li class="nav-item"><a class="nav-link" href="/contact"{cur("contact")}>Contact</a></li>
      </ul>
    </nav>
    <div class="nav-actions">
      <a class="nav-phone" href="tel:{PHONE_E164}">{icon("phone")}{PHONE}</a>
      <a class="btn btn--primary btn--sm" href="/contact" data-book>Book a call {ARROW()}</a>
      <button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer-scrim" data-close-drawer></div>
  <div class="drawer-panel" role="dialog" aria-modal="true" aria-label="Menu">
    <div class="drawer-head"><img src="{LOGO}" alt="N3X Ventures" width="136" height="32"><button class="drawer-close" data-close-drawer aria-label="Close menu">{icon("x")}</button></div>
    <div class="drawer-body">
      <ul class="drawer-nav">
        <li><details class="drawer-acc"><summary>Services {icon("chevron-down")}</summary><div class="drawer-sub">{svc_links}<a class="all" href="/services">All services →</a></div></details></li>
        <li><details class="drawer-acc"><summary>Industries {icon("chevron-down")}</summary><div class="drawer-sub">{ind_links}<a href="/coaches">Coaches</a><a class="all" href="/industries">All 25 industries →</a></div></details></li>
        <li><a href="/coaches">Coaches {icon("arrow-right")}</a></li>
        <li><a href="/blog">Blog {icon("arrow-right")}</a></li>
        <li><a href="/about">About {icon("arrow-right")}</a></li>
        <li><a href="/contact">Contact {icon("arrow-right")}</a></li>
      </ul>
      <a class="sister-card" href="{REALTY_URL}" target="_blank" rel="noopener" style="margin-top:22px"><img src="{REALTY_LOGO}" alt="N3X Realty" width="118" height="30" loading="lazy"><p>Real estate agent or brokerage? Our sister brand builds websites, CRM &amp; AI systems for realtors.</p><span class="link-arrow">Visit N3X Realty {icon("arrow-up-right")}</span></a>
    </div>
    <div class="drawer-foot">
      <a class="btn btn--primary btn--lg btn--block" href="/contact" data-book>Book a free strategy call</a>
      <a class="nav-phone" href="tel:{PHONE_E164}">{icon("phone")}{PHONE}</a>
    </div>
  </div>
</div>"""


def footer():
    svc = "".join(f'<li><a href="/services/{s[0]}">{E(s[1])}</a></li>' for s in SERVICES)
    ind = "".join(f'<li><a href="{niche_url(s)}">{E(n)}</a></li>' for s, n in [("coaches", "Coaches & Consultants"), ("lawyers", "Lawyers"), ("dentists", "Dentists"), ("roofing", "Roofing"), ("hvac", "HVAC"), ("med-spas", "Med Spas"), ("saas", "SaaS"), ("ecommerce", "E-commerce")])
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <a href="/" aria-label="N3X Ventures — home"><img src="{LOGO}" alt="N3X Ventures" width="196" height="46" loading="lazy"></a>
        <p>AI-powered growth marketing for US businesses — automation, ads, SEO &amp; GEO, content and brand, run by one accountable team.</p>
        <div class="footer-contact">
          <a href="tel:{PHONE_E164}">{icon("phone")} {PHONE}</a>
          <a href="mailto:{EMAIL}">{icon("mail")} {EMAIL}</a>
          <span>{icon("map-pin")} {" · ".join(LOCATIONS)}</span>
        </div>
        <div class="socials">
          <a href="{SOCIAL['instagram']}" target="_blank" rel="noopener" aria-label="N3X Ventures on Instagram">{icon("instagram")}</a>
          <a href="{SOCIAL['linkedin']}" target="_blank" rel="noopener" aria-label="N3X Ventures on LinkedIn">{icon("linkedin")}</a>
          <a href="{SOCIAL['facebook']}" target="_blank" rel="noopener" aria-label="N3X on Facebook">{icon("facebook")}</a>
          <a href="{WA}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{icon("message-circle")}</a>
        </div>
      </div>
      <div class="footer-col"><h2>Services</h2><ul>{svc}</ul></div>
      <div class="footer-col"><h2>Industries</h2><ul>{ind}<li><a href="/industries">View all 25 →</a></li></ul></div>
      <div class="footer-col"><h2>Company</h2><ul><li><a href="/about">About N3X</a></li><li><a href="/blog">Blog</a></li><li><a href="/coaches">Coaches program</a></li><li><a href="/contact">Contact</a></li><li><a href="/contact" data-book>Book a call</a></li><li><a href="/privacy">Privacy</a></li><li><a href="/terms">Terms</a></li></ul></div>
      <div class="footer-col footer-sister"><h2>Sister brand</h2>
        <a class="sister-card" href="{REALTY_URL}" target="_blank" rel="noopener"><img src="{REALTY_LOGO}" alt="N3X Realty" width="118" height="30" loading="lazy"><p>Websites, CRM &amp; AI lead systems built only for real estate agents and brokerages.</p><span class="link-arrow">Visit N3X Realty {icon("arrow-up-right")}</span></a>
      </div>
    </div>
  </div>
  <div class="footer-word" aria-hidden="true">N3X</div>
  <div class="footer-bottom"><div class="container"><p style="margin:0">© 2026 N3X Ventures. Part of the N3X family of brands. All rights reserved.</p><nav aria-label="Legal"><a href="/privacy">Privacy Policy</a><a href="/terms">Terms of Service</a><a href="/sitemap.xml">Sitemap</a></nav></div></div>
</footer>
<div class="fab-stack">
  <button class="fab fab--top" aria-label="Back to top">{icon("arrow-up")}</button>
  <a class="fab fab--wa" href="{WA}" target="_blank" rel="noopener" aria-label="Chat with N3X Ventures on WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.08 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.04 21.5h-.01a9.45 9.45 0 0 1-4.82-1.32l-.35-.21-3.58.94.96-3.49-.23-.36a9.43 9.43 0 0 1-1.45-5.03c0-5.22 4.25-9.47 9.48-9.47 2.53 0 4.91.99 6.7 2.78a9.4 9.4 0 0 1 2.77 6.7c0 5.22-4.25 9.46-9.47 9.46zm8.06-17.53A11.33 11.33 0 0 0 12.04.63C5.76.63.65 5.74.65 12.02c0 2.01.52 3.97 1.52 5.7L.55 23.62l6.04-1.58a11.36 11.36 0 0 0 5.44 1.39h.01c6.28 0 11.39-5.11 11.39-11.39 0-3.04-1.18-5.9-3.34-8.06z"/></svg></a>
</div>
<script src="/assets/js/n3x.js?v=2" defer></script>
</body>
</html>"""


def page(title, desc, path, body, active="", schema=(), body_class="", **kw):
    bc = f' class="{body_class}"' if body_class else ""
    return head(title, desc, path, schema, **kw) + f"\n<body{bc}>\n" + header(active) + f'\n<main id="main">\n{body}\n</main>\n' + footer()


# --------------------------------------------------------------------------- shared blocks
def crumbs(trail):
    items = []
    for i, (n, u) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li><span aria-current="page">{E(n)}</span></li>')
        else:
            items.append(f'<li><a href="{u}">{E(n)}</a></li>')
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{"".join(items)}</ol></nav>'


def faq_block(items, title="Questions, answered", eyebrow="FAQ", sub="Can't find what you're looking for? Call or WhatsApp us — a strategist will answer."):
    det = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{E(q["q"])}<span class="pm">{icon("plus")}</span></summary><div class="answer"><p>{E(q["a"])}</p></div></details>'
        for i, q in enumerate(items))
    return f"""<section class="sec sec--paper" id="faq">
  <div class="container faq-wrap">
    <div class="sec-head"><span class="tag">{E(eyebrow)}</span><h2>{E(title)}</h2><p class="lead">{E(sub)}</p><a class="btn btn--dark" href="/contact" data-book>Ask us directly {ARROW()}</a></div>
    <div class="faq reveal">{det}</div>
  </div>
</section>"""


def cta_block(h2="Your next stage of growth is one call away", p="Book a free 30-minute strategy call. We'll audit your digital presence and hand you a custom growth roadmap — no strings attached.", service="", niche=""):
    data = (f' data-service="{E(service)}"' if service else "") + (f' data-niche="{E(niche)}"' if niche else "")
    return f"""<section class="sec sec--tight" id="cta">
  <div class="container">
    <div class="cta reveal">
      <div class="bg-grid"></div><div class="glow glow--mint"></div><div class="glow glow--azure"></div>
      <span class="tag">Free strategy call</span>
      <h2>{E(h2)}</h2>
      <p class="lead">{E(p)}</p>
      <div class="btn-row"><a class="btn btn--primary btn--lg" href="/contact" data-book{data}>Book my free strategy call {ARROW()}</a><a class="btn btn--ghost btn--lg" href="{WA}" target="_blank" rel="noopener">{icon("message-circle")} WhatsApp us</a></div>
      <div class="cta-note"><span>{icon("check")} 30 minutes, no obligation</span><span>{icon("check")} Month-to-month plans</span><span>{icon("check")} Reply within 1 business day</span></div>
    </div>
  </div>
</section>"""


def pricing_block(pr, service="", niche="", dark=True):
    cards = []
    for p in pr["plans"]:
        feats = "".join(f"<li>{icon('check')}{E(f)}</li>" for f in p["features"])
        badge = '<span class="plan-badge">Most popular</span>' if p["featured"] else ""
        btn = "btn--primary" if p["featured"] else "btn--ghost"
        data = (f' data-service="{E(service)}"' if service else "") + (f' data-niche="{E(niche)}"' if niche else "")
        cards.append(f"""<div class="plan{' plan--featured' if p['featured'] else ''}">{badge}
  <div class="plan-name">{E(p['name'])}</div><p class="plan-desc">{E(p['desc'])}</p>
  <div class="plan-price"><strong>{E(p['amount'])}</strong><span>/ month</span></div>
  <ul>{feats}</ul>
  <a class="btn {btn} btn--block" href="/contact" data-book{data}>{E(p['cta'])} {ARROW()}</a>
</div>""")
    h = pr["head"]
    note = pr.get("note") or "All packages include a free onboarding audit. Custom enterprise plans available."
    return f"""<section class="sec" id="packages">
  <div class="bg-grid"></div>
  <div class="container">
    <div class="sec-head u-center"><span class="tag">{E(h['eyebrow'] or 'Investment plans')}</span><h2>{E(h['h2'])}</h2><p class="lead">{E(h['p'] or 'Start where you are, scale when you are ready. Every plan is month-to-month — no long-term contracts.')}</p></div>
    <div class="pricing" data-stagger>{"".join(cards)}</div>
    <p class="pricing-note">{icon("shield-check")}{E(note)}</p>
  </div>
</section>"""


def compare_block(vs, eyebrow=None, title=None):
    left = "".join(f"<li>{icon('x')}<span>{E(x)}</span></li>" for x in vs["left"])
    right = "".join(f"<li>{icon('check')}<span>{E(x)}</span></li>" for x in vs["right"])
    h = vs["head"]
    return f"""<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">{E(eyebrow or h['eyebrow'])}</span><h2>{E(title or h['h2'])}</h2></div>
    <div class="compare reveal">
      <div class="compare-col compare-col--bad"><h3><span class="badge">{icon("trending-down")}</span>{E(vs['left_title'])}</h3><ul>{left}</ul></div>
      <div class="compare-vs"><span>VS</span></div>
      <div class="compare-col compare-col--good"><h3><span class="badge">{icon("trending-up")}</span>{E(vs['right_title'])}</h3><ul>{right}</ul></div>
    </div>
  </div>
</section>"""


def steps_block(items, eyebrow, title, paper=False, sub=""):
    n = len(items)
    st = "".join(f'<div class="step"><div class="step-num">{i+1:02d}</div><h3>{E(s["title"])}</h3><p>{E(s["text"])}</p></div>' for i, s in enumerate(items))
    subp = f'<p class="lead">{E(sub)}</p>' if sub else ""
    return f"""<section class="sec{' sec--paper' if paper else ''}">
  <div class="container">
    <div class="sec-head"><span class="tag">{E(eyebrow)}</span><h2>{E(title)}</h2>{subp}</div>
    <div class="steps" style="--n:{n}" data-stagger>{st}</div>
  </div>
</section>"""


def quote_cards(ts):
    stars = "".join(icon("star") for _ in range(5))
    out = []
    for t in ts:
        ini = "".join(w[0] for w in t["name"].replace(".", "").split()[:2])
        out.append(f'<figure class="quote" style="margin:0"><div class="stars" aria-label="5 out of 5 stars">{stars}</div><blockquote>“{E(t["quote"])}”</blockquote><figcaption><span class="avatar">{E(ini)}</span><span><strong>{E(t["name"])}</strong><span>{E(t["role"])}</span></span></figcaption></figure>')
    return "".join(out)


def post_card(p, extra_cls=""):
    return f"""<a class="post-card {extra_cls}" href="/blog/{p['slug']}" data-cat="{p['cat_slug']}">
  <div class="media"><img src="/assets/img/{p['image']}-sm.webp" alt="{E(p['image_alt'])}" loading="lazy" width="800" height="500"></div>
  <div class="body"><div class="post-meta"><span class="cat">{E(p['category'])}</span><span>{p['date_h']}</span><span class="dot"></span><span>{p['minutes']} min read</span></div>
  <h3>{E(p['title'])}</h3><p>{E(p['description'])}</p><span class="read">Read article {icon("arrow-right")}</span></div>
</a>"""
