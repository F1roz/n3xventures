// ============================================================
// N3X — shared site behavior
// ============================================================

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- Booking Modal ---------- */
  (function initBookingModal(){

    // ⚠️ CONFIG — replace these two placeholders with your real endpoints before going live.
    const CALENDLY_URL = "https://calendly.com/n3xventures/30min"; // <-- your real Calendly event link
    const FORMSPREE_URL = "https://formspree.io/f/mkodrpyn"; // <-- your real Formspree (or other form backend) endpoint

    const SERVICE_OPTIONS = [
      "AI Automation","Paid Ads","SEO & GEO","Lead Generation","Websites",
      "Social Media","Content Creation","Video Editing","Branding","Not sure yet"
    ];
    const NICHE_OPTIONS = [
      "Roofing","HVAC","Plumbing","Electrical","Solar","Landscaping","Remodeling",
      "Dentists","Med Spas","Plastic Surgeons","Dermatologists","Chiropractors","Physical Therapy",
      "Lawyers","Financial Advisors","Insurance","Mortgage Brokers","Accounting",
      "SaaS","E-commerce","Marketing Agency","Coaches & Consultants","Recruitment","IT & MSP",
      "Real Estate","Other"
    ];

    function optionList(arr){
      return arr.map(v => `<option value="${v}">${v}</option>`).join("");
    }

    const modalHTML = `
    <div class="booking-overlay" id="booking-overlay" aria-hidden="true">
      <div class="booking-modal" id="booking-modal">
        <div class="booking-modal-head">
          <div class="booking-progress">
            <span class="booking-progress-dot active" data-step-dot="1"></span>
            <span>Step 1: Your Info</span>
            <span style="opacity:.4;">—</span>
            <span class="booking-progress-dot" data-step-dot="2"></span>
            <span>Step 2: Pick a Time</span>
          </div>
          <button class="booking-close" id="booking-close" aria-label="Close">&#x2715;</button>
        </div>
        <div class="booking-body">

          <div id="booking-step-1">
            <h3>Let's get you booked in</h3>
            <p class="booking-sub">Tell us a bit about your business, then pick a time that works for you.</p>
            <form id="booking-form" novalidate>
              <div class="booking-field">
                <label for="bk-name">Full Name</label>
                <input type="text" id="bk-name" name="name" required autocomplete="name">
                <div class="booking-error">Please enter your name.</div>
              </div>
              <div class="booking-row">
                <div class="booking-field">
                  <label for="bk-phone">Mobile Number</label>
                  <input type="tel" id="bk-phone" name="phone" required autocomplete="tel">
                  <div class="booking-error">Please enter a phone number.</div>
                </div>
                <div class="booking-field">
                  <label for="bk-email">Email</label>
                  <input type="email" id="bk-email" name="email" required autocomplete="email">
                  <div class="booking-error">Please enter a valid email.</div>
                </div>
              </div>
              <div class="booking-row">
                <div class="booking-field">
                  <label for="bk-service">Service Interested In</label>
                  <select id="bk-service" name="service" required>
                    <option value="" disabled selected>Select a service</option>
                    ${optionList(SERVICE_OPTIONS)}
                  </select>
                  <div class="booking-error">Please select a service.</div>
                </div>
                <div class="booking-field">
                  <label for="bk-niche">Your Industry</label>
                  <select id="bk-niche" name="niche" required>
                    <option value="" disabled selected>Select your industry</option>
                    ${optionList(NICHE_OPTIONS)}
                  </select>
                  <div class="booking-error">Please select your industry.</div>
                </div>
              </div>
              <div class="booking-actions">
                <button type="submit" class="btn btn-primary btn-full">Continue to Calendar →</button>
              </div>
            </form>
          </div>

          <div id="booking-step-2" style="display:none;">
            <button class="booking-back" id="booking-back">&#8592; Back</button>
            <h3>Pick a date &amp; time</h3>
            <p class="booking-sub">Choose whatever works best — you'll get an instant confirmation by email.</p>
            <div class="calendly-frame-wrap" id="calendly-frame-wrap"></div>
          </div>

        </div>
      </div>
    </div>
    <div class="booking-toast" id="booking-toast">Thanks! We've got your info — pick a time below.</div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    const overlay = document.getElementById('booking-overlay');
    const modal = document.getElementById('booking-modal');
    const step1 = document.getElementById('booking-step-1');
    const step2 = document.getElementById('booking-step-2');
    const form = document.getElementById('booking-form');
    const toast = document.getElementById('booking-toast');
    const dots = document.querySelectorAll('.booking-progress-dot');

    function showToast(msg){
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3200);
    }

    function openModal(){
      overlay.classList.add('open');
      overlay.setAttribute('aria-hidden','false');
      document.body.style.overflow = 'hidden';
    }
    function closeModal(){
      overlay.classList.remove('open');
      overlay.setAttribute('aria-hidden','true');
      document.body.style.overflow = '';
      // reset to step 1 for next open
      setTimeout(() => {
        step1.style.display = '';
        step2.style.display = 'none';
        modal.classList.remove('step-2');
        dots[0].classList.add('active');
        dots[1].classList.remove('active');
      }, 250);
    }

    document.getElementById('booking-close').addEventListener('click', closeModal);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal(); });

    document.getElementById('booking-back').addEventListener('click', () => {
      step2.style.display = 'none';
      step1.style.display = '';
      modal.classList.remove('step-2');
      dots[0].classList.add('active');
      dots[1].classList.remove('active');
    });

    form.addEventListener('submit', function(e){
      e.preventDefault();
      let valid = true;
      ['bk-name','bk-phone','bk-email','bk-service','bk-niche'].forEach(id => {
        const field = document.getElementById(id);
        const wrap = field.closest('.booking-field');
        const ok = field.checkValidity() && field.value.trim() !== '';
        wrap.classList.toggle('has-error', !ok);
        if (!ok) valid = false;
      });
      if (!valid) return;

      const data = {
        name: document.getElementById('bk-name').value.trim(),
        phone: document.getElementById('bk-phone').value.trim(),
        email: document.getElementById('bk-email').value.trim(),
        service: document.getElementById('bk-service').value,
        niche: document.getElementById('bk-niche').value,
      };

      // Best-effort lead capture to your form backend (Formspree, etc).
      // Booking still proceeds to the calendar even if this fails or isn't configured yet.
      if (FORMSPREE_URL.indexOf('YOUR_FORM_ID') === -1) {
        fetch(FORMSPREE_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(data)
        }).catch(() => {});
      }

      showToast("Thanks, " + data.name.split(' ')[0] + "! Pick a time below.");

      // Build Calendly embed with prefill — requires matching custom question
      // order (a1, a2...) in your real Calendly event's "Invitee Questions" settings.
      const frameWrap = document.getElementById('calendly-frame-wrap');
      if (CALENDLY_URL.indexOf('YOUR-CALENDLY-USERNAME') !== -1) {
        frameWrap.innerHTML = `<div class="booking-fallback">
          <p><strong>Calendly isn't connected yet.</strong><br>Add your real Calendly link in script.js (CALENDLY_URL) to enable live booking here.</p>
          <a href="mailto:n3xventures@gmail.com?subject=Strategy Call Request&body=Name: ${encodeURIComponent(data.name)}%0APhone: ${encodeURIComponent(data.phone)}%0AEmail: ${encodeURIComponent(data.email)}%0AService: ${encodeURIComponent(data.service)}%0AIndustry: ${encodeURIComponent(data.niche)}" class="btn btn-primary">Email Us Instead</a>
        </div>`;
      } else {
        const params = new URLSearchParams({
          name: data.name,
          email: data.email,
          a1: data.phone,
          a2: data.service,
          a3: data.niche,
          hide_gdpr_banner: '1'
        });
        frameWrap.innerHTML = `<iframe src="${CALENDLY_URL}?${params.toString()}" title="Book a call"></iframe>`;
      }

      step1.style.display = 'none';
      step2.style.display = '';
      modal.classList.add('step-2');
      dots[0].classList.remove('active');
      dots[1].classList.add('active');
    });

    // Intercept every booking-intent CTA button site-wide: any .btn whose href is exactly "#" or "#cta"
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a.btn');
      if (!link) return;
      const href = link.getAttribute('href');
      if (href === '#' || href === '#cta') {
        e.preventDefault();
        openModal();
      }
    });
  })();

  /* ---------- Mobile nav ---------- */
  const hamburger = document.getElementById('hamburger');
  const mobileNav = document.getElementById('mobile-nav');
  const mobileOverlay = document.getElementById('mobile-overlay');
  const mobileClose = document.getElementById('mobile-close');

  function openMobile(){
    mobileNav?.classList.add('open');
    mobileOverlay?.classList.add('open');
    hamburger?.setAttribute('aria-expanded','true');
    document.body.style.overflow = 'hidden';
  }
  function closeMobile(){
    mobileNav?.classList.remove('open');
    mobileOverlay?.classList.remove('open');
    hamburger?.setAttribute('aria-expanded','false');
    document.body.style.overflow = '';
  }
  hamburger?.addEventListener('click', openMobile);
  mobileClose?.addEventListener('click', closeMobile);
  mobileOverlay?.addEventListener('click', closeMobile);

  document.querySelectorAll('.mobile-sub-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const list = btn.nextElementSibling;
      const isOpen = list.classList.contains('open');
      document.querySelectorAll('.mobile-sub-list.open').forEach(l => l.classList.remove('open'));
      if(!isOpen) list.classList.add('open');
    });
  });

  /* ---------- Desktop dropdown: click-to-toggle (fixes touch devices where :hover never fires) ---------- */
  document.querySelectorAll('.nav-item.has-dropdown > .nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const item = link.closest('.nav-item');
      const isOpen = item.classList.contains('force-open');
      document.querySelectorAll('.nav-item.has-dropdown.force-open').forEach(i => i.classList.remove('force-open'));
      if (!isOpen) {
        e.preventDefault();
        item.classList.add('force-open');
      }
      // if already open, let the click through so the link's real href (e.g. index.html#services) works
    });
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item.has-dropdown')) {
      document.querySelectorAll('.nav-item.has-dropdown.force-open').forEach(i => i.classList.remove('force-open'));
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-item.has-dropdown.force-open').forEach(i => i.classList.remove('force-open'));
    }
  });

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold:.15, rootMargin:'0px 0px -60px 0px' });
    revealEls.forEach(el => io.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('in'));
  }

  /* ---------- Staggered children index ---------- */
  document.querySelectorAll('.reveal-stagger').forEach(group => {
    [...group.children].forEach((child,i) => child.style.setProperty('--i', i));
  });

  /* ---------- Hero word cycle ---------- */
  const cycleEl = document.querySelector('.word-cycle');
  if(cycleEl){
    let words;
    try { words = JSON.parse(cycleEl.dataset.words); } catch(e){ words = []; }
    let idx = 0;
    if(words.length){
      setInterval(() => {
        cycleEl.classList.add('cycle-out');
        setTimeout(() => {
          idx = (idx + 1) % words.length;
          cycleEl.textContent = words[idx];
          cycleEl.classList.remove('cycle-out');
        }, 320);
      }, 2200);
    }
  }

  /* ---------- Animated counters ---------- */
  const counters = document.querySelectorAll('.stat-num[data-count]');
  if(counters.length && 'IntersectionObserver' in window){
    const cio = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseFloat(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        const decimals = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;
        const dur = 1400;
        const start = performance.now();
        function tick(now){
          const p = Math.min((now - start) / dur, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          const val = target * eased;
          el.textContent = (decimals ? val.toFixed(decimals) : Math.round(val)) + suffix;
          if(p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        cio.unobserve(el);
      });
    }, { threshold:.5 });
    counters.forEach(c => cio.observe(c));
  }

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    q?.addEventListener('click', () => {
      const isOpen = item.classList.contains('open');
      item.closest('.faq-list').querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
      if(!isOpen) item.classList.add('open');
    });
  });

  /* ---------- Back to top ---------- */
  const backToTop = document.querySelector('.back-to-top');
  window.addEventListener('scroll', () => {
    if(!backToTop) return;
    backToTop.classList.toggle('show', window.scrollY > 600);
  });
  backToTop?.addEventListener('click', () => window.scrollTo({ top:0, behavior:'smooth' }));

  /* ---------- Industry card tilt-ish hover handled in CSS; nothing extra needed ---------- */
});
