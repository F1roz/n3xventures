"""Build the full N3X Ventures static site into ./site"""
import json, os, re, shutil, datetime, html
from registry import *
from layout import *
from posts1 import POSTS_A
from posts2 import POSTS_B

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("N3X_OUT", os.path.join(ROOT, "site"))
C = json.load(open(os.path.join(ROOT, "content.json")))
TODAY = "2026-10-15"
PAGES = []  # (path, lastmod, priority)


def write(path, content, lastmod=TODAY, priority="0.7"):
    """path is the public URL path, e.g. / or /services/paid-ads"""
    if path == "/":
        fp = os.path.join(OUT, "index.html")
    elif path.endswith("/") or path in ("/services", "/industries", "/blog"):
        fp = os.path.join(OUT, path.strip("/"), "index.html")
    else:
        fp = os.path.join(OUT, path.strip("/") + ".html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    if not fp.endswith("404.html"):
        content = relativize(content, fp)
    open(fp, "w", encoding="utf-8").write(content)
    if priority:
        PAGES.append((path, lastmod, priority))


def _rel_target(url, from_dir):
    """Map a root-absolute site URL to a relative file path that works in Live Server, file:// and Vercel."""
    path, sep, frag = url.partition("#")
    path, qsep, query = path.partition("?")
    if path == "/":
        target = "index.html"
    else:
        p = path.strip("/")
        last = p.rsplit("/", 1)[-1]
        if "." in last:
            target = p
        elif p in ("services", "industries", "blog"):
            target = p + "/index.html"
        else:
            target = p + ".html"
    rel = os.path.relpath(os.path.join(OUT, target), from_dir).replace(os.sep, "/")
    return rel + (qsep + query if qsep else "") + (sep + frag if sep else "")


def relativize(content, fp):
    d = os.path.dirname(fp)
    content = re.sub(r'(href|src)="(/(?!/)[^"]*)"', lambda m: f'{m.group(1)}="{_rel_target(m.group(2), d)}"', content)
    def fix_srcset(m):
        parts = []
        for part in m.group(1).split(","):
            bits = part.strip().split(" ")
            if bits[0].startswith("/"):
                bits[0] = _rel_target(bits[0], d)
            parts.append(" ".join(bits))
        return 'srcset="' + ", ".join(parts) + '"'
    return re.sub(r'srcset="([^"]+)"', fix_srcset, content)


def strip_emoji(s):
    return re.sub(r"^[^\w$]+\s*", "", s).strip()


def clip(s, n=158):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:—-")
    return cut + "…"


def img(name, alt, sizes="(max-width: 1024px) 100vw, 50vw", eager=False, w=1600, h=1067, cls=""):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="/assets/img/{name}.webp" srcset="/assets/img/{name}-sm.webp 800w, /assets/img/{name}.webp 1600w" '
            f'sizes="{sizes}" alt="{E(alt)}" width="{w}" height="{h}" {load}>')


# --------------------------------------------------------------------------- blog prep
from posts_extra import EXTRA
for _p in POSTS_A + POSTS_B:
    if _p["slug"] in EXTRA:
        _i = _p["body"].rfind("<h2>")
        _p["body"] = _p["body"][:_i] + EXTRA[_p["slug"]] + _p["body"][_i:]
POSTS = sorted(POSTS_A + POSTS_B, key=lambda p: p["date"], reverse=True)
CAT_SLUGS = {}
for p in POSTS:
    p["cat_slug"] = re.sub(r"[^a-z0-9]+", "-", p["category"].lower()).strip("-")
    CAT_SLUGS[p["category"]] = p["cat_slug"]
    d = datetime.date.fromisoformat(p["date"])
    p["date_h"] = d.strftime("%b %-d, %Y")
    words = len(re.sub(r"<[^>]+>", " ", p["body"]).split()) + len(" ".join(p["takeaways"]).split()) + len(" ".join(q["q"] + " " + q["a"] for q in p["faq"]).split())
    p["words"] = words
    p["minutes"] = max(3, round(words / 230))
    # add ids to h2s and build toc
    toc = []

    def _id(m):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        sid = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
        toc.append((sid, text))
        return f'<h2 id="{sid}">{m.group(1)}</h2>'
    p["body"] = re.sub(r"<h2>(.*?)</h2>", _id, p["body"])
    p["toc"] = toc
    p.setdefault("niches", [])
POST = {p["slug"]: p for p in POSTS}


def posts_for(service=None, niche=None, n=3):
    scored = []
    for p in POSTS:
        s = 0
        if service and service in p["services"]:
            s += 3 - p["services"].index(service) * .5
        if niche and niche in p.get("niches", []):
            s += 4
        scored.append((s, p["date"], p))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [t[2] for t in scored[:n]]


def related_posts_block(ps, title="From the N3X playbook", dark=True):
    cards = "".join(post_card(p) for p in ps)
    cls = "sec sec--dark-cards" if dark else "sec related"
    return f"""<section class="{cls}">
  <div class="container">
    <div class="sec-head sec-head--split"><div><span class="tag">Insights</span><h2>{E(title)}</h2></div><a class="btn btn--ghost" href="/blog">All articles {ARROW()}</a></div>
    <div class="post-grid" data-stagger>{cards}</div>
  </div>
</section>"""


# --------------------------------------------------------------------------- HOME
HOME_FAQ = [
    {"q": "How is N3X Ventures different from a typical marketing agency?", "a": "We combine growth marketing with AI automation as one system, not two separate vendors — and every strategy is built for your specific industry, not a generic template."},
    {"q": "Do you work with businesses outside your listed industries?", "a": "Yes. Our 25 core industries are where we have the deepest playbooks, but our services apply to almost any business that depends on leads, sales, or brand authority."},
    {"q": "Can I start with just one service?", "a": "Absolutely. Many clients start with a single service like SEO or a website, then expand into automation and paid ads once they see results."},
    {"q": "How quickly will I see results?", "a": "It depends on the service — paid ads and automation can show movement within weeks, while SEO and organic content typically build over 60–90 days."},
    {"q": "Do you offer done-for-you services, or just consulting?", "a": "Done-for-you. Our team designs, builds, and manages everything — you get a strategy plus full execution, not a slide deck to implement yourself."},
    {"q": "Are there long-term contracts?", "a": "No. Every N3X Ventures plan is month-to-month and includes a free onboarding audit. We earn your business every month."},
    {"q": "Where is N3X Ventures based?", "a": "Our team operates from Lubbock, Texas, Atlanta, Georgia and Dubai, and we work with businesses across the United States remotely."},
]
HOME_SVC_COPY = {
    "ai-automation": "Chatbots, voice agents, lead qualification and CRM workflows that work while you sleep.",
    "paid-ads": "Google, Meta, LinkedIn, TikTok & YouTube campaigns built to convert — not just get clicks.",
    "seo-geo": "Rank in Google and get recommended by ChatGPT, Gemini & AI search — both channels, one strategy.",
    "lead-generation": "Cold outreach, funnels & nurture sequences that keep your calendar full of qualified calls.",
    "websites": "Fast, conversion-first websites and landing pages that sell while you're off the clock.",
    "social-media": "Strategy and daily management across Instagram, LinkedIn, Facebook, TikTok, X & YouTube.",
    "linkedin-marketing": "Founder-led content, profile optimization and outbound that turns LinkedIn into pipeline.",
    "content-creation": "Blog writing, copywriting and content calendars that build authority and get found.",
    "video-editing": "Short-form reels, long-form YouTube and podcast editing that keeps people watching.",
    "branding": "Identity, positioning & messaging that makes premium pricing feel obvious.",
}


def industry_cards(include_realty=True):
    def card(href, slugimg, cat, catname, name):
        return (f'<a class="ind-card" href="{href}" data-cat="{cat}"><img src="/assets/img/{slugimg}-sm.webp" alt="" loading="lazy" decoding="async" width="800" height="533">'
                f'<small>{E(catname)}</small><h3>{E(name)} {icon("arrow-up-right")}</h3></a>')
    cards = [card(f"/niches/{n[0]}", "ind-" + n[0], CAT_SLUG[n[3]], n[3], n[1]) for n in NICHES]
    cards.insert(21, card("/coaches", "ind-coaches", "b2b", "B2B & Online", "Coaches & Consultants"))
    if include_realty:
        cards.append(f'<a class="ind-card ind-card--realty" href="{REALTY_URL}" target="_blank" rel="noopener" data-cat="realty"><img src="{REALTY_LOGO}" alt="N3X Realty" width="110" height="26" loading="lazy"><div><small>Real estate agents &amp; brokerages</small><h3>Real estate has its own dedicated brand</h3><p>Websites, CRM &amp; AI lead systems built only for realtors — by our sister company N3X Realty.</p></div><span class="btn btn--ghost btn--sm">Visit N3X Realty {icon("arrow-up-right")}</span></a>')
    return "".join(cards)


def ind_filter():
    chips = '<button class="chip" data-filter="all" aria-pressed="true">All industries</button>' + "".join(
        f'<button class="chip" data-filter="{CAT_SLUG[c]}" aria-pressed="false">{E(c)}</button>' for c in CATS)
    return f'<div class="filter-bar" data-filter-group="#ind-grid" role="toolbar" aria-label="Filter industries">{chips}</div>'


