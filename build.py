#!/usr/bin/env python3
"""Собирает сайт: content/site.json + static/ -> _site/index.html.

Запуск:  python3 build.py
Без внешних зависимостей. Все тексты правятся в content/site.json.
"""
import json
import os
import shutil
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")


def e(s):
    return escape(str(s or ""), quote=True)


def icon(name):
    paths = {
        "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>',
        "telegram": '<path d="M21.5 4.5 2.8 11.7c-.8.3-.8 1.4 0 1.7l4.6 1.6 1.8 5.6c.2.7 1.1.9 1.6.4l2.6-2.5 4.7 3.5c.6.4 1.4.1 1.6-.6l3.2-15.1c.2-.9-.6-1.6-1.4-1.3Z"/><path d="m7.4 15 10-7.3-7.6 8.6"/>',
        "youtube": '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3Z" fill="currentColor"/>',
        "facebook": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v8h4v-8h3l1-4h-4V8.5c0-.3.2-.5.5-.5Z"/>',
        "send": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
        "plus": '<path d="M12 5v14M5 12h14"/>',
        "close": '<path d="M6 6l12 12M18 6 6 18"/>',
        "arrow-left": '<path d="M15 6l-6 6 6 6"/>',
        "arrow-right": '<path d="M9 6l6 6-6 6"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/>',
        "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
        "pin": '<path d="M12 22s7-6.1 7-12a7 7 0 1 0-14 0c0 5.9 7 12 7 12Z"/><circle cx="12" cy="10" r="2.5"/>',
    }
    return ('<svg class="i i-%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>'
            % (name, paths[name]))


def socials(c, cls="socials"):
    items = [("instagram", "Instagram"), ("telegram", "Telegram"), ("youtube", "YouTube"), ("facebook", "Facebook")]
    out = []
    for key, label in items:
        if c.get(key):
            out.append('<a class="soc soc-%s" href="%s" target="_blank" rel="noopener" aria-label="%s">%s</a>'
                       % (key, e(c[key]), label, icon(key)))
    return '<div class="%s">%s</div>' % (cls, "".join(out))


NAV = [
    ("Главная", "#top"),
    ("Методика", "#approach"),
    ("Услуги и стоимость", "#pricing"),
    ("Традиция", "#about"),
    ("Вималананда", "#vimalananda"),
    ("Команда", "#team"),
]


def nav_links():
    return "".join('<a href="%s">%s</a>' % (h, e(t)) for t, h in NAV)


def ul(points, cls="dots"):
    return '<ul class="%s">%s</ul>' % (cls, "".join("<li>%s</li>" % e(p) for p in points))


def form_fields(prefix, button):
    return f"""
      <label class="fld"><span>Имя</span><input name="name" type="text" autocomplete="name" placeholder="Введите ваше имя"></label>
      <label class="fld"><span>Телефон *</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" required placeholder="Введите ваш номер телефона"></label>
      <label class="fld"><span>Email *</span><input name="email" type="email" autocomplete="email" required placeholder="Введите вашу почту"></label>
      <label class="agree"><input type="checkbox" name="agree" required checked> <span>Согласен(а) на обработку персональных данных</span></label>
      <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <input type="hidden" name="source" value="{prefix}">
      <button class="btn btn-lead" type="submit"><span>{e(button)}</span></button>
      <p class="form-error" role="alert" hidden>Не удалось отправить. Напишите нам в Telegram — ответим быстро.</p>"""


