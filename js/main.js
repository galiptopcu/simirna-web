/* ── FAQ accordion ── */
function toggleFaq(el) {
  const item = el.closest('.faq-item');
  const isOpen = item.classList.contains('open');
  document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
  if (!isOpen) item.classList.add('open');
}

/* ── Scroll-reveal animations ── */
function initFadeUps() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.fade-up:not(.visible)').forEach(el => obs.observe(el));
}
initFadeUps();

/* ── Navbar scroll shadow ── */
window.addEventListener('scroll', () => {
  const nb = document.getElementById('navbar');
  if (nb) nb.classList.toggle('scrolled', window.scrollY > 40);
});

/* ── Mobile menu ── */
function toggleMobileMenu() {
  const burger = document.getElementById('navBurger');
  const menu = document.getElementById('mobileMenu');
  if (!burger || !menu) return;
  const isOpen = menu.classList.toggle('open');
  burger.classList.toggle('open', isOpen);
  burger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  document.body.style.overflow = isOpen ? 'hidden' : '';
}
function closeMobileMenu() {
  const burger = document.getElementById('navBurger');
  const menu = document.getElementById('mobileMenu');
  if (!burger || !menu || !menu.classList.contains('open')) return;
  menu.classList.remove('open');
  burger.classList.remove('open');
  burger.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

/* ── Contact forms → Web3Forms ── */
(function () {
  document.querySelectorAll('.contact-form-box form, .contact-form-card form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('.form-submit');
      var msg = form.querySelector('.form-message');
      var origText = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = '...'; }
      if (msg) { msg.textContent = ''; msg.className = 'form-message'; }
      fetch('https://api.web3forms.com/submit', { method: 'POST', body: new FormData(form) })
        .then(function (r) { return r.json(); })
        .then(function (json) {
          if (json.success) {
            form.reset();
            if (msg) { msg.textContent = form.dataset.sent || 'Mesajınız gönderildi!'; msg.className = 'form-message form-message--ok'; }
          } else {
            throw new Error(json.message);
          }
        })
        .catch(function () {
          if (msg) { msg.textContent = form.dataset.error || 'Bir hata oluştu, lütfen tekrar deneyin.'; msg.className = 'form-message form-message--err'; }
        })
        .finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = origText; }
        });
    });
  });
}());