def build_home():
    words = ["Dentists", "Lawyers", "Coaches", "Roofers", "Med Spas", "SaaS Founders", "Plumbers", "Contractors"]
    feed_rows = [("Roof inspection request", "Lubbock, TX", "Booked"), ("Invisalign consult", "Atlanta, GA", "Qualified"),
                 ("Emergency AC repair", "Dallas, TX", "Booked"), ("Free strategy call", "Austin, TX", "Booked"),
                 ("Personal injury intake", "Houston, TX", "Qualified"), ("Kitchen remodel quote", "Marietta, GA", "Booked")]
    rows = "".join(f'<div class="lead-row"><div><b>{E(a)}</b><br><span>{E(b)}</span></div><i>{E(c)}</i></div>' for a, b, c in feed_rows)
    # bento
    order = ["ai-automation", "seo-geo", "paid-ads", "lead-generation", "social-media", "websites", "linkedin-marketing", "content-creation", "video-editing", "branding"]
    layout = {"ai-automation": "bento-card--wide", "seo-geo": "bento-card--wide bento-card--accent",
              "websites": "bento-card--wide", "linkedin-marketing": "bento-card--wide"}
    bento = []
    for i, s in enumerate(order):
        sv = SVC[s]
        cls = layout.get(s, "")
        im = img("svc-" + s, "", sizes="(max-width:760px) 100vw, 50vw") if "photo" in cls else ""
        bento.append(f'<a class="bento-card {cls}" href="/services/{s}">{im}<span class="num">{i+1:02d}</span><span class="ico">{icon(sv["icon"])}</span><h3>{E(sv["name"])}</h3><p>{E(HOME_SVC_COPY[s])}</p><span class="link-arrow">Learn more {ARROW()}</span></a>')
    # last item to fill: CTA card
    why = [("trophy", "8+ years experience", "Founded in 2022 — but our core team has built and scaled growth systems for over 8 years."),
           ("zap", "AI-first approach", "Automation isn't an add-on. It's built into every service we deliver, from day one."),
           ("chart-column", "Results-focused", "We measure success in leads, bookings and revenue — not vanity metrics or busywork."),
           ("refresh-cw", "End-to-end service", "Strategy, design, tech, content and automation — one team, zero freelancer juggling.")]
    why_cards = "".join(f'<div class="card"><span class="ico">{icon(a)}</span><h3>{E(b)}</h3><p>{E(c)}</p></div>' for a, b, c in why)
    process = [{"title": "Discover", "text": "We learn your business, market and current gaps in a focused strategy session."},
               {"title": "Strategy", "text": "A custom growth roadmap with clear deliverables, timelines & KPIs — built for your industry."},
               {"title": "Execute", "text": "Our team builds — brand, funnels, content, automation — with speed and precision."},
               {"title": "Optimize", "text": "We track performance weekly and iterate fast on what's actually moving the needle."},
               {"title": "Scale", "text": "We double down on what's working and expand your systems as your business grows."}]
    cases = [("3.8", "x", 1, "Revenue growth in 6 months", "A life coach went from $4K to $15K/month after a full funnel, brand & content rebuild."),
             ("240", "%", 0, "More qualified calls", "A business coach's calendar went from 3 calls a week to 10+ with our lead system."),
             ("127", "K", 0, "Course launch revenue", "Generated in 10 days with our full-stack launch system for a mindset coach."),
             ("18", " hrs", 0, "Saved weekly on admin", "A wellness coach reclaimed 18 hours a week after we automated her business ops.")]
    case_cards = "".join(f'<div class="metric-card"><div class="stat-num" data-count="{a}" data-suffix="{b}" data-decimals="{d}" {"data-prefix=$" if b == "K" else ""}>{"$" if b == "K" else ""}{a}{b}</div><h3>{E(t)}</h3><p>{E(x)}</p></div>' for a, b, d, t, x in cases)
    testis = C["coaches"]["testimonials"]
    marquee_items = "".join(f'<a href="{niche_url(n[0])}">{E(n[1])}</a>' for n in NICHES) + '<a href="/coaches">Coaches</a>'
    body = f"""
<section class="hero">
  <div class="bg-grid"></div><div class="glow glow--mint"></div><div class="glow glow--azure"></div>
  <div class="container hero-grid">
    <div class="hero-enter">
      <span class="tag">AI &amp; growth marketing agency</span>
      <h1>Growth systems built for <span class="cycle"><span class="cycle-word" data-words='{json.dumps(words)}'>{words[0]}</span></span></h1>
      <p class="lead">N3X Ventures plugs AI automation, paid ads, SEO &amp; GEO, content and lead generation into one growth engine — built for the way your industry actually sells.</p>
      <div class="btn-row"><a class="btn btn--primary btn--lg" href="/contact" data-book>Book a free strategy call {ARROW()}</a><a class="btn btn--ghost btn--lg" href="/services">Explore services</a></div>
      <div class="hero-proof"><span>{icon("badge-check")}8+ years team experience</span><span>{icon("badge-check")}25+ industries served</span><span>{icon("badge-check")}Month-to-month, no lock-in</span></div>
    </div>
    <div class="engine hero-enter" aria-hidden="true">
      <div class="engine-card engine-float f1"><span class="ico">{icon("bot")}</span><div><strong>AI replied in 8 seconds</strong><span>New lead qualified &amp; booked</span></div></div>
      <div class="engine-card engine-main">
        <div class="engine-top"><div class="dots"><i></i><i></i><i></i></div><span class="live">LIVE GROWTH ENGINE</span></div>
        <div class="engine-kpis">
          <div class="kpi"><small>Leads / mo</small><strong>312</strong><em>▲ 48%</em></div>
          <div class="kpi"><small>Cost / lead</small><strong>$27</strong><em>▼ 31%</em></div>
          <div class="kpi"><small>Booked</small><strong>41%</strong><em>▲ 2.3×</em></div>
        </div>
        <div class="engine-chart"><svg viewBox="0 0 400 150" preserveAspectRatio="none"><defs><linearGradient id="lg" x1="0" x2="1"><stop offset="0" stop-color="#22e5b0"/><stop offset="1" stop-color="#0ea5ff"/></linearGradient><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22e5b0" stop-opacity=".28"/><stop offset="1" stop-color="#0ea5ff" stop-opacity="0"/></linearGradient></defs><path d="M0 128 C40 122 60 118 90 110 S150 112 180 92 S240 80 270 62 S330 44 360 30 S390 20 400 16 L400 150 L0 150Z" fill="url(#fill)"/><path class="line" d="M0 128 C40 122 60 118 90 110 S150 112 180 92 S240 80 270 62 S330 44 360 30 S390 20 400 16" fill="none" stroke="url(#lg)" stroke-width="3" stroke-linecap="round"/></svg></div>
        <div class="lead-feed"><div class="lead-feed-track">{rows}{rows}</div></div>
      </div>
      <div class="engine-card engine-float f2"><span class="ico">{icon("search")}</span><div><strong>Cited by AI search</strong><span>ChatGPT · Gemini · Perplexity</span></div></div>
    </div>
  </div>
</section>
<div class="marquee" aria-label="Industries we serve"><div class="marquee-track">{marquee_items}{marquee_items.replace('<a ', '<a tabindex="-1" aria-hidden="true" ')}</div></div>

<section class="sec" id="services">
  <div class="container">
    <div class="sec-head sec-head--split"><div><span class="tag">What we do</span><h2>Every growth lever, <span class="grad-text">under one roof</span></h2><p class="lead">Stop stitching together freelancers and disconnected tools. N3X Ventures runs strategy, execution and automation as one connected system.</p></div><a class="btn btn--ghost" href="/services">All services {ARROW()}</a></div>
    <div class="bento" data-stagger>{"".join(bento)}</div>
  </div>
</section>

<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">Why N3X Ventures</span><h2>Not a generic agency. <span class="grad-text">A growth partner.</span></h2><p class="lead">One accountable team that owns the outcome — from the first ad click to the booked appointment.</p></div>
    <div class="grid grid-4" data-stagger>{why_cards}</div>
    <div class="stats reveal" style="margin-top:28px">
      <div class="stat"><div class="stat-num" data-count="2022" data-plain="1">2022</div><div class="stat-label">Company founded</div></div>
      <div class="stat"><div class="stat-num" data-count="8" data-suffix="+ yrs">8+ yrs</div><div class="stat-label">Core team experience</div></div>
      <div class="stat"><div class="stat-num" data-count="25" data-suffix="+">25+</div><div class="stat-label">Industries served</div></div>
      <div class="stat"><div class="stat-num" data-count="3.8" data-decimals="1" data-suffix="×">3.8×</div><div class="stat-label">Avg. coaching client revenue lift</div></div>
    </div>
  </div>
</section>

{steps_block(process, "How we work", "From first call to compounding growth", sub="A simple, transparent process — you always know what's happening, what's next and what it's producing.")}

<section class="sec sec--deep" id="industries">
  <div class="container">
    <div class="sec-head sec-head--split"><div><span class="tag">Industries we serve</span><h2>Real strategies for <span class="grad-text">25 core industries</span></h2><p class="lead">No one-size-fits-all. Every industry gets messaging, offers and channels built around how its customers actually buy.</p></div><a class="btn btn--ghost" href="/industries">Explore industries {ARROW()}</a></div>
    {ind_filter()}
    <div class="ind-grid" id="ind-grid" data-stagger>{industry_cards()}</div>
  </div>
</section>

<section class="sec">
  <div class="container">
    <div class="spotlight reveal">
      <div class="spotlight-media">{img("ind-coaches", "Coach shaking hands with a client during a team strategy session", sizes="(max-width:1024px) 100vw, 50vw")}<div class="float"><div class="stat-num" data-count="3.8" data-decimals="1" data-suffix="×">3.8×</div><p>Average revenue increase for coaching clients within 6 months.</p></div></div>
      <div class="spotlight-body">
        <span class="tag">Featured program</span>
        <h2>Built for coaches &amp; course creators</h2>
        <p class="lead">You have transformative knowledge — but without the right systems, it stays invisible. We turn expertise into a scalable, fully booked coaching business.</p>
        <ul class="checks"><li>{icon("circle-check")}Funnel &amp; offer systems that convert cold traffic into calls</li><li>{icon("circle-check")}Personal brand &amp; content that positions you as the authority</li><li>{icon("circle-check")}Automation that nurtures, books and onboards without you</li></ul>
        <div class="btn-row"><a class="btn btn--primary" href="/coaches">Explore the coaches program {ARROW()}</a></div>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">Proof, not promises</span><h2>Real clients. <span class="grad-text">Real results.</span></h2></div>
    <div class="grid grid-4" data-stagger>{case_cards}</div>
    <div class="grid grid-2" style="margin-top:16px" data-stagger>{quote_cards(testis)}</div>
  </div>
</section>

{related_posts_block(POSTS[:3], "Fresh from the growth playbook")}
{faq_block(HOME_FAQ)}
{cta_block()}
"""
    title = "N3X Ventures — AI-Powered Growth Marketing Agency for US Businesses"
    desc = "AI automation, paid ads, SEO & GEO, lead generation, websites and branding for US businesses in 25+ industries. Book a free strategy call."
    write("/", page(title, desc, "/", body, schema=[faq_schema(HOME_FAQ), {"@type": "WebPage", "@id": BASE + "/#webpage", "url": BASE + "/", "name": title, "isPartOf": {"@id": BASE + "/#website"}, "about": {"@id": ORG_ID}, "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".hero h1", ".hero .lead"]}}]), priority="1.0")


# --------------------------------------------------------------------------- SERVICES
SVC_SEO_TITLE = {
    "ai-automation": "AI Automation Agency: Chatbots, Voice Agents & CRM | N3X Ventures",
    "paid-ads": "Paid Ads Agency: Google, Meta & LinkedIn Ads | N3X Ventures",
    "seo-geo": "SEO & GEO Agency: Rank on Google and AI Search | N3X Ventures",
    "lead-generation": "Lead Generation Agency: Outreach, Funnels & Nurture | N3X Ventures",
    "websites": "Website Design & Development for Small Business | N3X Ventures",
    "social-media": "Social Media Marketing & Management Agency | N3X Ventures",
    "linkedin-marketing": "LinkedIn Marketing Agency for B2B & Founders | N3X Ventures",
    "content-creation": "Content Creation & SEO Copywriting Agency | N3X Ventures",
    "video-editing": "Video Editing Services: Reels, YouTube & Podcasts | N3X Ventures",
    "branding": "Branding Agency: Identity, Positioning & Messaging | N3X Ventures",
}
SVC_NICHES = {
    "ai-automation": ["roofing", "hvac", "dentists", "med-spas", "lawyers", "insurance", "mortgage-brokers"],
    "paid-ads": ["roofing", "plumbing", "solar", "lawyers", "dentists", "ecommerce", "saas"],
    "seo-geo": ["roofing", "hvac", "plumbing", "dentists", "lawyers", "accounting", "chiropractors"],
    "lead-generation": ["saas", "it-msp", "recruitment", "marketing-agencies", "financial-advisors", "insurance"],
    "websites": ["remodeling", "landscaping", "med-spas", "plastic-surgeons", "lawyers", "ecommerce"],
    "social-media": ["med-spas", "dermatologists", "ecommerce", "landscaping", "remodeling", "physical-therapy"],
    "linkedin-marketing": ["saas", "it-msp", "recruitment", "accounting", "financial-advisors", "marketing-agencies"],
    "content-creation": ["saas", "lawyers", "financial-advisors", "accounting", "ecommerce", "dentists"],
    "video-editing": ["med-spas", "remodeling", "plastic-surgeons", "ecommerce", "landscaping", "solar"],
    "branding": ["plastic-surgeons", "lawyers", "med-spas", "financial-advisors", "saas", "remodeling"],
}


def build_service(slug):
    d = C["services"][slug]
    sv = SVC[slug]
    h = d["hero"]
    inc = d["included"]["items"]
    starter = d["pricing"]["plans"][0]["amount"]
    trail = [("Home", "/"), ("Services", "/services"), (sv["name"], f"/services/{slug}")]
    inc_cards = "".join(f'<div class="card"><span class="ico">{icon(emoji_icon(i["icon"]))}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p></div>' for i in inc)
    chips = "".join(f'<a href="/niches/{n}">{icon(NICHE[n]["icon"])}{E(NICHE[n]["name"])}</a>' for n in SVC_NICHES[slug]) + f'<a href="/coaches">{icon("graduation-cap")}Coaches</a><a href="/industries">{icon("layout-grid")}All industries</a>'
    others = [s for s in SVC if s != slug]
    other_cards = "".join(f'<a class="card" href="/services/{s}"><span class="ico">{icon(SVC[s]["icon"])}</span><h3>{E(SVC[s]["name"])}</h3><p>{E(SVC[s]["blurb"])}</p><span class="link-arrow">Explore {ARROW()}</span></a>' for s in others[:3] if True)
    # pick 3 complementary services
    comp = {"ai-automation": ["lead-generation", "websites", "paid-ads"], "paid-ads": ["websites", "ai-automation", "seo-geo"],
            "seo-geo": ["content-creation", "websites", "ai-automation"], "lead-generation": ["ai-automation", "linkedin-marketing", "paid-ads"],
            "websites": ["seo-geo", "branding", "paid-ads"], "social-media": ["video-editing", "content-creation", "branding"],
            "linkedin-marketing": ["content-creation", "lead-generation", "branding"], "content-creation": ["seo-geo", "social-media", "video-editing"],
            "video-editing": ["social-media", "content-creation", "paid-ads"], "branding": ["websites", "content-creation", "social-media"]}[slug]
    other_cards = "".join(f'<a class="card" href="/services/{s}"><span class="ico">{icon(SVC[s]["icon"])}</span><h3>{E(SVC[s]["name"])}</h3><p>{E(SVC[s]["blurb"])}</p><span class="link-arrow">Explore {ARROW()}</span></a>' for s in comp)
    quick = f"<strong>In short:</strong> N3X Ventures' {sv['name']} service covers {', '.join(i['title'] for i in inc[:3]).replace(' & ', ' and ')} and more — fully done-for-you, on month-to-month plans starting at {starter}/month."
    body = f"""
<section class="page-hero">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid">
    <div class="hero-enter">
      {crumbs(trail)}
      <span class="tag">{icon(sv["icon"])} {E(sv["name"])}</span>
      <h1>{E(h["h1"])}</h1>
      <p class="lead">{E(h["p"])}</p>
      <div class="btn-row"><a class="btn btn--primary btn--lg" href="/contact" data-book data-service="{E(sv['name'])}">Book a free strategy call {ARROW()}</a><a class="btn btn--ghost btn--lg" href="#packages">View packages</a></div>
      <div class="answer-box"><span class="ico">{icon("sparkles")}</span><p>{quick}</p></div>
    </div>
    <div class="hero-media hero-enter">
      <div class="frame">{img("svc-" + slug, sv["name"] + " services by N3X Ventures", eager=True)}</div>
      <div class="chip-float cf1"><span class="ico">{icon(emoji_icon(inc[0]["icon"]))}</span><div><strong>{E(inc[0]["title"])}</strong><span>{E(inc[0]["text"])}</span></div></div>
      <div class="chip-float cf2"><span class="ico">{icon("badge-dollar-sign")}</span><div><strong>From {E(starter)}/mo</strong><span>Month-to-month · no lock-in</span></div></div>
    </div>
  </div>
</section>
{compare_block(d["vs"])}
<section class="sec" id="included">
  <div class="container">
    <div class="sec-head"><span class="tag">What's included</span><h2>Everything inside our {E(sv["name"])} service</h2><p class="lead">One team handles strategy, execution and reporting — so nothing falls between the cracks.</p></div>
    <div class="grid grid-3" data-stagger>{inc_cards}</div>
  </div>
</section>
{steps_block(d["process"]["items"], "Our process", d["process"]["head"]["h2"], paper=True)}
{pricing_block(d["pricing"], service=sv["name"])}
<section class="sec sec--paper sec--tight">
  <div class="container">
    <div class="sec-head"><span class="tag">Industries</span><h2>{E(sv["name"])} tuned for your industry</h2><p class="lead">We adapt messaging, offers and channels to how your customers buy. Popular with:</p></div>
    <div class="chip-cloud reveal">{chips}</div>
  </div>
</section>
<section class="sec">
  <div class="container">
    <div class="sec-head"><span class="tag">Works even better with</span><h2>Pair it with</h2></div>
    <div class="grid grid-3" data-stagger>{other_cards}</div>
  </div>
</section>
{related_posts_block(posts_for(service=slug), "Learn more about " + sv["name"])}
{faq_block(d["faq"]["items"], d["faq"]["head"]["h2"])}
{cta_block(d["cta"]["h2"], d["cta"]["p"], service=sv["name"])}
"""
    prices = [int(re.sub(r"[^\d]", "", p["amount"])) for p in d["pricing"]["plans"]]
    svc_schema = {"@type": "Service", "@id": BASE + f"/services/{slug}#service", "name": sv["name"], "serviceType": sv["name"],
                  "description": h["p"], "provider": {"@id": ORG_ID}, "areaServed": {"@type": "Country", "name": "United States"},
                  "url": BASE + f"/services/{slug}",
                  "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": min(prices), "highPrice": max(prices), "offerCount": len(prices)},
                  "hasOfferCatalog": {"@type": "OfferCatalog", "name": f"{sv['name']} plans", "itemListElement": [
                      {"@type": "Offer", "name": p["name"], "price": int(re.sub(r"[^\d]", "", p["amount"])), "priceCurrency": "USD", "description": p["desc"],
                       "priceSpecification": {"@type": "UnitPriceSpecification", "price": int(re.sub(r"[^\d]", "", p["amount"])), "priceCurrency": "USD", "unitText": "MONTH"}} for p in d["pricing"]["plans"]]}}
    desc = clip(h['p'], 128) + f" Plans from {starter}/mo."
    write(f"/services/{slug}", page(SVC_SEO_TITLE[slug], desc, f"/services/{slug}", body, active="services",
          schema=[svc_schema, crumbs_schema(trail), faq_schema(d["faq"]["items"])], preload=f"/assets/img/svc-{slug}.webp"), priority="0.9")


def build_services_hub():
    trail = [("Home", "/"), ("Services", "/services")]
    groups = {"Growth": [], "Build & Automate": []}
    for s in SERVICES:
        sv = SVC[s[0]]
        d = C["services"][s[0]]
        starter = d["pricing"]["plans"][0]["amount"]
        groups[sv["group"]].append(f"""<a class="bento-card bento-card--photo" href="/services/{sv['slug']}" style="grid-column:span 1;min-height:340px">{img('svc-' + sv['slug'], '', sizes='(max-width:760px) 100vw, 33vw')}<span class="num">From {E(starter)}/mo</span><span class="ico">{icon(sv['icon'])}</span><h3>{E(sv['name'])}</h3><p>{E(d['hero']['h1'])}</p><span class="link-arrow">Explore {E(sv['name'])} {ARROW()}</span></a>""")
    sections = ""
    for gname, cards in groups.items():
        sub = "Channels that bring qualified demand to your door." if gname == "Growth" else "The systems, assets and automation that convert that demand."
        sections += f"""<section class="sec{' sec--deep' if gname != 'Growth' else ''}"><div class="container"><div class="sec-head"><span class="tag">{E(gname)}</span><h2>{E(gname)} services</h2><p class="lead">{sub}</p></div><div class="bento" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr))" data-stagger>{''.join(cards)}</div></div></section>"""
    body = f"""
<section class="page-hero page-hero--center">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid"><div class="hero-enter">
    {crumbs(trail)}
    <span class="tag">10 services · 1 team</span>
    <h1>Every growth lever, <span class="grad-text">one accountable team</span></h1>
    <p class="lead">From AI automation to SEO, GEO, paid ads and branding — pick one service or combine them into a complete growth engine. Every plan is month-to-month.</p>
    <div class="btn-row"><a class="btn btn--primary btn--lg" href="/contact" data-book>Help me choose {ARROW()}</a></div>
  </div></div>
</section>
{sections}
{steps_block([{"title": "Discover", "text": "A free strategy call to understand your business, goals and gaps."}, {"title": "Roadmap", "text": "A custom plan showing which services move the needle first."}, {"title": "Build", "text": "Our team executes fast — usually live within weeks, not months."}, {"title": "Grow", "text": "Weekly optimization and monthly reporting tied to revenue."}], "How it works", "Not sure where to start? That's what the first call is for.", paper=True)}
{faq_block(HOME_FAQ[:5])}
{cta_block("Not sure which service you need?", "Tell us about your business and goals. We'll recommend the highest-impact starting point — even if it's just one service.")}
"""
    items = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + f"/services/{s[0]}", "name": s[1]} for i, s in enumerate(SERVICES)]}
    write("/services", page("Marketing, AI Automation & Web Services | N3X Ventures", "10 done-for-you growth services: AI automation, paid ads, SEO & GEO, lead gen, websites, social, LinkedIn, content, video and branding.", "/services", body, active="services", schema=[crumbs_schema(trail), items, faq_schema(HOME_FAQ[:5])]), priority="0.9")


