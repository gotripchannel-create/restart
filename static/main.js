/* Проект «Рестарт» — интерактив: меню, табы, модалки, формы, анимации. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var SITE = window.SITE || {};

  /* Шапка: тень при прокрутке */
  var header = $("#header");
  var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 10); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Мобильное меню */
  var burger = $(".burger"), mnav = $("#mnav");
  function setMenu(open) {
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    mnav.hidden = !open;
  }
  burger.addEventListener("click", function () { setMenu(mnav.hidden); });
  $$("#mnav a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });

  /* Табы цен */
  var tabs = $$(".tab");
  tabs.forEach(function (tab, i) {
    tab.addEventListener("click", function () { selectTab(i); });
    tab.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowRight" || ev.key === "ArrowLeft") {
        var n = (i + (ev.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length;
        selectTab(n); tabs[n].focus();
      }
    });
  });
  function selectTab(i) {
    tabs.forEach(function (t, j) {
      var on = i === j, panel = document.getElementById(t.getAttribute("aria-controls"));
      t.classList.toggle("is-active", on);
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      panel.hidden = !on;
      panel.classList.toggle("is-active", on);
    });
  }

  /* Модальные окна */
  var lastFocus = null;
  function openModal(id) {
    var m = document.getElementById(id);
    if (!m) return;
    $$(".modal").forEach(function (x) { x.hidden = true; });
    lastFocus = document.activeElement;
    m.hidden = false;
    document.body.classList.add("no-scroll");
    var f = $("input:not([type=hidden]):not(.hp), button", m);
    setTimeout(function () { f && f.focus(); }, 50);
  }
  function closeModals() {
    $$(".modal").forEach(function (x) { x.hidden = true; });
    document.body.classList.remove("no-scroll");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  $$("[data-open]").forEach(function (b) {
    b.addEventListener("click", function () { setMenu(false); openModal(b.getAttribute("data-open")); });
  });
  $$(".modal").forEach(function (m) {
    m.addEventListener("click", function (ev) {
      if (ev.target === m || ev.target.closest("[data-close]")) closeModals();
    });
  });
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") closeModals(); });

  /* Отзывы: стрелки */
  var slides = $(".slides");
  if (slides) {
    var step = function () { var c = $(".review", slides); return c ? c.getBoundingClientRect().width + 24 : 300; };
    $(".snav.prev").addEventListener("click", function () { slides.scrollBy({ left: -step(), behavior: "smooth" }); });
    $(".snav.next").addEventListener("click", function () {
      var end = slides.scrollLeft + slides.clientWidth >= slides.scrollWidth - 5;
      slides.scrollTo({ left: end ? 0 : slides.scrollLeft + step(), behavior: "smooth" });
    });
  }

  /* Аккордеон: открыт только один пункт */
  $$(".acc").forEach(function (d) {
    d.addEventListener("toggle", function () {
      if (d.open) $$(".acc").forEach(function (o) { if (o !== d) o.open = false; });
    });
  });

  /* Появление при прокрутке */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); countUp(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Счётчики в цифрах */
  function countUp(el) {
    var b = $("b[data-count]", el);
    if (!b) return;
    var raw = b.getAttribute("data-count"), m = raw.match(/^(\d+)(.*)$/);
    if (!m || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var target = +m[1], suffix = m[2], t0 = null, dur = 1400;
    function frame(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / dur), v = Math.round(target * (1 - Math.pow(1 - p, 3)));
      b.textContent = v + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* Формы заявок */
  $$("[data-form]").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var err = $(".form-error", form), btn = $("button[type=submit]", form);
      err.hidden = true;
      var phone = form.phone, email = form.email, ok = true;
      [phone, email].forEach(function (i) { i.classList.remove("is-invalid"); });
      if ((phone.value.match(/\d/g) || []).length < 7) { phone.classList.add("is-invalid"); ok = false; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) { email.classList.add("is-invalid"); ok = false; }
      if (!form.agree.checked) ok = false;
      if (!ok) { var bad = $(".is-invalid", form); bad && bad.focus(); return; }
      if (form.website.value) return; // бот

      var data = {
        name: form.name.value.trim(),
        phone: phone.value.trim(),
        email: email.value.trim(),
        source: form.source.value,
        page: location.href
      };

      if (!SITE.endpoint) {
        // Приёмник заявок ещё не настроен — отправляем человека в Telegram, чтобы заявка не потерялась
        window.open(SITE.telegram, "_blank");
        form.reset(); form.agree.checked = true;
        openModal("thanks");
        return;
      }
      btn.classList.add("is-loading");
      fetch(SITE.endpoint, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify(data)
      }).then(function () {
        form.reset(); form.agree.checked = true;
        if (window.ym && SITE.metrika) window.ym(SITE.metrika, "reachGoal", "lead");
        openModal("thanks");
      }).catch(function () {
        err.hidden = false;
      }).then(function () { btn.classList.remove("is-loading"); });
    });
    $$("input", form).forEach(function (i) { i.addEventListener("input", function () { i.classList.remove("is-invalid"); }); });
  });
})();
