"""Static registries: site constants, services, industries, icons."""
import os, re

BASE = "https://n3xventures.vercel.app"
REALTY_URL = "https://n3xrealty.vercel.app"
PHONE = "404-981-1910"
PHONE_E164 = "+14049811910"
WA = "https://wa.me/14049811910"
EMAIL = "n3xventures@gmail.com"
LOCATIONS = ["Lubbock, Texas", "Atlanta, Georgia", "Dubai, UAE"]
SOCIAL = {
    "instagram": "https://www.instagram.com/n3xventures/",
    "linkedin": "https://linkedin.com/company/n3xventures",
    "facebook": "https://www.facebook.com/n3xrealty",
}
GA = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-T8WX7GJDET"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-T8WX7GJDET');
</script>"""

# --------------------------------------------------------------------------- icons
ICON_DIR = os.path.join(os.path.dirname(__file__), "node_modules/lucide-static/icons")
_icon_cache = {}


def icon(name, cls=""):
    if name not in _icon_cache:
        p = os.path.join(ICON_DIR, name + ".svg")
        if not os.path.exists(p):
            raise SystemExit(f"missing icon {name}")
        svg = open(p).read()
        svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
        svg = re.sub(r'\s(width|height)="24"', "", svg)
        svg = re.sub(r'\sclass="[^"]*"', "", svg)
        svg = re.sub(r"\s+", " ", svg).replace("> <", "><")
        _icon_cache[name] = svg
    s = _icon_cache[name]
    extra = f' class="{cls}"' if cls else ""
    return s.replace("<svg ", f'<svg aria-hidden="true" focusable="false"{extra} ', 1)


EMOJI = {
    "💬": "message-circle", "📞": "phone-call", "🎯": "target", "⚙️": "settings-2", "📅": "calendar-check",
    "🔗": "link", "✉️": "mail", "📚": "book-open", "📄": "file-text", "🧭": "compass", "📋": "clipboard-list",
    "📊": "chart-column", "🎨": "palette", "📐": "ruler", "✍️": "pen-line", "📇": "contact", "🔄": "refresh-cw",
    "💡": "lightbulb", "📱": "smartphone", "📝": "notebook-pen", "🎬": "clapperboard", "🎞️": "film",
    "♻️": "recycle", "💼": "briefcase", "📈": "trending-up", "💰": "piggy-bank", "🤖": "bot",
    "🧑‍💼": "user-round-check", "🏢": "building-2", "📥": "inbox", "📰": "newspaper", "🔍": "search",
    "📺": "tv", "🔧": "wrench", "📍": "map-pin", "🎥": "video", "🎓": "graduation-cap", "✨": "sparkles",
    "🖼️": "image", "⚡": "zap", "📉": "trending-down", "🌐": "globe", "🔁": "repeat", "💳": "credit-card",
    "💸": "banknote", "⭐": "star", "☎️": "phone-missed", "⚖️": "scale", "🛒": "shopping-cart", "📧": "mail-check",
    "🔌": "plug", "🏗️": "construction", "🤝": "handshake", "📜": "scroll-text", "🔐": "lock", "📸": "camera",
    "🍂": "leaf", "⏱️": "timer", "🗓️": "calendar-days", "🩺": "stethoscope", "🚨": "siren", "🥇": "medal",
    "💵": "dollar-sign", "👥": "users", "🤔": "circle-help", "🔇": "volume-x", "⏳": "hourglass", "🏷️": "tag",
    "🚀": "rocket", "🏆": "trophy", "🔭": "telescope", "🧠": "brain", "🦷": "smile", "🛡️": "shield-check",
}


def emoji_icon(e, fallback="sparkles"):
    return EMOJI.get(e.strip(), fallback)


# --------------------------------------------------------------------------- services
SERVICES = [
    # slug, name, nav blurb, icon, group
    ("ai-automation", "AI Automation", "Chatbots, voice agents & CRM workflows that never sleep", "bot", "Build & Automate"),
    ("paid-ads", "Paid Ads", "Google, Meta, LinkedIn & YouTube built for booked calls", "target", "Growth"),
    ("seo-geo", "SEO & GEO", "Rank on Google and get cited by ChatGPT & AI search", "search", "Growth"),
    ("lead-generation", "Lead Generation", "Outreach, funnels & nurture that fill your calendar", "magnet", "Growth"),
    ("websites", "Websites", "Fast, conversion-first sites & landing pages", "monitor-smartphone", "Build & Automate"),
    ("social-media", "Social Media", "Strategy & daily management across every platform", "share-2", "Growth"),
    ("linkedin-marketing", "LinkedIn Marketing", "Founder-led content & outbound for B2B", "briefcase-business", "Growth"),
    ("content-creation", "Content Creation", "Blogs, copy & calendars that build authority", "pen-line", "Build & Automate"),
    ("video-editing", "Video Editing", "Reels, YouTube & podcasts that hold attention", "clapperboard", "Build & Automate"),
    ("branding", "Branding", "Identity & positioning that justifies premium prices", "sparkles", "Build & Automate"),
]
SVC = {s[0]: {"slug": s[0], "name": s[1], "blurb": s[2], "icon": s[3], "group": s[4]} for s in SERVICES}

# --------------------------------------------------------------------------- industries
CATS = ["Home Services", "Healthcare", "Financial & Legal", "B2B & Online"]
CAT_SLUG = {"Home Services": "home", "Healthcare": "health", "Financial & Legal": "finance", "B2B & Online": "b2b"}
NICHES = [
    # slug, short name, audience noun (plural), category, icon, booking label
    ("roofing", "Roofing", "roofing companies", "Home Services", "house", "Roofing"),
    ("hvac", "HVAC", "HVAC companies", "Home Services", "thermometer-snowflake", "HVAC"),
    ("plumbing", "Plumbing", "plumbing companies", "Home Services", "wrench", "Plumbing"),
    ("electrical", "Electrical", "electricians", "Home Services", "zap", "Electrical"),
    ("solar", "Solar", "solar installers", "Home Services", "sun", "Solar"),
    ("landscaping", "Landscaping", "landscaping businesses", "Home Services", "trees", "Landscaping"),
    ("remodeling", "Remodeling", "remodeling contractors", "Home Services", "hammer", "Remodeling"),
    ("dentists", "Dentists", "dental practices", "Healthcare", "smile", "Dentists"),
    ("med-spas", "Med Spas", "med spas", "Healthcare", "flower-2", "Med Spas"),
    ("plastic-surgeons", "Plastic Surgeons", "plastic surgery practices", "Healthcare", "stethoscope", "Plastic Surgeons"),
    ("dermatologists", "Dermatologists", "dermatology practices", "Healthcare", "scan-face", "Dermatologists"),
    ("chiropractors", "Chiropractors", "chiropractic clinics", "Healthcare", "activity", "Chiropractors"),
    ("physical-therapy", "Physical Therapy", "physical therapy clinics", "Healthcare", "person-standing", "Physical Therapy"),
    ("lawyers", "Lawyers", "law firms", "Financial & Legal", "scale", "Lawyers"),
    ("financial-advisors", "Financial Advisors", "financial advisors", "Financial & Legal", "chart-line", "Financial Advisors"),
    ("insurance", "Insurance", "insurance agencies", "Financial & Legal", "shield-check", "Insurance"),
    ("mortgage-brokers", "Mortgage Brokers", "mortgage brokers", "Financial & Legal", "landmark", "Mortgage Brokers"),
    ("accounting", "Accounting", "accounting firms", "Financial & Legal", "calculator", "Accounting"),
    ("saas", "SaaS", "SaaS companies", "B2B & Online", "cloud", "SaaS"),
    ("ecommerce", "E-commerce", "e-commerce brands", "B2B & Online", "shopping-cart", "E-commerce"),
    ("marketing-agencies", "Marketing Agencies", "marketing agencies", "B2B & Online", "megaphone", "Marketing Agency"),
    ("recruitment", "Recruitment", "recruitment agencies", "B2B & Online", "users", "Recruitment"),
    ("it-msp", "IT & MSP", "IT & MSP companies", "B2B & Online", "server", "IT & MSP"),
]
NICHE = {n[0]: {"slug": n[0], "name": n[1], "aud": n[2], "cat": n[3], "icon": n[4], "book": n[5]} for n in NICHES}
COACHES = {"slug": "coaches", "name": "Coaches & Consultants", "aud": "coaches", "cat": "B2B & Online", "icon": "graduation-cap", "book": "Coaches & Consultants"}


def niche_url(slug):
    return "/coaches" if slug == "coaches" else f"/niches/{slug}"


def svc_for_title(title):
    t = title.lower()
    rules = [("linkedin", "linkedin-marketing"), ("seo", "seo-geo"), ("geo", "seo-geo"), ("search", "seo-geo"),
             ("ads", "paid-ads"), ("advertis", "paid-ads"), ("retarget", "paid-ads"), ("ai ", "ai-automation"),
             ("automation", "ai-automation"), ("chatbot", "ai-automation"), ("follow-up", "ai-automation"),
             ("crm", "ai-automation"), ("website", "websites"), ("landing", "websites"), ("social", "social-media"),
             ("video", "video-editing"), ("reel", "video-editing"), ("brand", "branding"), ("content", "content-creation"),
             ("blog", "content-creation"), ("email", "lead-generation"), ("lead", "lead-generation"),
             ("outreach", "lead-generation"), ("funnel", "lead-generation"), ("outbound", "lead-generation")]
    for k, v in rules:
        if k in t:
            return v
    return None