# --------------------------------------------------------------------------- NICHES
NICHE_ADJ = {"roofing": "Roofing", "hvac": "HVAC", "plumbing": "Plumbing", "electrical": "Electrician", "solar": "Solar",
             "landscaping": "Landscaping", "remodeling": "Remodeling", "dentists": "Dental", "med-spas": "Med Spa",
             "plastic-surgeons": "Plastic Surgery", "dermatologists": "Dermatology", "chiropractors": "Chiropractic",
             "physical-therapy": "Physical Therapy", "lawyers": "Law Firm", "financial-advisors": "Financial Advisor",
             "insurance": "Insurance Agency", "mortgage-brokers": "Mortgage Broker", "accounting": "Accounting Firm",
             "saas": "SaaS", "ecommerce": "E-commerce", "marketing-agencies": "Agency", "recruitment": "Recruitment Agency", "it-msp": "MSP & IT"}


def build_niche(slug):
    d = C["niches"][slug]
    nv = NICHE[slug]
    h = d["hero"]
    trail = [("Home", "/"), ("Industries", "/industries"), (nv["name"], f"/niches/{slug}")]
    starter = d["pricing"]["plans"][0]["amount"]
    pains = "".join(f'<div class="card pain"><span class="ico">{icon(emoji_icon(i["icon"], "circle-alert"))}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p></div>' for i in d["pains"]["items"])
    svc_cards = []
    for i in d["included"]["items"]:
        link = svc_for_title(i["title"]) or (i["href"].split("/")[-1].replace(".html", "") if i.get("href") else None)
        if link:
            svc_cards.append(f'<a class="card" href="/services/{link}"><span class="ico">{icon(emoji_icon(i["icon"]))}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p><span class="link-arrow">{E(SVC[link]["name"])} {ARROW()}</span></a>')
        else:
            svc_cards.append(f'<div class="card"><span class="ico">{icon(emoji_icon(i["icon"]))}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p></div>')
    siblings = [n for n in NICHES if n[3] == nv["cat"] and n[0] != slug]
    sib = "".join(f'<a href="/niches/{n[0]}">{icon(n[4])}{E(n[1])}</a>' for n in siblings) + f'<a href="/industries">{icon("layout-grid")}All industries</a>'
    top3 = [x["title"] for x in d["included"]["items"][:3]]
    quick = f"<strong>In short:</strong> N3X Ventures helps {nv['aud']} win more customers with {top3[0]}, {top3[1]} and {top3[2]} — done-for-you, with plans from {starter}/month and no long-term contract."
    adj = NICHE_ADJ[slug]
    title = f"{adj} Marketing Agency — Leads, SEO & AI | N3X Ventures" if slug != "marketing-agencies" else "Growth & White-Label Partner for Marketing Agencies | N3X Ventures"
    body = f"""
<section class="page-hero">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid">
    <div class="hero-enter">
      {crumbs(trail)}
      <span class="tag">{icon(nv["icon"])} {E(strip_emoji(h["eyebrow"]))}</span>
      <h1>{E(h["h1"])}</h1>
      <p class="lead">{E(h["p"])}</p>
      <div class="btn-row"><a class="btn btn--primary btn--lg" href="/contact" data-book data-niche="{E(nv['book'])}">Book a free strategy call {ARROW()}</a><a class="btn btn--ghost btn--lg" href="#solutions">See how we help</a></div>
      <div class="answer-box"><span class="ico">{icon("sparkles")}</span><p>{quick}</p></div>
    </div>
    <div class="hero-media hero-enter">
      <div class="frame">{img("ind-" + slug, f"Marketing for {nv['aud']} — N3X Ventures", eager=True)}</div>
      <div class="chip-float cf1"><span class="ico">{icon("bot")}</span><div><strong>Every lead answered in &lt;60s</strong><span>AI text &amp; call follow-up, 24/7</span></div></div>
      <div class="chip-float cf2"><span class="ico">{icon(nv["icon"])}</span><div><strong>Built for {E(nv["name"])}</strong><span>Plans from {E(starter)}/mo</span></div></div>
    </div>
  </div>
</section>
<section class="sec sec--deep">
  <div class="container">
    <div class="sec-head"><span class="tag">Common struggles</span><h2>{E(d["pains"]["head"]["h2"])}</h2><p class="lead">If any of these sound familiar, you're not alone — and every one of them is fixable.</p></div>
    <div class="grid grid-4" data-stagger>{pains}</div>
  </div>
</section>
<div id="solutions"></div>
{compare_block(d["vs"], "Our approach", d["vs"]["head"]["h2"])}
<section class="sec">
  <div class="container">
    <div class="sec-head"><span class="tag">Relevant services</span><h2>{E(d["included"]["head"]["h2"])}</h2><p class="lead">{E(d["included"]["head"]["p"] or "Only what actually moves the needle in your industry.")}</p></div>
    <div class="grid grid-3" data-stagger>{"".join(svc_cards)}</div>
  </div>
</section>
{pricing_block(d["pricing"], niche=nv["book"])}
{related_posts_block(posts_for(niche=slug), "Playbooks for " + nv["aud"])}
{faq_block(d["faq"]["items"], d["faq"]["head"]["h2"])}
<section class="sec sec--paper sec--tight" style="padding-top:0">
  <div class="container">
    <div class="sec-head"><span class="tag">Related industries</span><h2>More {E(nv["cat"].lower())} we serve</h2></div>
    <div class="chip-cloud reveal">{sib}</div>
  </div>
</section>
{cta_block(d["cta"]["h2"], d["cta"]["p"], niche=nv["book"])}
"""
    svc_schema = {"@type": "Service", "name": f"Growth marketing for {nv['aud']}", "serviceType": "Digital marketing", "audience": {"@type": "BusinessAudience", "name": nv["aud"].capitalize()},
                  "provider": {"@id": ORG_ID}, "areaServed": {"@type": "Country", "name": "United States"}, "description": h["p"], "url": BASE + f"/niches/{slug}",
                  "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": int(re.sub(r"[^\d]", "", starter)), "highPrice": int(re.sub(r"[^\d]", "", d["pricing"]["plans"][-1]["amount"])), "offerCount": 3}}
    desc = clip(h['p'], 130) + f" Plans from {starter}/mo."
    write(f"/niches/{slug}", page(title, desc, f"/niches/{slug}", body, active="industries",
          schema=[svc_schema, crumbs_schema(trail), faq_schema(d["faq"]["items"])], preload=f"/assets/img/ind-{slug}.webp"), priority="0.8")