def render(d):
    c = d["contacts"]
    seo = d["seo"]
    hero = d["hero"]
    cards = hero["cards"]

    team_html = ""
    for i, m in enumerate(d["team"]["members"]):
        anchor = ' id="vimalananda"' if i == 0 else ""
        team_html += f"""
        <article class="member reveal"{anchor}>
          <div class="member-photo"><img src="{e(m['photo'])}" alt="{e(m['name'])}" loading="lazy" width="400" height="500"></div>
          <h3>{e(m['name'])}</h3>
          {ul(m['points'])}
        </article>"""

    steps_html = "".join(f"""
        <div class="step reveal" style="--i:{i}">
          <span class="step-dot"></span>
          <div class="step-label"><small>{i+1:02d}</small>{e(s)}</div>
        </div>""" for i, s in enumerate(d["steps"]["items"]))

    tabs_btns, tabs_panels = "", ""
    for ti, tab in enumerate(d["pricing"]["tabs"]):
        active = ti == 0
        tabs_btns += ('<button class="tab%s" role="tab" aria-selected="%s" aria-controls="tab-%d" id="tabbtn-%d">%s</button>'
                      % (" is-active" if active else "", "true" if active else "false", ti, ti, e(tab["name"])))
        cards_html = "".join(f"""
            <article class="price-card">
              <img class="price-icon" src="{e(d['pricing']['icon'])}" alt="" loading="lazy" width="120" height="120">
              <div class="price-body">
                <h3>{e(pc['title'])}</h3>
                {ul(pc['points'])}
                <div class="price-meta"><span class="badge badge-fill">{e(pc['duration'])}</span><span class="badge badge-line">{e(pc['price'])}</span></div>
              </div>
            </article>""" for pc in tab["cards"])
        tabs_panels += ('<div class="tab-panel%s" role="tabpanel" id="tab-%d" aria-labelledby="tabbtn-%d"%s>%s</div>'
                        % (" is-active" if active else "", ti, ti, "" if active else " hidden", cards_html))

    acc_html = "".join(f"""
          <details class="acc"{' open' if i == 0 else ''}>
            <summary>{e(l['title'])}<span class="acc-ico">{icon('plus')}</span></summary>
            <div class="acc-body">{ul(l['points'])}</div>
          </details>""" for i, l in enumerate(d["results"]["levels"]))

    reviews_html = "".join(f"""
          <article class="review">
            <div class="review-head"><img src="{e(r['photo'])}" alt="{e(r['name'])}" loading="lazy" width="64" height="64"><h3>{e(r['name'])}</h3></div>
            <p>{e(r['text'])}</p>
          </article>""" for r in d["reviews"]["items"])

    about_p = "".join("<p>%s</p>" % e(p) for p in d["about"]["paragraphs"])
    approach_p = "".join("<p>%s</p>" % e(p) for p in d["approach"]["paragraphs"])
    stats_html = "".join('<div class="stat reveal"><b data-count="%s">%s</b><span>%s</span></div>'
                         % (e(s["value"]), e(s["value"]), e(s["label"])) for s in d["stats"])

    phone_href = "tel:" + "".join(ch for ch in c["phone"] if ch.isdigit() or ch == "+")
    canonical = f'<link rel="canonical" href="{e(SITE_URL)}/">' if SITE_URL else ""
    og_img = (SITE_URL + "/" + seo["og_image"]) if SITE_URL else seo["og_image"]
    config = json.dumps({"endpoint": d["forms"]["endpoint"], "telegram": c["telegram"]}, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(seo['title'])}</title>
<meta name="description" content="{e(seo['description'])}">
{canonical}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(seo['title'])}">
<meta property="og:description" content="{e(seo['description'])}">
<meta property="og:image" content="{e(og_img)}">
<meta name="theme-color" content="#F09143">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Unbounded:wght@500;700&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="{e(hero['image'])}">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "Проект «Рестарт»", "email": c["email"], "telephone": c["phone"], "address": c["location"], "sameAs": [c[k] for k in ("telegram", "instagram", "youtube", "facebook") if c.get(k)]}, ensure_ascii=False)}</script>
</head>
<body id="top">

<header class="header" id="header">
  <div class="wrap header-in">
    <a class="logo" href="#top" aria-label="Рестарт — на главную">RE<span>START</span></a>
    <nav class="nav" aria-label="Меню">{nav_links()}</nav>
    {socials(c, "socials header-soc")}
    <button class="burger" aria-label="Открыть меню" aria-expanded="false" aria-controls="mnav"><span></span><span></span><span></span></button>
  </div>
  <div class="mnav" id="mnav" hidden>
    <nav>{nav_links()}</nav>
    <button class="btn" data-open="consult">{e(hero['button'])}</button>
    {socials(c)}
  </div>
</header>

<main>
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hcard hcard-main">
      <img src="{e(hero['image'])}" alt="Вималананда — основатель проекта «Рестарт»" width="1400" height="1400" fetchpriority="high">
      <h1>{e(hero['title'])}</h1>
      <button class="btn btn-hero" data-open="consult">{e(hero['button'])} {icon('send')}</button>
    </div>
    <a class="hcard hcard-wide" href="{e(cards[0]['link'])}"><img src="{e(cards[0]['image'])}" alt="{e(cards[0]['title'])}" width="1200" height="675"><span>{e(cards[0]['title'])}</span></a>
    <a class="hcard hcard-sm" href="{e(cards[1]['link'])}"><img src="{e(cards[1]['image'])}" alt="{e(cards[1]['title'])}" width="900" height="1200"><span>{e(cards[1]['title'])}</span></a>
    <a class="hcard hcard-sm" href="{e(cards[2]['link'])}"><img src="{e(cards[2]['image'])}" alt="{e(cards[2]['title'])}" width="1000" height="560"><span>{e(cards[2]['title'])}</span></a>
  </div>
</section>

<section class="sec peach" id="about">
  <div class="wrap">
    <div class="panel reveal"><h2>{e(d['about']['title'])}</h2>{about_p}</div>
    <div class="stats">{stats_html}</div>
  </div>
</section>

