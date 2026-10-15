/* N3X Ventures — site behaviour */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Header scroll state ---------- */
  const header = $(".site-header");
  const topBtn = $(".fab--top");
  const onScroll = () => {
    const y = window.scrollY;
    header && header.classList.toggle("is-scrolled", y > 8);
    topBtn && topBtn.classList.toggle("is-visible", y > 700);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  topBtn && topBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }));

  /* ---------- Desktop mega menus (hover + click + keyboard) ---------- */
  $$(".nav-item.has-mega").forEach((item) => {
    const trigger = $(".nav-link", item);
    let t;
    const open = () => { clearTimeout(t); $$(".nav-item.is-open").forEach((i) => i !== item && close(i)); item.classList.add("is-open"); trigger.setAttribute("aria-expanded", "true"); };
    const close = (i = item) => { i.classList.remove("is-open"); $(".nav-link", i).setAttribute("aria-expanded", "false"); };
    item.addEventListener("mouseenter", open);
    item.addEventListener("mouseleave", () => { t = setTimeout(() => close(), 140); });
    trigger.addEventListener("click", (e) => {
      if (!item.classList.contains("is-open")) { e.preventDefault(); open(); }
    });
    item.addEventListener("focusout", (e) => { if (!item.contains(e.relatedTarget)) close(); });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") $$(".nav-item.is-open").forEach((i) => { i.classList.remove("is-open"); $(".nav-link", i).setAttribute("aria-expanded", "false"); });
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".nav-item.has-mega")) $$(".nav-item.is-open").forEach((i) => i.classList.remove("is-open"));
  });

  /* ---------- Mobile drawer ---------- */
  const drawer = $("#drawer");
  const burger = $(".burger");
  const openDrawer = () => { drawer.classList.add("is-open"); drawer.setAttribute("aria-hidden", "false"); burger.setAttribute("aria-expanded", "true"); document.body.classList.add("no-scroll"); setTimeout(() => $(".drawer-close", drawer).focus(), 50); };
  const closeDrawer = () => { drawer.classList.remove("is-open"); drawer.setAttribute("aria-hidden", "true"); burger.setAttribute("aria-expanded", "false"); document.body.classList.remove("no-scroll"); };
  if (drawer && burger) {
    burger.addEventListener("click", openDrawer);
    $$("[data-close-drawer]", drawer).forEach((el) => el.addEventListener("click", closeDrawer));
    $$("a", drawer).forEach((a) => a.addEventListener("click", closeDrawer));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && drawer.classList.contains("is-open")) closeDrawer(); });
  }

  /* ---------- Reveal on scroll ---------- */
  $$("[data-stagger]").forEach((g) => [...g.children].forEach((c, i) => { c.classList.add("reveal"); c.style.setProperty("--i", i % 8); }));
  const reveals = $$(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } }), { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach((el) => io.observe(el));
  } else reveals.forEach((el) => el.classList.add("in"));

  /* ---------- Word cycle ---------- */
  const cyc = $(".cycle-word");
  if (cyc && !reduce) {
    let words = []; try { words = JSON.parse(cyc.dataset.words); } catch (e) {}
    let i = 0;
    setInterval(() => {
      cyc.classList.add("is-out");
      setTimeout(() => { i = (i + 1) % words.length; cyc.textContent = words[i]; cyc.classList.remove("is-out"); }, 350);
    }, 2300);
  }

  /* ---------- Counters ---------- */
  const counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const fmt = (v, d) => d ? v.toFixed(d) : Math.round(v).toLocaleString("en-US");
    const cio = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return;
      const el = en.target, target = parseFloat(el.dataset.count), dec = parseInt(el.dataset.decimals || 0, 10);
      const pre = el.dataset.prefix || "", suf = el.dataset.suffix || "";
      const plain = el.dataset.plain === "1";
      if (reduce) { el.textContent = pre + (plain ? target : fmt(target, dec)) + suf; cio.unobserve(el); return; }
      const t0 = performance.now(), dur = 1500;
      const tick = (now) => { const p = Math.min((now - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3); const v = target * e; el.textContent = pre + (plain ? Math.round(v) : fmt(v, dec)) + suf; if (p < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick); cio.unobserve(el);
    }), { threshold: 0.5 });
    counters.forEach((c) => cio.observe(c));
  }

  /* ---------- Filters (industries + blog) ---------- */
  $$("[data-filter-group]").forEach((bar) => {
    const target = $(bar.dataset.filterGroup);
    if (!target) return;
    bar.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-filter]"); if (!btn) return;
      $$("[data-filter]", bar).forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      const f = btn.dataset.filter;
      $$("[data-cat]", target).forEach((card) => card.classList.toggle("is-hidden", f !== "all" && !card.dataset.cat.split(" ").includes(f)));
    });
  });

  /* ---------- Article: reading progress + TOC highlight + copy link ---------- */
  const tocD = $(".toc details");
  if (tocD) {
    const mq = window.matchMedia("(max-width: 1024px)");
    const syncToc = () => { tocD.open = !mq.matches; };
    syncToc(); mq.addEventListener && mq.addEventListener("change", syncToc);
    tocD.addEventListener("click", (e) => { if (!mq.matches && e.target.closest("summary")) e.preventDefault(); });
  }
  const bar = $(".read-progress");
  const prose = $(".prose");
  if (bar && prose) {
    const upd = () => {
      const r = prose.getBoundingClientRect();
      const p = Math.min(Math.max((window.innerHeight * 0.35 - r.top) / r.height, 0), 1);
      bar.style.transform = `scaleX(${p})`;
    };
    window.addEventListener("scroll", upd, { passive: true }); upd();
    const links = $$(".toc a");
    const heads = links.map((a) => document.getElementById(a.getAttribute("href").slice(1))).filter(Boolean);
    if (heads.length && "IntersectionObserver" in window) {
      const tio = new IntersectionObserver((entries) => entries.forEach((en) => {
        if (en.isIntersecting) links.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === "#" + en.target.id));
      }), { rootMargin: "-20% 0px -70% 0px" });
      heads.forEach((h) => tio.observe(h));
    }
  }
  $$("[data-copy-link]").forEach((b) => b.addEventListener("click", () => {
    navigator.clipboard && navigator.clipboard.writeText(location.href).then(() => { b.setAttribute("aria-label", "Link copied"); b.classList.add("copied"); setTimeout(() => b.classList.remove("copied"), 1600); });
  }));

  /* ---------- Contact form → Formspree ---------- */
  const FORMSPREE_URL = "https://formspree.io/f/mkodrpyn";
  const cform = $("#contact-form");
  if (cform) {
    cform.addEventListener("submit", (e) => {
      e.preventDefault();
      const status = $(".form-status", cform);
      if (!cform.checkValidity()) { cform.reportValidity(); return; }
      const data = Object.fromEntries(new FormData(cform).entries());
      status.textContent = "Sending…";
      fetch(FORMSPREE_URL, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
        .then((r) => { if (!r.ok) throw 0; status.textContent = "Thanks — we'll reply within one business day."; status.style.color = "#07805f"; cform.reset(); if (window.gtag) gtag("event", "generate_lead", { form: "contact" }); })
        .catch(() => { status.innerHTML = 'Something went wrong. Email us at <a href="mailto:n3xventures@gmail.com">n3xventures@gmail.com</a>.'; status.style.color = "#c4441f"; });
    });
  }

  /* ---------- Booking modal (Calendly + Formspree) ---------- */
  const CALENDLY_URL = "https://calendly.com/n3xventures/30min";
  const SERVICE_OPTIONS = ["AI Automation", "Paid Ads", "SEO & GEO", "Lead Generation", "Websites", "Social Media", "LinkedIn Marketing", "Content Creation", "Video Editing", "Branding", "Not sure yet"];
  const NICHE_OPTIONS = ["Roofing", "HVAC", "Plumbing", "Electrical", "Solar", "Landscaping", "Remodeling", "Dentists", "Med Spas", "Plastic Surgeons", "Dermatologists", "Chiropractors", "Physical Therapy", "Lawyers", "Financial Advisors", "Insurance", "Mortgage Brokers", "Accounting", "SaaS", "E-commerce", "Marketing Agency", "Coaches & Consultants", "Recruitment", "IT & MSP", "Real Estate", "Other"];
  const opts = (a) => a.map((v) => `<option value="${v}">${v}</option>`).join("");
  document.body.insertAdjacentHTML("beforeend", `
  <div class="booking-overlay" id="booking-overlay" aria-hidden="true">
    <div class="booking-modal" id="booking-modal" role="dialog" aria-modal="true" aria-labelledby="bk-title">
      <div class="booking-modal-head">
        <div class="booking-progress"><span class="booking-progress-dot active"></span><span>01 Your info</span><span style="opacity:.4">—</span><span class="booking-progress-dot"></span><span>02 Pick a time</span></div>
        <button class="booking-close" id="booking-close" aria-label="Close booking dialog">✕</button>
      </div>
      <div class="booking-body">
        <div id="booking-step-1">
          <h3 id="bk-title">Book your free strategy call</h3>
          <p class="booking-sub">30 minutes. A real strategist. A custom growth roadmap for your business — no pressure, no obligation.</p>
          <form id="booking-form" novalidate>
            <div class="booking-field"><label for="bk-name">Full name</label><input type="text" id="bk-name" name="name" required autocomplete="name"><div class="booking-error">Please enter your name.</div></div>
            <div class="booking-row">
              <div class="booking-field"><label for="bk-phone">Mobile number</label><input type="tel" id="bk-phone" name="phone" required autocomplete="tel"><div class="booking-error">Please enter a phone number.</div></div>
              <div class="booking-field"><label for="bk-email">Email</label><input type="email" id="bk-email" name="email" required autocomplete="email"><div class="booking-error">Please enter a valid email.</div></div>
            </div>
            <div class="booking-row">
              <div class="booking-field"><label for="bk-service">Service you're interested in</label><select id="bk-service" name="service" required><option value="" disabled selected>Select a service</option>${opts(SERVICE_OPTIONS)}</select><div class="booking-error">Please select a service.</div></div>
              <div class="booking-field"><label for="bk-niche">Your industry</label><select id="bk-niche" name="niche" required><option value="" disabled selected>Select your industry</option>${opts(NICHE_OPTIONS)}</select><div class="booking-error">Please select your industry.</div></div>
            </div>
            <div class="booking-actions"><button type="submit" class="btn btn--primary btn--lg">Continue to calendar →</button></div>
            <div class="booking-trust"><span>✓ Free 30-min call</span><span>✓ Month-to-month plans</span><span>✓ Reply within 1 business day</span></div>
          </form>
        </div>
        <div id="booking-step-2" hidden>
          <button class="booking-back" id="booking-back">← Back</button>
          <h3>Pick a date &amp; time</h3>
          <p class="booking-sub">Choose what works best — you'll get an instant email confirmation.</p>
          <div class="calendly-frame-wrap" id="calendly-frame-wrap"></div>
        </div>
      </div>
    </div>
  </div>
  <div class="booking-toast" id="booking-toast" role="status"></div>`);

  const overlay = $("#booking-overlay"), modal = $("#booking-modal"), s1 = $("#booking-step-1"), s2 = $("#booking-step-2"), form = $("#booking-form"), toast = $("#booking-toast"), dots = $$(".booking-progress-dot");
  let lastFocus = null;
  const toStep = (n) => { s1.hidden = n !== 1; s2.hidden = n !== 2; modal.classList.toggle("step-2", n === 2); dots[0].classList.toggle("active", n === 1); dots[1].classList.toggle("active", n === 2); };
  const openModal = (preset) => {
    lastFocus = document.activeElement;
    if (preset && preset.service) { const s = $("#bk-service"); if ([...s.options].some((o) => o.value === preset.service)) s.value = preset.service; }
    if (preset && preset.niche) { const n = $("#bk-niche"); if ([...n.options].some((o) => o.value === preset.niche)) n.value = preset.niche; }
    overlay.classList.add("open"); overlay.setAttribute("aria-hidden", "false"); document.body.classList.add("no-scroll");
    setTimeout(() => $("#bk-name").focus(), 80);
    if (window.gtag) gtag("event", "booking_open");
  };
  const closeModal = () => { overlay.classList.remove("open"); overlay.setAttribute("aria-hidden", "true"); document.body.classList.remove("no-scroll"); setTimeout(() => toStep(1), 250); lastFocus && lastFocus.focus(); };
  $("#booking-close").addEventListener("click", closeModal);
  overlay.addEventListener("click", (e) => { if (e.target === overlay) closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && overlay.classList.contains("open")) closeModal(); });
  $("#booking-back").addEventListener("click", () => toStep(1));
  $$("input, select", form).forEach((f) => f.addEventListener("input", () => f.closest(".booking-field").classList.remove("has-error")));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    let ok = true;
    ["bk-name", "bk-phone", "bk-email", "bk-service", "bk-niche"].forEach((id) => { const f = $("#" + id), good = f.checkValidity() && f.value.trim() !== ""; f.closest(".booking-field").classList.toggle("has-error", !good); if (!good) ok = false; });
    if (!ok) return;
    const data = { name: $("#bk-name").value.trim(), phone: $("#bk-phone").value.trim(), email: $("#bk-email").value.trim(), service: $("#bk-service").value, niche: $("#bk-niche").value, page: location.pathname };
    fetch(FORMSPREE_URL, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) }).catch(() => {});
    if (window.gtag) gtag("event", "generate_lead", { form: "booking", service: data.service, industry: data.niche });
    toast.textContent = "Thanks, " + data.name.split(" ")[0] + "! Pick a time below."; toast.classList.add("show"); setTimeout(() => toast.classList.remove("show"), 3200);
    const p = new URLSearchParams({ name: data.name, email: data.email, a1: data.phone, a2: data.service, a3: data.niche, hide_gdpr_banner: "1" });
    $("#calendly-frame-wrap").innerHTML = `<iframe src="${CALENDLY_URL}?${p.toString()}" title="Book a call with N3X Ventures" loading="lazy"></iframe>`;
    toStep(2);
  });
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-book], a.btn[href='#book']");
    if (!t) return;
    e.preventDefault();
    openModal({ service: t.dataset.service, niche: t.dataset.niche });
  });
})();