def build_industries_hub():
    trail = [("Home", "/"), ("Industries", "/industries")]
    cat_sections = ""
    for c in CATS:
        items = [NICHE[n[0]] for n in NICHES if n[3] == c]
        cards = "".join(f'<a class="card" href="/niches/{n["slug"]}"><span class="ico">{icon(n["icon"])}</span><h3>{E(n["name"])}</h3><p>{E(clip(C["niches"][n["slug"]]["hero"]["h1"], 90))}</p><span class="link-arrow">See the playbook {ARROW()}</span></a>' for n in items)
        if c == "B2B & Online":
            cards += f'<a class="card" href="/coaches"><span class="ico">{icon("graduation-cap")}</span><h3>Coaches &amp; Consultants</h3><p>{E(C["coaches"]["hero"]["h1"])}</p><span class="link-arrow">See the program {ARROW()}</span></a>'
        cat_sections += f'<div style="margin-top:48px"><h3 style="font-size:1.5rem;margin-bottom:18px">{E(c)}</h3><div class="grid grid-3" data-stagger>{cards}</div></div>'
    body = f"""
<section class="page-hero page-hero--center">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid"><div class="hero-enter">
    {crumbs(trail)}
    <span class="tag">25 industry playbooks</span>
    <h1>Marketing that speaks <span class="grad-text">your industry's language</span></h1>
    <p class="lead">A roofer, a dentist and a SaaS founder don't sell the same way — so we don't market them the same way. Find your industry below.</p>
  </div></div>
</section>
<section class="sec sec--deep" style="padding-top:24px">
  <div class="container">
    {ind_filter()}
    <div class="ind-grid" id="ind-grid" data-stagger>{industry_cards()}</div>
  </div>
</section>
<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head"><span class="tag">Browse by category</span><h2>Every industry, at a glance</h2><p class="lead">Each playbook covers the specific problems, channels, services and pricing for that industry.</p></div>
    {cat_sections}
  </div>
</section>
{cta_block("Don't see your industry?", "Our services work for almost any business that depends on leads, sales or brand authority. Tell us about yours.")}
"""
    items = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + f"/niches/{n[0]}", "name": n[1]} for i, n in enumerate(NICHES)]}
    write("/industries", page("Industries We Serve — 25 Marketing Playbooks | N3X Ventures", "Industry-specific growth marketing for home services, healthcare, legal & financial, B2B, SaaS, e-commerce and coaches. Find your industry's playbook.", "/industries", body, active="industries", schema=[crumbs_schema(trail), items]), priority="0.9")