<section class="sec" id="team">
  <div class="wrap">
    <h2 class="reveal">{e(d['team']['title'])}</h2>
    <p class="lead-text reveal">{e(d['team']['text'])}</p>
    <div class="team">{team_html}</div>
    <div class="center"><button class="btn" data-open="consult">{e(d['team']['button'])}</button></div>
  </div>
</section>

<section class="sec peach" id="approach">
  <div class="wrap"><div class="panel reveal"><h2>{e(d['approach']['title'])}</h2>{approach_p}</div></div>
</section>

<section class="sec" id="steps">
  <div class="wrap">
    <h2 class="reveal">{e(d['steps']['title'])}</h2>
    <div class="steps">{steps_html}</div>
    <div class="center"><button class="btn" data-open="consult">{e(d['steps']['button'])}</button></div>
  </div>
</section>

<section class="sec peach" id="pricing">
  <div class="wrap">
    <div class="pricing-head">
      <h2 class="reveal">{e(d['pricing']['title'])}</h2>
      <button class="btn" data-open="consult">{e(d['pricing']['button'])}</button>
    </div>
    <div class="tabs" role="tablist" aria-label="Пакеты">{tabs_btns}</div>
    {tabs_panels}
  </div>
</section>

<section class="sec" id="results">
  <div class="wrap results">
    <div class="results-left reveal">
      <h2 class="upper">{e(d['results']['title'])}</h2>
      <div class="results-img"><img src="{e(d['results']['image'])}" alt="Вималананда" loading="lazy" width="1200" height="800"></div>
    </div>
    <div class="accs reveal">{acc_html}</div>
  </div>
</section>

<section class="sec peach" id="lead">
  <div class="wrap">
    <div class="panel lead reveal">
      <div class="lead-left">
        <img src="{e(d['lead']['image'])}" alt="" loading="lazy" width="700" height="700">
        <h2>{e(d['lead']['title'])}</h2>
        <p class="lead-sub">{e(d['lead']['subtitle'])}</p>
      </div>
      <form class="form" data-form novalidate>{form_fields("Форма на странице", d['lead']['button'])}</form>
    </div>
  </div>
</section>

<section class="sec" id="reviews">
  <div class="wrap">
    <h2 class="center reveal">{e(d['reviews']['title'])}</h2>
    <div class="slider">
      <div class="slides" tabindex="0">{reviews_html}</div>
      <div class="slider-nav"><button class="snav prev" aria-label="Назад">{icon('arrow-left')}</button><button class="snav next" aria-label="Вперёд">{icon('arrow-right')}</button></div>
    </div>
  </div>
</section>
</main>

<footer class="sec footer-sec" id="contacts">
  <div class="wrap">
    <div class="footer reveal">
      <nav class="fnav" aria-label="Меню в подвале">{nav_links()}</nav>
      <div class="fcontacts">
        <h2>{e(d['footer']['contacts_title'])}</h2>
        <p>{icon('pin')} {e(c['location'])}</p>
        <p>{icon('mail')} <a href="mailto:{e(c['email'])}">{e(c['email'])}</a></p>
        <p>{icon('phone')} <a href="{e(phone_href)}">{e(c['phone'])}</a></p>
        {socials(c)}
      </div>
    </div>
    <p class="copy">{e(d['footer']['copyright'])}</p>
  </div>
</footer>

<a class="fab" href="{e(c['telegram'])}" target="_blank" rel="noopener" aria-label="Написать в Telegram">{icon('telegram')}</a>

<div class="modal" id="consult" hidden>
  <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="consult-title">
    <button class="modal-x" data-close aria-label="Закрыть">{icon('close')}</button>
    <h2 id="consult-title">{e(hero['button'])}</h2>
    <form class="form" data-form novalidate>{form_fields("Окно «Бесплатная консультация»", d['lead']['button'])}</form>
  </div>
</div>

<div class="modal" id="thanks" hidden>
  <div class="modal-box modal-thanks" role="dialog" aria-modal="true" aria-labelledby="thanks-title">
    <button class="modal-x" data-close aria-label="Закрыть">{icon('close')}</button>
    <div class="thanks-ico">✓</div>
    <h2 id="thanks-title">{e(d['forms']['success_title'])}</h2>
    <p>{e(d['forms']['success_text'])}</p>
    <button class="btn" data-close>Готово</button>
  </div>
</div>

<script>window.SITE={config};</script>
<script src="main.js" defer></script>
</body>
</html>
"""


def main():
    with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as f:
        data = json.load(f)
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, "static"), OUT)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(render(data))
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE_URL}/sitemap.xml\n" if SITE_URL else ""))
    if SITE_URL:
        with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    f"<url><loc>{SITE_URL}/</loc></url></urlset>\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print("Готово:", os.path.join(OUT, "index.html"))


if __name__ == "__main__":
    main()