# --------------------------------------------------------------------------- COACHES
def build_coaches():
    d = C["coaches"]
    h = d["hero"]
    trail = [("Home", "/"), ("Industries", "/industries"), ("Coaches", "/coaches")]
    stats = "".join(f'<div class="stat"><div class="stat-num" data-count="{s["count"]}" data-suffix="{E(s["suffix"])}" {"data-decimals=" + chr(34) + s["decimals"] + chr(34) if s["decimals"] else ""} {"data-prefix=$" if s["suffix"] == "K" else ""}>{"$" if s["suffix"] == "K" else ""}{s["count"]}{E(s["suffix"])}</div><div class="stat-label">{E(s["label"])}</div></div>' for s in d["stats"])
    pains = "".join(f'<div class="card pain"><span class="ico">{icon(emoji_icon(i["icon"], "circle-alert"))}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p></div>' for i in d["pains"]["items"])
    svc = "".join(f'<a class="card" href="/services/{svc_for_title(i["title"]) or "branding"}"><span class="ico">{icon(emoji_icon(i["icon"]))}</span><h3>{E(i["title"])}</h3><p>{E(i["text"])}</p><span class="link-arrow">Learn more {ARROW()}</span></a>' for i in d["included"]["items"])
    body = f"""
<section class="page-hero">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid">
    <div class="hero-enter">
      {crumbs(trail)}
      <span class="tag">{icon("graduation-cap")} For coaches &amp; course creators</span>
      <h1>{E(h["h1"])}</h1>
      <p class="lead">{E(h["p"])}</p>
      <div class="btn-row"><a class="btn btn--primary btn--lg" href="/contact" data-book data-niche="Coaches &amp; Consultants">Book a free strategy call {ARROW()}</a><a class="btn btn--ghost btn--lg" href="#packages">View packages</a></div>
    </div>
    <div class="hero-media hero-enter">
      <div class="frame">{img("ind-coaches", "Coach shaking hands with a client during a team strategy session", eager=True)}</div>
      <div class="chip-float cf1"><span class="ico">{icon("calendar-check")}</span><div><strong>10+ calls a week</strong><span>From 3 — with our lead system</span></div></div>
      <div class="chip-float cf2"><span class="ico">{icon("trending-up")}</span><div><strong>$127K launch</strong><span>In 10 days for a mindset coach</span></div></div>
    </div>
  </div>
</section>
<section class="sec sec--tight" style="padding-top:0"><div class="container"><div class="stats reveal">{stats}</div></div></section>
<section class="sec sec--deep">
  <div class="container">
    <div class="sec-head"><span class="tag">Sound familiar?</span><h2>{E(d["pains"]["head"]["h2"])}</h2><p class="lead">{E(d["pains"]["head"]["p"])}</p></div>
    <div class="grid grid-3" data-stagger>{pains}</div>
  </div>
</section>
{compare_block(d["vs"], "Our approach", "Your problems, mapped to real solutions")}
<section class="sec">
  <div class="container">
    <div class="sec-head"><span class="tag">Built for you</span><h2>{E(d["included"]["head"]["h2"])}</h2></div>
    <div class="grid grid-3" data-stagger>{svc}</div>
  </div>
</section>
{steps_block(d["process"]["items"], "The process", d["process"]["head"]["h2"], paper=True)}
{pricing_block(d["pricing"], niche="Coaches & Consultants")}
<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">Client wins</span><h2>Real coaches. <span class="grad-text">Real results.</span></h2></div>
    <div class="grid grid-2" data-stagger>{quote_cards(d["testimonials"])}</div>
  </div>
</section>
{related_posts_block(posts_for(niche="coaches"), "Playbooks for coaches")}
{faq_block(d["faq"]["items"], d["faq"]["head"]["h2"])}
{cta_block(d["cta"]["h2"], d["cta"]["p"], niche="Coaches & Consultants")}
"""
    svc_schema = {"@type": "Service", "name": "Marketing & growth systems for coaches", "provider": {"@id": ORG_ID}, "audience": {"@type": "Audience", "name": "Coaches, consultants and course creators"},
                  "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": 699, "highPrice": 2999, "offerCount": 3}, "url": BASE + "/coaches"}
    write("/coaches", page("Marketing for Coaches & Course Creators | N3X Ventures", clip(h["p"], 158), "/coaches", body, active="coaches",
          schema=[svc_schema, crumbs_schema(trail), faq_schema(d["faq"]["items"])], preload="/assets/img/ind-coaches.webp"), priority="0.9")


# --------------------------------------------------------------------------- ABOUT
def build_about():
    trail = [("Home", "/"), ("About", "/about")]
    tl = [("Discovery & audit", "We start by understanding your business, customers and current digital presence — identifying exactly where revenue is being left on the table."),
          ("Custom growth roadmap", "You get a 90-day plan with clear deliverables, timelines and KPIs — built for your specific industry, not a generic template."),
          ("Build & launch", "Our in-house team executes: brand, website, funnels, content, ads and automation — live and working within days, not months."),
          ("Weekly optimization", "We track performance every week, kill what isn't working and double down on what is — fast iteration beats a perfect plan."),
          ("Scale", "Once your systems are proven, we expand budget and channels methodically, compounding results instead of resetting them.")]
    tl_html = "".join(f'<div class="tl-item reveal"><div class="step-num">{i+1:02d}</div><div><h3>{E(a)}</h3><p>{E(b)}</p></div></div>' for i, (a, b) in enumerate(tl))
    values = [("chart-column", "Results over reports", "We're judged on leads and revenue, not activity logs."), ("zap", "Speed with precision", "Fast execution — without cutting corners on quality."),
              ("handshake", "Radical transparency", "You always know what's working, what isn't, and why."), ("brain", "AI-native thinking", "We build automation into everything, not bolt it on later.")]
    val_html = "".join(f'<div class="card"><span class="ico">{icon(a)}</span><h3>{E(b)}</h3><p>{E(c)}</p></div>' for a, b, c in values)
    body = f"""
<section class="page-hero page-hero--center">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid"><div class="hero-enter">
    {crumbs(trail)}
    <span class="tag">About N3X Ventures</span>
    <h1>One team. Three focused brands. <span class="grad-text">One growth mission.</span></h1>
    <p class="lead">N3X was founded in 2022 — but our core team carries over 8 years of hands-on experience building marketing, automation and technology systems that actually move revenue.</p>
  </div></div>
</section>
<section class="sec sec--tight" style="padding-top:0"><div class="container"><div class="photo-band reveal">{img("pg-about", "The N3X Ventures team planning a growth strategy at a whiteboard", sizes="100vw", eager=True)}</div></div></section>
<section class="sec sec--tight">
  <div class="container mv" data-stagger>
    <div class="card"><span class="ico">{icon("target")}</span><h3>Our mission</h3><p>To give every business — regardless of size or industry — access to the same AI-powered growth infrastructure that only enterprise companies could once afford. We turn expertise, products and services into predictable, scalable revenue.</p></div>
    <div class="card"><span class="ico">{icon("telescope")}</span><h3>Our vision</h3><p>A world where growth isn't guesswork. Where every dentist, lawyer, coach and contractor has a marketing engine as sophisticated as the biggest brands in their industry — built, managed and optimized by one accountable team.</p></div>
  </div>
</section>
<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">The N3X family</span><h2>One parent company, <span class="grad-text">three focused brands</span></h2><p class="lead">N3X was built as a parent company from day one — each brand goes deep on one mission instead of spreading thin across all of them.</p></div>
    <div class="family">
      <div class="family-root reveal"><img src="/assets/brand/n3x-logo-mark.webp" alt="N3X" width="200" height="132" loading="lazy" style="height:72px"><p>The parent company — growth marketing, AI automation &amp; brand strategy for every industry.</p></div>
      <div class="family-branches" data-stagger>
        <div class="family-branch family-branch--self"><div class="mark"><img src="{LOGO}" alt="N3X Ventures" width="150" height="35" loading="lazy"></div><h3>N3X Ventures <span class="you">You are here</span></h3><p>E-commerce, coaching, and marketing, branding &amp; content services for businesses across every field.</p></div>
        <a class="family-branch" href="{REALTY_URL}" target="_blank" rel="noopener"><div class="mark" style="background:var(--ink-900);border-radius:10px;padding:6px 10px;width:max-content"><img src="{REALTY_LOGO}" alt="N3X Realty" width="130" height="34" loading="lazy" style="height:26px"></div><h3>N3X Realty</h3><p>A dedicated real estate growth platform — websites, CRM and AI systems built for agents and brokerages.</p></a>
        <div class="family-branch"><div class="mark"><span class="mono-mark">N3X <span class="grad-text">Chain</span></span></div><h3>N3X Chain</h3><p>Blockchain infrastructure &amp; AI application development — our technology and engineering arm.</p></div>
      </div>
    </div>
  </div>
</section>
<section class="sec">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">How we work</span><h2>A workflow built for <span class="grad-text">clarity and speed</span></h2></div>
    <div class="timeline">{tl_html}</div>
  </div>
</section>
<section class="sec sec--paper">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">What we stand for</span><h2>Our values</h2></div>
    <div class="grid grid-4" data-stagger>{val_html}</div>
    <div class="stats reveal" style="margin-top:28px">
      <div class="stat"><div class="stat-num" data-count="2022" data-plain="1">2022</div><div class="stat-label">Company founded</div></div>
      <div class="stat"><div class="stat-num" data-count="8" data-suffix="+ yrs">8+ yrs</div><div class="stat-label">Team experience</div></div>
      <div class="stat"><div class="stat-num" data-count="3">3</div><div class="stat-label">Brands under N3X</div></div>
      <div class="stat"><div class="stat-num" data-count="25" data-suffix="+">25+</div><div class="stat-label">Industries served</div></div>
    </div>
  </div>
</section>
<section class="sec sec--tight">
  <div class="container">
    <div class="sec-head u-center"><span class="tag">Where we work</span><h2>Three hubs, serving the US</h2></div>
    <div class="grid grid-3" data-stagger>
      <div class="card"><span class="ico">{icon("map-pin")}</span><h3>Lubbock, Texas</h3><p>Headquarters and home-services growth hub.</p></div>
      <div class="card"><span class="ico">{icon("map-pin")}</span><h3>Atlanta, Georgia</h3><p>Client strategy, healthcare and professional services.</p></div>
      <div class="card"><span class="ico">{icon("map-pin")}</span><h3>Dubai, UAE</h3><p>Creative, engineering and AI automation team.</p></div>
    </div>
  </div>
</section>
{cta_block("Let's build your growth system", "Tell us about your business and we'll show you exactly where N3X Ventures can move the needle.")}
"""
    about_schema = {"@type": "AboutPage", "url": BASE + "/about", "name": "About N3X Ventures", "about": {"@id": ORG_ID}}
    write("/about", page("About N3X Ventures — AI Growth Marketing Team", "N3X Ventures is part of the N3X family of brands. Founded in 2022 with 8+ years of team experience building marketing, AI automation and technology systems.", "/about", body, active="about", schema=[about_schema, crumbs_schema(trail)]), priority="0.7")


# --------------------------------------------------------------------------- CONTACT
def build_contact():
    trail = [("Home", "/"), ("Contact", "/contact")]
    svc_opts = "".join(f"<option>{E(s[1])}</option>" for s in SERVICES) + "<option>Not sure yet</option>"
    ind_opts = "".join(f"<option>{E(n[1])}</option>" for n in NICHES) + "<option>Coaches &amp; Consultants</option><option>Real Estate</option><option>Other</option>"
    body = f"""
<section class="page-hero">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container">
    {crumbs(trail)}
    <div class="contact-grid">
      <div class="hero-enter">
        <span class="tag">Contact</span>
        <h1>Let's talk <span class="grad-text">growth</span></h1>
        <p class="lead">Book a free 30-minute strategy call, send us a message, or reach out on WhatsApp. A real strategist replies within one business day.</p>
        <div class="btn-row" style="margin-bottom:28px"><a class="btn btn--primary btn--lg" href="#book" data-book>Book a strategy call {ARROW()}</a></div>
        <div class="contact-list">
          <a class="contact-item" href="tel:{PHONE_E164}"><span class="ico">{icon("phone")}</span><span><small>Call us</small><strong>{PHONE}</strong></span></a>
          <a class="contact-item" href="{WA}" target="_blank" rel="noopener"><span class="ico">{icon("message-circle")}</span><span><small>WhatsApp</small><strong>Chat with a strategist</strong></span></a>
          <a class="contact-item" href="mailto:{EMAIL}"><span class="ico">{icon("mail")}</span><span><small>Email</small><strong>{EMAIL}</strong></span></a>
          <div class="contact-item"><span class="ico">{icon("map-pin")}</span><span><small>Locations</small><strong>{" · ".join(LOCATIONS)}</strong></span></div>
        </div>
      </div>
      <div class="form-card hero-enter">
        <h2>Send us a message</h2>
        <p style="color:var(--ink-muted)">Tell us a little about your business — we'll come prepared.</p>
        <form id="contact-form" novalidate>
          <div class="field-row"><div class="field"><label for="c-name">Full name</label><input id="c-name" name="name" required autocomplete="name"></div><div class="field"><label for="c-company">Company</label><input id="c-company" name="company" autocomplete="organization"></div></div>
          <div class="field-row"><div class="field"><label for="c-email">Email</label><input id="c-email" type="email" name="email" required autocomplete="email"></div><div class="field"><label for="c-phone">Phone</label><input id="c-phone" type="tel" name="phone" autocomplete="tel"></div></div>
          <div class="field-row"><div class="field"><label for="c-service">Service</label><select id="c-service" name="service">{svc_opts}</select></div><div class="field"><label for="c-ind">Industry</label><select id="c-ind" name="industry">{ind_opts}</select></div></div>
          <div class="field"><label for="c-msg">What are you hoping to achieve?</label><textarea id="c-msg" name="message" required></textarea></div>
          <button class="btn btn--dark btn--lg btn--block" type="submit">Send message {ARROW()}</button>
          <p class="form-status" role="status" aria-live="polite"></p>
        </form>
      </div>
    </div>
  </div>
</section>
{faq_block(HOME_FAQ[2:7], "Before you reach out")}
"""
    cp = {"@type": "ContactPage", "url": BASE + "/contact", "name": "Contact N3X Ventures", "about": {"@id": ORG_ID}}
    write("/contact", page("Contact N3X Ventures — Book a Free Strategy Call", f"Book a free 30-minute strategy call with N3X Ventures. Call {PHONE}, WhatsApp us, or email {EMAIL}. Lubbock · Atlanta · Dubai.", "/contact", body, active="contact", schema=[cp, crumbs_schema(trail), faq_schema(HOME_FAQ[2:7])]), priority="0.8")


# --------------------------------------------------------------------------- BLOG
def build_blog_index():
    trail = [("Home", "/"), ("Blog", "/blog")]
    feat = POSTS[0]
    cats = []
    for p in POSTS:
        if p["category"] not in cats:
            cats.append(p["category"])
    chips = '<button class="chip" data-filter="all" aria-pressed="true">All topics</button>' + "".join(f'<button class="chip" data-filter="{CAT_SLUGS[c]}" aria-pressed="false">{E(c)}</button>' for c in cats)
    grid = "".join(post_card(p) for p in POSTS[1:])
    body = f"""
<section class="page-hero page-hero--center">
  <div class="bg-grid"></div><div class="glow glow--mint"></div>
  <div class="container page-hero-grid"><div class="hero-enter">
    {crumbs(trail)}
    <span class="tag">The N3X growth playbook</span>
    <h1>Practical growth insights <span class="grad-text">for busy owners</span></h1>
    <p class="lead">No fluff. Field-tested guides on AI automation, SEO &amp; GEO, paid ads, lead generation and branding — written by the team that does the work.</p>
  </div></div>
</section>
<section class="sec sec--paper">
  <div class="container">
    <a class="post-feature reveal" href="/blog/{feat['slug']}">
      <div class="media">{img(feat['image'], feat['image_alt'], sizes="(max-width:1024px) 100vw, 60vw", eager=True)}</div>
      <div class="body"><div class="post-meta"><span class="cat">{E(feat['category'])}</span><span>Latest</span><span class="dot"></span><span>{feat['minutes']} min read</span></div><h2>{E(feat['title'])}</h2><p>{E(feat['description'])}</p><span class="btn btn--dark" style="align-self:flex-start">Read the guide {ARROW()}</span></div>
    </a>
    <div class="filter-bar" data-filter-group="#post-grid" role="toolbar" aria-label="Filter articles by topic">{chips}</div>
    <div class="post-grid" id="post-grid" data-stagger>{grid}</div>
  </div>
</section>
{cta_block("Rather have experts do it for you?", "Reading is great. Results are better. Book a free strategy call and we'll apply these playbooks to your business.")}
"""
    blog_schema = {"@type": "Blog", "@id": BASE + "/blog#blog", "url": BASE + "/blog", "name": "N3X Ventures Blog", "publisher": {"@id": ORG_ID},
                   "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": BASE + f"/blog/{p['slug']}", "datePublished": p["date"]} for p in POSTS]}
    write("/blog", page("Blog — AI, SEO, GEO & Growth Marketing Guides | N3X Ventures", "Field-tested guides on AI automation, SEO & GEO, paid ads, lead generation, websites and branding for US service businesses.", "/blog", body, active="blog", schema=[blog_schema, crumbs_schema(trail)]), priority="0.8")


def build_post(p):
    trail = [("Home", "/"), ("Blog", "/blog"), (p["category"], "/blog"), (p["title"], f"/blog/{p['slug']}")]
    toc = "".join(f'<li><a href="#{sid}">{E(t)}</a></li>' for sid, t in p["toc"])
    tk = "".join(f"<li>{icon('check')}<span>{E(t)}</span></li>" for t in p["takeaways"])
    main_svc = SVC[p["services"][0]]
    inline_cta = f'<div class="inline-cta"><div><h3>Want this done for you?</h3><p>Our {E(main_svc["name"])} team builds and runs it end to end.</p></div><a class="btn btn--primary" href="/services/{main_svc["slug"]}">Explore {E(main_svc["name"])} {ARROW()}</a></div>'
    body_html = p["body"]
    # insert inline CTA roughly mid-article (before the 4th h2)
    parts = re.split(r"(?=<h2 )", body_html)
    if len(parts) > 4:
        parts.insert(4, inline_cta)
    body_html = "".join(parts)
    faq = "".join(f'<details><summary>{E(q["q"])}<span class="pm">{icon("plus")}</span></summary><div class="answer"><p>{E(q["a"])}</p></div></details>' for q in p["faq"])
    related = [x for x in POSTS if x["slug"] != p["slug"] and (set(x["services"]) & set(p["services"]))][:3]
    if len(related) < 3:
        related += [x for x in POSTS if x["slug"] != p["slug"] and x not in related][:3 - len(related)]
    svc_links = " · ".join(f'<a href="/services/{s}">{E(SVC[s]["name"])}</a>' for s in p["services"])
    share_url = html.escape(BASE + f"/blog/{p['slug']}")
    upd = p.get("updated", p["date"])
    body = f"""
<div class="read-progress" aria-hidden="true"></div>
<article itemscope itemtype="https://schema.org/BlogPosting">
<header class="article-head">
  <div class="container" style="max-width:1100px">
    {crumbs(trail[:3] + [(trail[3][0], trail[3][1])])}
    <div class="post-meta" style="margin-bottom:18px"><span class="cat">{E(p['category'])}</span><time datetime="{p['date']}">{p['date_h']}</time><span class="dot"></span><span>{p['minutes']} min read</span></div>
    <h1 itemprop="headline">{E(p['title'])}</h1>
    <p class="dek" itemprop="description">{E(p['description'])}</p>
    <div class="byline">
      <span class="avatar"><img src="/assets/brand/favicon-192.png" alt="" width="28" height="28"></span>
      <div><strong>N3X Ventures Growth Team</strong><span>Reviewed by our strategy leads · Updated <time datetime="{upd}">{datetime.date.fromisoformat(upd).strftime('%B %-d, %Y')}</time></span></div>
      <div class="share">
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" target="_blank" rel="noopener" aria-label="Share on LinkedIn">{icon("linkedin")}</a>
        <a href="https://twitter.com/intent/tweet?url={share_url}&amp;text={html.escape(p['title'])}" target="_blank" rel="noopener" aria-label="Share on X">{icon("twitter")}</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" rel="noopener" aria-label="Share on Facebook">{icon("facebook")}</a>
        <button type="button" data-copy-link aria-label="Copy link">{icon("link")}</button>
      </div>
    </div>
    <figure class="article-cover" style="margin-bottom:0">{img(p['image'], p['image_alt'], sizes="(max-width:1100px) 100vw, 1100px", eager=True)}</figure>
  </div>
</header>
<div class="article-wrap">
  <div class="container" style="max-width:1240px">
    <div class="article-layout">
      <aside class="article-aside">
        <nav class="toc" aria-label="Table of contents"><details open><summary><h2>On this page</h2></summary><ol>{toc}</ol></details>
        <div class="toc-cta"><strong>Free strategy call</strong><p>Get a custom growth roadmap for your business in 30 minutes.</p><a class="btn btn--primary btn--sm btn--block" href="/contact" data-book>Book a call</a></div></nav>
      </aside>
      <div>
        <div class="prose" itemprop="articleBody">
          <section class="takeaways" aria-labelledby="tk"><h2 id="tk">Key takeaways</h2><ul>{tk}</ul></section>
          {body_html}
          <section class="article-faq faq" aria-labelledby="faq-h"><h2 id="faq-h">Frequently asked questions</h2>{faq}</section>
          <div class="author-box"><span class="avatar"><img src="/assets/brand/favicon-192.png" alt="" width="36" height="36"></span><div><strong>About N3X Ventures</strong><p>N3X Ventures is an AI-powered growth marketing agency serving US businesses across 25+ industries from Lubbock, Atlanta and Dubai. Related services: {svc_links}.</p></div></div>
        </div>
      </div>
      <aside class="article-aside"></aside>
    </div>
  </div>
</div>
</article>
<section class="sec related">
  <div class="container">
    <div class="sec-head sec-head--split"><div><span class="tag">Keep reading</span><h2>Related articles</h2></div><a class="btn btn--outline-dark" href="/blog">All articles {ARROW()}</a></div>
    <div class="post-grid" data-stagger>{"".join(post_card(r) for r in related)}</div>
  </div>
</section>
<div style="background:var(--paper)">{cta_block()}</div>
"""
    art = {"@type": "BlogPosting", "@id": BASE + f"/blog/{p['slug']}#article", "headline": p["title"], "description": p["description"],
           "image": [BASE + f"/assets/img/{p['image']}.webp"], "datePublished": p["date"] + "T09:00:00-05:00", "dateModified": upd + "T09:00:00-05:00",
           "author": {"@type": "Organization", "name": "N3X Ventures Growth Team", "url": BASE + "/about"}, "publisher": {"@id": ORG_ID},
           "mainEntityOfPage": BASE + f"/blog/{p['slug']}", "articleSection": p["category"], "wordCount": p["words"], "inLanguage": "en-US",
           "keywords": [p["category"]] + [SVC[s]["name"] for s in p["services"]],
           "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".article-head h1", ".takeaways"]}}
    meta = f'<meta property="article:published_time" content="{p["date"]}T09:00:00-05:00">\n<meta property="article:modified_time" content="{upd}T09:00:00-05:00">\n<meta property="article:section" content="{E(p["category"])}">\n'
    write(f"/blog/{p['slug']}", page(f"{p['seo_title']} | N3X Ventures", p["description"], f"/blog/{p['slug']}", body, active="blog", body_class="is-article",
          schema=[art, crumbs_schema(trail), faq_schema(p["faq"])], og_type="article", og_image=f"/assets/img/{p['image']}.webp", article_meta=meta, preload=f"/assets/img/{p['image']}.webp"), lastmod=upd, priority="0.7")


# --------------------------------------------------------------------------- LEGAL / 404
def build_legal():
    def legal(path, title, h1, sections, active=""):
        trail = [("Home", "/"), (h1, path)]
        secs = "".join(f"<h2>{E(a)}</h2>{b}" for a, b in sections)
        body = f"""<section class="page-hero"><div class="bg-grid"></div><div class="container legal">{crumbs(trail)}<span class="tag">Legal</span><h1>{E(h1)}</h1><p class="lead">Last updated October 15, 2026</p>{secs}</div></section>"""
        write(path, page(title, f"{h1} for N3X Ventures: how we handle your information, our website terms, and how to contact us with any questions.", path, body, schema=[crumbs_schema(trail)]), priority="0.3")
    legal("/privacy", "Privacy Policy | N3X Ventures", "Privacy Policy", [
        ("Who we are", f"<p>N3X Ventures (“we”, “us”) operates this website. You can contact us at <a href='mailto:{EMAIL}'>{EMAIL}</a> or {PHONE}.</p>"),
        ("Information we collect", "<p>When you submit a form or book a call we collect the details you provide, such as your name, email, phone number, company, industry and message. We also collect standard analytics data (pages visited, device and approximate location) through Google Analytics.</p>"),
        ("How we use it", "<p>We use your information to respond to inquiries, schedule and prepare for calls, deliver services, and improve our website. We do not sell your personal information.</p>"),
        ("Service providers", "<p>We use trusted third parties to operate this site and our business, including Google Analytics (analytics), Formspree (form delivery), Calendly (scheduling) and Vercel (hosting). These providers process data on our behalf under their own privacy terms.</p>"),
        ("Cookies", "<p>Google Analytics uses cookies to understand how visitors use the site. You can block or delete cookies in your browser settings, or use Google's opt-out browser add-on.</p>"),
        ("Text messages", "<p>If you provide your phone number, we may contact you by call or SMS about your inquiry. Message and data rates may apply. Reply STOP to opt out at any time.</p>"),
        ("Your choices", f"<p>You may request access to, correction of, or deletion of your personal information by emailing <a href='mailto:{EMAIL}'>{EMAIL}</a>.</p>"),
        ("Changes", "<p>We may update this policy from time to time. The latest version will always be available on this page.</p>"),
    ])
    legal("/terms", "Terms of Service | N3X Ventures", "Terms of Service", [
        ("Agreement", "<p>By using this website you agree to these terms. If you do not agree, please do not use the site.</p>"),
        ("Services", "<p>Information on this website describes our services in general terms. Specific deliverables, pricing and timelines are defined in a separate written proposal or agreement. Listed prices are starting points and may vary by scope.</p>"),
        ("Results", "<p>Case studies and results describe outcomes for specific clients and are not a guarantee of future results. Marketing performance depends on many factors outside our control.</p>"),
        ("Intellectual property", "<p>All content on this website, including text, graphics and logos, belongs to N3X Ventures or its licensors and may not be reused without permission.</p>"),
        ("Third-party links", "<p>This site may link to third-party websites. We are not responsible for their content or practices.</p>"),
        ("Limitation of liability", "<p>This website is provided “as is”. To the fullest extent permitted by law, N3X Ventures is not liable for any damages arising from your use of the site.</p>"),
        ("Contact", f"<p>Questions about these terms? Email <a href='mailto:{EMAIL}'>{EMAIL}</a>.</p>"),
    ])
    body = f"""<section class="page-hero page-hero--center" style="min-height:60vh;display:grid;align-items:center"><div class="bg-grid"></div><div class="glow glow--mint"></div><div class="container page-hero-grid"><div class="hero-enter"><span class="tag">Error 404</span><h1>This page took a <span class="grad-text">wrong turn</span></h1><p class="lead">The page you're looking for doesn't exist or has moved. Let's get you back on track.</p><div class="btn-row"><a class="btn btn--primary btn--lg" href="/">Back to home {ARROW()}</a><a class="btn btn--ghost btn--lg" href="/blog">Read the blog</a></div></div></div></section>"""
    write("/404", page("Page not found | N3X Ventures", "The page you're looking for doesn't exist.", "/404", body, robots="noindex, follow"), priority=None)


# --------------------------------------------------------------------------- SEO files
def build_seo_files():
    urls = "".join(f"<url><loc>{BASE}{p if p != '/' else '/'}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority></url>\n" for p, lm, pr in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(f"""# N3X Ventures — search & AI crawlers welcome
User-agent: *
Allow: /

# AI assistants & answer engines (GEO / AEO)
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Bingbot
Allow: /

Sitemap: {BASE}/sitemap.xml
""")
    svc_lines = "\n".join(f"- [{s[1]}]({BASE}/services/{s[0]}): {s[2]}. Plans from {C['services'][s[0]]['pricing']['plans'][0]['amount']}/month." for s in SERVICES)
    ind_lines = "\n".join(f"- [{n[1]}]({BASE}/niches/{n[0]}): growth marketing for {n[2]}. Plans from {C['niches'][n[0]]['pricing']['plans'][0]['amount']}/month." for n in NICHES)
    blog_lines = "\n".join(f"- [{p['title']}]({BASE}/blog/{p['slug']}): {p['description']}" for p in POSTS)
    open(os.path.join(OUT, "llms.txt"), "w").write(f"""# N3X Ventures

> N3X Ventures is an AI-powered growth marketing agency (founded 2022, 8+ years of team experience) that builds AI automation, paid ads, SEO & GEO, lead generation, websites, social media, LinkedIn marketing, content, video editing and branding for US businesses across 25+ industries. Done-for-you, month-to-month plans. Part of the N3X family of brands alongside N3X Realty (real estate) and N3X Chain (blockchain & AI engineering).

- Website: {BASE}
- Phone / WhatsApp: {PHONE} ({PHONE_E164})
- Email: {EMAIL}
- Locations: {", ".join(LOCATIONS)}
- Book a free 30-minute strategy call: {BASE}/contact
- Sister brand for real estate agents: {REALTY_URL}

## Services
{svc_lines}

## Industries
{ind_lines}
- [Coaches & Consultants]({BASE}/coaches): funnels, personal brand, content and automation for coaches and course creators. Plans from $699/month.

## Guides
{blog_lines}

## Company
- [About]({BASE}/about)
- [Contact]({BASE}/contact)
- [All services]({BASE}/services)
- [All industries]({BASE}/industries)
""")
    json.dump({"name": "N3X Ventures", "short_name": "N3X", "start_url": "/", "display": "standalone", "background_color": "#101118", "theme_color": "#101118",
               "description": "AI-powered growth marketing agency.",
               "icons": [{"src": "/assets/brand/favicon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/brand/favicon-512.png", "sizes": "512x512", "type": "image/png"},
                         {"src": "/assets/brand/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
              open(os.path.join(OUT, "site.webmanifest"), "w"), indent=1)
    items = "".join(f"""<item><title>{E(p['title'])}</title><link>{BASE}/blog/{p['slug']}</link><guid>{BASE}/blog/{p['slug']}</guid><pubDate>{datetime.datetime.fromisoformat(p['date'] + 'T14:00:00').strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><category>{E(p['category'])}</category><description>{E(p['description'])}</description></item>\n""" for p in POSTS)
    open(os.path.join(OUT, "blog", "feed.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>N3X Ventures Blog</title><link>{BASE}/blog</link><description>Growth marketing, AI automation, SEO and GEO guides.</description><language>en-us</language>\n{items}</channel></rss>\n')
    json.dump({"cleanUrls": True, "trailingSlash": False,
               "redirects": [{"source": "/index", "destination": "/", "permanent": True}, {"source": "/niches", "destination": "/industries", "permanent": False}],
               "headers": [
                   {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                   {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}, {"key": "X-Frame-Options", "value": "SAMEORIGIN"}, {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"}]}]},
              open(os.path.join(OUT, "vercel.json"), "w"), indent=2)
    shutil.copy(os.path.join(OUT, "assets/brand/favicon.ico"), os.path.join(OUT, "favicon.ico"))


if __name__ == "__main__":
    for d in ("services", "niches", "blog", "industries"):
        shutil.rmtree(os.path.join(OUT, d), ignore_errors=True)
    build_home()
    build_services_hub()
    for s in SVC:
        build_service(s)
    build_industries_hub()
    for n in NICHE:
        build_niche(n)
    build_coaches()
    build_about()
    build_contact()
    build_blog_index()
    for p in POSTS:
        build_post(p)
    build_legal()
    build_seo_files()
    print("pages:", len(PAGES) + 1, "posts:", len(POSTS), "avg words:", sum(p["words"] for p in POSTS) // len(POSTS))
