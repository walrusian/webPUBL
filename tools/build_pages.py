#!/usr/bin/env python3
# Сборщик страниц Wagner Motors: общая шапка/подвал/иконки + содержимое всех страниц.
# Запуск из корня проекта: python3 tools/build_pages.py — перезаписывает *.html в корне.
import json
import os

OUT = os.environ.get('BUILD_OUT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Адрес обработчика заявок. Пусто — демо (GitHub Pages, заявки никуда не уходят).
# Для хостинга собирается через tools/package_hosting.py, там LEAD_API=api/lead.php
LEAD_API = os.environ.get('LEAD_API', '')

# Временно выключенные части сайта. Код (cart.html, js/cart.js, стили билета/корзины) остаётся —
# чтобы вернуть, поставить True и пересобрать страницы.
PROMO = False   # акция: розыгрыш Porsche Cayenne (блок с билетом, бейджи, правила акции)
SHOW_PRICE = False  # цена комплексной диагностики (5 000 ₽) на страницах — убрана по просьбе владельца 12.10.2026
SHOP = False    # корзина и онлайн-оплата (кнопка корзины, «Купить», «Добавить в корзину»)

ICONS = {
    'i-cart': '<path d="M3 4h2l2.2 10.2a2 2 0 0 0 2 1.6h7.6a2 2 0 0 0 2-1.5L20.5 8H6.2"/><circle cx="10" cy="20" r="1.3"/><circle cx="17" cy="20" r="1.3"/>',
    'i-close': '<path d="M6 6l12 12M18 6L6 18"/>',
    'i-arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'i-chev-left': '<path d="M15 5l-7 7 7 7"/>',
    'i-chev-right': '<path d="M9 5l7 7-7 7"/>',
    'i-play': '<path d="M8 5.5v13l11-6.5z"/>',
    'i-camera': '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    'i-video': '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3"/>',
    'i-phone': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/>',
    'i-pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'i-clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'i-mail': '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><path d="M4 7l8 6 8-6"/>',
    'i-chat': '<path d="M4 5.5h16v11H9l-5 4z"/>',
    'i-wrench': '<path d="M14.7 6.3a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3l7.7-7.7z"/><path d="M14.7 6.3L17 4l3 3-2.3 2.3"/>',
    'i-engine': '<path d="M3 10v6M3 13h3M6 9h3V7h6v2h2l2 2h2v5h-2l-2 2H9l-3-2z"/>',
    'i-gauge': '<path d="M4.5 17a8 8 0 1 1 15 0"/><path d="M12 13.5l4-4.5"/><circle cx="12" cy="13.5" r="1.2"/>',
    'i-disc': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/><path d="M12 4a8 8 0 0 1 8 8"/>',
    'i-bolt': '<path d="M13 3L5 13.5h6L10 21l8-10.5h-6z"/>',
    'i-drop': '<path d="M12 3.5s6 6.5 6 10.5a6 6 0 0 1-12 0c0-4 6-10.5 6-10.5z"/>',
    'i-car': '<path d="M5 16v-4l1.8-4.2A2 2 0 0 1 8.6 6.5h6.8a2 2 0 0 1 1.8 1.3L19 12v4"/><path d="M3.5 12h17v4.5h-17z"/><path d="M6 16.5V19M18 16.5V19"/>',
    'i-snow': '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/>',
    'i-check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'i-plus': '<path d="M12 5v14M5 12h14"/>',
    'i-minus': '<path d="M5 12h14"/>',
    'i-trash': '<path d="M5 7h14M10 7V4.5h4V7M7 7l1 13h8l1-13"/>',
    'i-star': '<path d="M12 3.5l2.6 5.4 5.9.7-4.4 4 1.2 5.9L12 16.6l-5.3 2.9 1.2-5.9-4.4-4 5.9-.7z"/>',
    'i-ticket': '<path d="M3.5 7.5a1 1 0 0 1 1-1h15a1 1 0 0 1 1 1V10a2 2 0 0 0 0 4v2.5a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1V14a2 2 0 0 0 0-4z"/><path d="M14.5 7v10" stroke-dasharray="1.5 2.2"/>',
    'i-card': '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3 10h18M7 15h3"/>',
    'i-qr': '<path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h2v2h-2zM18 18h2v2h-2zM14 18h2M18 14h2"/>',
    'i-user': '<circle cx="12" cy="8.5" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>',
    'i-shield': '<path d="M12 3.5l7 2.5v5.5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'i-doc': '<path d="M6 3.5h8l4 4v13H6z"/><path d="M14 3.5v4h4M9 12h6M9 16h6"/>',
}


def sprite():
    syms = ''.join(f'<symbol id="{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{syms}</svg>'


def i(name, cls='i'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


def todo(text):
    return f'<mark class="todo">[{text}]</mark>'


def bicon(name, size=''):
    # Фирменные иконки клиента (img/icon-*.webp); для недостающих — svg в том же стиле
    if name in ('pin', 'phone', 'price', 'chat', 'tools'):
        return f'<img class="bicon{size}" src="img/icon-{name}.webp" alt="" width="56" height="56" loading="lazy" decoding="async">'
    return f'<span class="bicon bicon--svg{size}">{i(name)}</span>'


SERVICE_ADDR = 'г.&nbsp;Ставрополь, ул.&nbsp;Коломийцева, 38а, корп.&nbsp;2'
HOURS = 'ежедневно с 9:00 до 20:00'
PHONES = [('+79282222464', '+7 (928) 222-24-64'), ('+79624947794', '+7 (962) 494-77-94')]
PHONE_LINKS = '<br>'.join(f'<a class="tel" href="tel:{h}">{t}</a>' for h, t in PHONES)

LOGO = '<img class="logo__mark" src="img/logo-128.webp" alt="" width="36" height="36"><span class="logo__text"><span class="logo__word">WAGNER</span><span class="logo__sub">MOTORS</span></span>'


NAV = [
    ('about.html', 'О компании'),
    ('services.html', 'Услуги'),
    ('gallery.html', 'Галерея'),
    ('reviews.html', 'Отзывы'),
    ('contacts.html', 'Контакты'),
]


def header(active):
    cur = ' aria-current="page"'
    links = ''.join(
        f'<a href="{h}"{cur if h == active else ""}>{t}</a>' for h, t in NAV)
    mlinks = ''.join(
        f'<a href="{h}"{cur if h == active else ""}>{t}{i("i-chev-right")}</a>' for h, t in NAV)
    return f'''<header class="nav">
  <div class="container nav__inner">
    <a class="logo" href="index.html" aria-label="Wagner Motors — на главную">
      {LOGO}
    </a>
    <nav class="nav__links" aria-label="Основное меню">{links}</nav>
    <div class="nav__actions">
      {f'<a class="icon-btn cart-btn" href="cart.html" aria-label="Корзина">{i("i-cart")}<span class="cart-btn__badge" hidden>0</span></a>' if SHOP else ''}
      <a class="nav-msg" href="{TELEGRAM_URL}" target="_blank" rel="noopener" aria-label="Написать в Telegram">{TG_ICON}</a>
      <a class="nav-msg" href="{MAX_URL}" target="_blank" rel="noopener" aria-label="Написать в MAX">{MAX_ICON}</a>
      <a class="btn btn--primary btn--sm nav__cta" href="booking.html">Записаться</a>
      <button class="icon-btn burger" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="menu"><span class="burger__lines"></span></button>
    </div>
  </div>
</header>
<div class="menu-scrim"></div>
<nav class="menu" id="menu" aria-label="Меню">
  {mlinks}
  <a class="btn btn--primary btn--lg" href="booking.html">Записаться</a>
  <a class="btn btn--ghost btn--lg" href="tel:{PHONES[0][0]}">{i("i-phone")}{PHONES[0][1]}</a>
</nav>'''


FOOTER = f'''<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="logo" href="index.html">{LOGO}</a>
        <p class="small">Автосервис. Диагностика и ремонт автомобилей.</p>
        <p class="small">{SERVICE_ADDR}</p>
      </div>
      <div>
        <h4>Сайт</h4>
        <ul>
          <li><a href="about.html">О компании</a></li>
          <li><a href="services.html">Услуги</a></li>
          <li><a href="gallery.html">Галерея</a></li>
          <li><a href="reviews.html">Отзывы</a></li>
        </ul>
      </div>
      <div>
        <h4>Клиентам</h4>
        <ul>
          <li><a href="booking.html">Записаться</a></li>
          {'<li><a href="cart.html">Корзина</a></li>' if SHOP else ''}
          {'<li><a href="privacy.html#promo">Правила акции</a></li>' if PROMO else ''}
          <li><a href="privacy.html">Политика конфиденциальности</a></li>
          <li><a href="consent.html">Согласие на обработку данных</a></li>
        </ul>
      </div>
      <div>
        <h4>Связаться</h4>
        <ul>
          {''.join(f'<li><a href="tel:{h}">{t}</a></li>' for h, t in PHONES)}
          <li>Работаем {HOURS}</li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© <span data-year>2026</span> ООО «Вагнер Моторс» · ИНН 2623033488</span>
      <a href="contacts.html">Контакты</a>
    </div>
  </div>
</footer>'''


# Политика безопасности: только свои файлы, без внешних скриптов, шрифтов и фреймов.
# Единственный встроенный скрипт (класс .js на <html>) разрешён по sha256-хешу —
# меняя его текст, пересчитай хеш. style-src 'unsafe-inline' нужен для атрибутов style="--d:…".
# Когда появится серверная функция для заявок, добавь её адрес в connect-src.
# frame-ancestors, X-Frame-Options, HSTS и nosniff через <meta> не работают — их ставят на хостинге.
CSP = ("default-src 'self'; script-src 'self' 'sha256-Du+OJKJSbdUgz5nrHeWWINvez6XKDDU/tyj/5c2uvwo='; "
       "style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
       "media-src 'self'; object-src 'none'; frame-src 'none'; worker-src 'none'; manifest-src 'self'; "
       "base-uri 'self'; form-action 'self'; upgrade-insecure-requests")


def ver(path):
    # Метка версии файла (первые 8 символов хеша): при любой правке меняется адрес, и браузер берёт свежий файл
    import hashlib
    with open(os.path.join(OUT, path), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def page(filename, title, description, body, active='', scripts=(), body_class=''):
    js = ''.join(f'\n<script src="js/{s}?v={ver(f"js/{s}")}" defer></script>' for s in ('spring.js', 'main.js', *scripts))
    html = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#0a0a0b">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">{f'{chr(10)}<meta name="lead-api" content="{LEAD_API}">' if LEAD_API else ''}
<link rel="icon" type="image/png" href="img/logo-64.png">
<link rel="stylesheet" href="css/styles.css?v={ver('css/styles.css')}">
<script>document.documentElement.classList.add('js')</script>{js}
</head>
<body{f' class="{body_class}"' if body_class else ''}>
{sprite()}
{header(active)}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
'''
    with open(os.path.join(OUT, filename), 'w', encoding='utf-8') as f:
        f.write(html)


def ph(label, icon='i-camera', tone='steel', extra=''):
    return f'<div class="ph ph--{tone}{extra}"><div class="ph__inner">{i(icon)}<span>{label}</span></div></div>'


def ph_video(label, tone='cool'):
    return f'<div class="ph ph--{tone}"><div class="ph__inner"><span class="ph__play">{i("i-play")}</span><span>{label}</span></div></div>'


# Фотосессии мастерской (фотограф Роман, rkochkaev.ru, разделы 08.02–26.08.2026): 37 лучших кадров.
# Головы механиков на g01 и номера на g15, g33 размыты. Плитка — *-800.webp, полноэкранный просмотр — *-1600.webp.
PHOTOS = [
    # общий план и машины
    ('g01', 'workshop', 'Мастерская'),
    ('g15', 'cars', 'Porsche Cayman на подъёмнике'),
    ('g13', 'process', 'Цепь ГРМ'),
    ('g02', 'workshop', 'BMW на стенде'),
    ('g18', 'process', 'Сварочные работы'),
    ('g20', 'process', 'Привод ГРМ'),
    ('g03', 'workshop', 'Нива на подъёмнике'),
    ('g14', 'process', 'Тормозной суппорт и диск'),
    ('g31', 'cars', 'Audi в сервисе'),
    ('g05', 'process', 'Новый тормозной суппорт'),
    ('g21', 'process', 'Поршень и шатун'),
    ('g33', 'cars', 'BMW на подъёмнике'),
    ('g24', 'process', 'Снятие колеса'),
    ('g07', 'process', 'Ремонт двигателя'),
    ('g30', 'cars', 'В боксе'),
    ('g06', 'process', 'Перфорированный тормозной диск'),
    ('g19', 'process', 'Двигатель на стенде'),
    ('g17', 'cars', 'Задний фонарь'),
    ('g25', 'process', 'Проверка давления в шинах'),
    ('g22', 'process', 'Головка блока цилиндров'),
    ('g04', 'workshop', 'Чистый бокс'),
    ('g26', 'process', 'Обслуживание тормозов'),
    ('g28', 'process', 'Сборка ГРМ'),
    ('g32', 'cars', 'Колёсный диск'),
    ('g08', 'process', 'Подвеска'),
    ('g29', 'process', 'Блок цилиндров'),
    ('g34', 'cars', 'Шильдик S4'),
    ('g27', 'process', 'Шиномонтаж'),
    ('g35', 'process', 'Шестерня ГРМ'),
    ('g09', 'process', 'Трансмиссия'),
    ('g16', 'process', 'Свечи зажигания'),
    ('g23', 'process', 'Инструмент и запчасти'),
    ('g36', 'process', 'Распредвалы'),
    ('g10', 'process', 'Работа мастера'),
    ('g37', 'process', 'Головка блока с распредвалами'),
    ('g11', 'process', 'Ступица и тормоза'),
    ('g12', 'process', 'Днище автомобиля'),
]


def photo_item(key, kind, caption):
    return (f'<button class="g-item" type="button" data-type="{kind}" '
            f'data-src="img/gallery/{key}-1600.webp" aria-label="Открыть: {caption}">'
            f'<img class="g-item__img" src="img/gallery/{key}-800.webp" alt="{caption}" loading="lazy" decoding="async"></button>')


def g_item(label, tone, kind='photo', caption=None):
    inner = ph_video(label, tone) if kind == 'video' else ph(label, 'i-camera', tone)
    cap = caption or label
    return f'<button class="g-item" type="button" data-type="{kind}" data-caption="{cap}" aria-label="Открыть: {cap}">{inner}</button>'


REVIEWS = [
    ('26 января 2025', 'Спасибо ребятам за проделанную работу на моей Октахе!) Быстро сделали ТО, расходники в наличии, работают быстро и хорошо, сразу виден профессиональный подход. Остался очень доволен, рекомендую!!!'),
    ('1 июля 2023', 'Огромное спасибо Саше! При замене тормозных дисков и колодок, выявил ошибку в работе форсунок двс (BMW G30 530d), что возможно могло повлечь гидроудар мотора. Профессионал своего дела! Рекомендую!'),
    ('27 января 2025', 'Обслужил здесь свой автомобиль. Автосервис очень понравился, цены адекватные, мастера знают толк в своем деле. Грамотно подобрали на него расходники и з/ч, приеду еще.'),
    ('28 января 2025', 'Доволен уровнем сервиса. Недавно был на диагностике, чек загорелся. Наблюдал за работой электрика, настоящий профессионал, просмотрел все ошибки,дал рекомендации. В общем, все круто'),
    ('3 августа 2025', 'Ребята молодцы. Машина будет обслуживаться теперь только у них 🥹\nВсегда все расскажут и покажут\nВесь прайс всегда обговаривается (не все СТО так делают, как оказалось)\nБуду отправлять к вам людей однозначно 🫶'),
    ('2 февраля 2025', 'Внимательность и доброжелательность сотрудников. Чистота и порядок в помещении. Большой ассортимент предлагаемых запчастей и аксессуаров. Качественное выполнение работ. Профессионально ответили на все возникшие вопросы. Рекомендую'),
    ('26 января 2025', 'Отличный сервис. Знаю ребят уже давно. Одним словом мастера своего дела, к каждому клиенту, всегда индивидуальный подход, никогда не оставят без внимания любую мелочь, на которую в сторонних сервисах, даже не обратили бы внимания. Всегда прислушиваются к клиенту, а самое главное что результат всегда выше, чем ожидания.'),
    ('27 января 2025', 'Добрый вечер всем . После покупки автомобиля заехали в автосервис для диагностики и полного обслужавания машины, что могу сказать парни знают своё дело на все 100%. Грамотная диагностика всего автомобиля , заказ запчастей ну и полное обслужавание от замены всех расходников и заканчивая советами на будущее . Спасибо огромное команде автосервиса, желаю хороших клиентов и только в перед 💪💪👍'),
    ('26 января 2025', 'Ожидание/реальность от сервиса - купил машину (ГАИ находится рядом ) решил быстро поменять масло и уехать , но после первого обслуживания приезжаю теперь только в этот сервис !!! Цены приятные , быстро , к тому же при общении с мастерами понимаешь уровень компетенции в этом СТО  которого в других сервисах сейчас к сожалению не хватает .\n\nСубъективно вижу построенную работу на доверительные и продолжительные отношения с клиентами, все максимально прозрачно , все что надо расскажут и подскажут .\nРекомендую однозначно !👍👍👍👍'),
]


def review(date, text, extra=''):
    stars = ''.join(i('i-star') for _ in range(5))
    return f'''<article class="review{extra}">
  <div class="stars stars--on" role="img" aria-label="5 из 5">{stars}</div>
  <p class="review__text">{text}</p>
  <div class="review__who">{bicon("chat", " bicon--sm")}<div><strong>Отзыв клиента</strong><span class="small">{date}</span></div></div>
</article>'''


def review_card():
    stars = ''.join(i('i-star') for _ in range(5))
    return f'''<article class="review">
  <div class="stars" aria-label="Оценка появится позже">{stars}</div>
  <div><span class="sk" style="--w:96%"></span><span class="sk" style="--w:100%"></span><span class="sk" style="--w:88%"></span><span class="sk" style="--w:60%"></span></div>
  <div class="review__who"><span class="review__avatar"></span><div><span class="sk" style="--w:55%"></span><span class="sk" style="--w:35%"></span></div></div>
</article>'''


CHECKLIST = ''.join(f'<li>{i("i-check")}<span>{t}</span></li>' for t in [
    'Компьютерная диагностика электронных систем',
    'Двигатель и навесное оборудование',
    'Ходовая часть и подвеска',
    'Тормозная система',
    'Электрика и аккумулятор',
    'Отчёт с рекомендациями по ремонту',
])

PRICES = [
    ('diag', 'i-bolt', 'Диагностика и электроника', [
        ('Компьютерная диагностика', 500), ('Ремонт ABS', 15000), ('Прошивка Ramon Performance', 20000)]),
    ('engine', 'i-engine', 'Двигатель и турбина', [
        ('Снятие-установка ДВС', 10000), ('Ремонт ДВС', 10000), ('Замена ГРМ', 5000), ('Замена помпы', 800),
        ('Замена ремней роликов', 600), ('Замена свечей зажигания', 400), ('Ремонт турбины', 5000),
        ('Снятие турбины', 2000), ('Удаление катализаторов', 3000)]),
    ('fluids', 'i-drop', 'ТО и жидкости', [
        ('Замена масла', 300), ('Замена масляного фильтра', 200), ('Замена антифриза', 700),
        ('Замена тормозной жидкости', 800), ('Заправка кондиционера', 2000)]),
    ('chassis', 'i-disc', 'Тормоза и ходовая', [
        ('Замена передних тормозных дисков', 800), ('Замена задних тормозных дисков', 900),
        ('Замена передних колодок', 500), ('Замена задних колодок', 600), ('Замена стоек амортизатора', 1000),
        ('Замена пыльников приводов', 1000), ('Ремонт ходовой', 800), ('Сход-развал', 1000)]),
    ('gearbox', 'i-wrench', 'АКПП', [('Ремонт АКПП', 5000), ('Снятие-установка АКПП', 4000)]),
    ('body', 'i-shield', 'Шины и кузов', [
        ('Шиномонтаж любой сложности', 1000), ('Антикоррозийная обработка днища', 12000), ('Арматурные работы', 1500)]),
]


# Порядок на странице услуг: пары с близким числом пунктов, чтобы ряды были ровными
# (двигатель 9 + ходовая 8, ТО 5 + диагностика 3, кузов 3 + АКПП 2)
_ORDER = ['engine', 'chassis', 'fluids', 'diag', 'body', 'gearbox']
PRICES_PAIRED = sorted(PRICES, key=lambda g: _ORDER.index(g[0]))


def rub(n):
    return f'{n:,}'.replace(',', '&nbsp;') + '&nbsp;₽'


def plural(n, forms):
    m10, m100 = n % 10, n % 100
    if m10 == 1 and m100 != 11:
        return forms[0]
    if 2 <= m10 <= 4 and not 12 <= m100 <= 14:
        return forms[1]
    return forms[2]


def price_card(key, ic, title, items, n=0):
    names = ' · '.join(t for t, _ in items[:3])
    more = f' и&nbsp;ещё&nbsp;{len(items) - 3}' if len(items) > 3 else ''
    return f'''<a class="card reveal" href="services.html#{key}" style="--d:{n % 3}">
  <span class="card__icon">{i(ic)}</span>
  <h3 class="h3">{title}</h3>
  <p class="small">{names}{more}</p>
  <div class="card__foot"><span>{len(items)} {plural(len(items), ("услуга", "услуги", "услуг"))}</span>{i("i-arrow")}</div>
</a>'''


def price_group(key, ic, title, items, n=0):
    rows = ''.join(f'<li class="price-row"><span>{t}</span></li>' for t, p in items)
    return f'''<section class="price-group reveal" id="{key}" style="--d:{n % 2}">
  <div class="price-group__head"><span class="card__icon">{i(ic)}</span><h3 class="h3">{title}</h3></div>
  <ul class="price-list">{rows}</ul>
</section>'''


SERVICES = [
    ('i-drop', 'Техническое обслуживание', 'Замена масла, фильтров и жидкостей по регламенту.'),
    ('i-engine', 'Ремонт двигателя', 'От замены ремня ГРМ до капитального ремонта.'),
    ('i-car', 'Ходовая и подвеска', 'Амортизаторы, рычаги, сайлентблоки, развал-схождение.'),
    ('i-disc', 'Тормозная система', 'Колодки, диски, суппорты, тормозная жидкость.'),
    ('i-bolt', 'Автоэлектрика', 'Проводка, генератор, стартер, электронные блоки.'),
    ('i-wrench', 'Слесарный ремонт', 'Выхлопная система, трансмиссия, рулевое управление.'),
]
SERVICES_MORE = [
    ('i-snow', 'Кондиционер', 'Диагностика, заправка и ремонт климатической системы.'),
    ('i-gauge', 'Подготовка к поездке', 'Проверка перед дальней дорогой или сменой сезона.'),
    ('i-shield', 'Проверка перед покупкой', 'Осмотр автомобиля с пробегом перед сделкой.'),
]


def service_card(ic, title, text, href='services.html', price=True):
    foot = f'<div class="card__foot"><span>Стоимость — {todo("уточнить")}</span>{i("i-arrow")}</div>' if price else ''
    return f'''<a class="card reveal" href="{href}">
  <span class="card__icon">{i(ic)}</span>
  <h3 class="h3">{title}</h3>
  <p class="small">{text}</p>
  {foot}
</a>'''


# Мессенджеры (13.10.2026). Telegram — на номер +7 (962) 494-77-94: ссылка t.me/+номер открывает чат в приложении
# (работает, если в Telegram разрешён поиск по номеру). MAX — на +7 (928) 222-24-64: открыть чат по номеру ссылкой
# MAX не умеет, нужна ссылка на профиль (Профиль → Поделиться). ВРЕМЕННО ведёт на max.ru — заменить ссылкой на профиль.
TELEGRAM_URL = 'https://t.me/+79624947794'
MAX_URL = 'https://max.ru/'
TG_ICON = ('<svg class="msg__icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#2AABEE"/>'
           '<path fill="#fff" d="M5.4 11.8 17.3 7.2c.6-.2 1.1.1.9 1l-2 9.5c-.1.7-.6.8-1.2.5l-3.1-2.3-1.5 1.4c-.2.2-.3.3-.6.3l.2-3.2 5.8-5.3c.3-.2-.1-.4-.4-.2l-7.2 4.5-3.1-1c-.7-.2-.7-.7.1-1z"/></svg>')
MAX_ICON = ('<svg class="msg__icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#5B5BF6"/>'
            '<path fill="#fff" d="M6 16.5V7.5h1.9l4.1 5 4.1-5H18v9h-2v-5.8l-4 4.8-4-4.8v5.8z"/></svg>')


def messengers():
    links = [f'<a class="msg" href="{TELEGRAM_URL}" target="_blank" rel="noopener">{TG_ICON}<span>Telegram</span></a>',
             f'<a class="msg" href="{MAX_URL}" target="_blank" rel="noopener">{MAX_ICON}<span>MAX</span></a>']
    return '<span class="msgs">' + ''.join(links) + '</span>'


def contacts_list():
    rows = [
        ('pin', 'Адрес', SERVICE_ADDR),
        ('phone', 'Телефоны — всегда на связи', PHONE_LINKS),
        ('chat', 'Напишите в мессенджер', messengers()),
        ('i-clock', 'Часы работы', HOURS[0].upper() + HOURS[1:]),
    ]
    return '<dl class="contact-list">' + ''.join(
        f'<div class="contact reveal" style="--d:{n}">{bicon(ic)}<div><dt>{t}</dt><dd>{v}</dd></div></div>'
        for n, (ic, t, v) in enumerate(rows)) + '</dl>'


# Ссылки на карточки автосервиса в картах (сверено 13.10.2026: адрес Коломийцева 38А к2); внешний код на страницу не грузится
MAP_YANDEX = 'https://yandex.ru/maps/org/vagner_motors/169217220279/'
MAP_2GIS = 'https://2gis.ru/stavropol/firm/70000001041090086'

MAP = f'''<div class="map reveal">
  <span class="map__pin">{i("i-pin")}</span>
  <div class="map__card"><span><strong>Wagner Motors</strong> · {SERVICE_ADDR}</span>
    <div class="map__links">
      <a class="btn btn--ghost btn--sm" href="{MAP_YANDEX}" target="_blank" rel="noopener">Яндекс Карты</a>
      <a class="btn btn--ghost btn--sm" href="{MAP_2GIS}" target="_blank" rel="noopener">2ГИС</a>
    </div>
  </div>
</div>'''

# ---------------------------------------------------------------- ГЛАВНАЯ
SCAN = f'''<div class="scan" data-x0="30" data-x1="790" aria-hidden="true">
  <svg viewBox="0 0 800 300" preserveAspectRatio="xMidYMid meet">
    <defs>
      <linearGradient id="beamGrad" x1="0" x2="1"><stop offset="0" stop-color="#e2633b" stop-opacity="0"/><stop offset="1" stop-color="#e2633b" stop-opacity=".3"/></linearGradient>
      <radialGradient id="shadowGrad"><stop offset="0" stop-color="#000" stop-opacity=".8"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
      <clipPath id="scanClip"><rect x="0" y="0" width="0" height="300"/></clipPath>
    </defs>
    <ellipse cx="400" cy="270" rx="380" ry="14" fill="url(#shadowGrad)"/>
    <line class="scan__ground" x1="10" y1="276" x2="790" y2="276"/>
    <image class="scan__img" href="img/cayenne-dim.webp" x="28.5" y="6.9" width="752.4" height="279" preserveAspectRatio="none"/>
    <g class="scan__litwrap" clip-path="url(#scanClip)"><image href="img/cayenne-lit.webp" x="28.5" y="6.9" width="752.4" height="279" preserveAspectRatio="none"/></g>
    <g class="scan__line" transform="translate(30 0)"><rect x="-80" y="40" width="80" height="236" fill="url(#beamGrad)"/><line x1="0" y1="30" x2="0" y2="280"/></g>
  </svg>
  <div class="scan__point" data-x="141" style="--x:17.62%;--y:41.30%"><span class="scan__dot"></span><span class="scan__label">Двигатель {i("i-check")}</span></div>
  <div class="scan__point scan__point--below" data-x="178" style="--x:22.24%;--y:72.05%"><span class="scan__dot"></span><span class="scan__label">Ходовая {i("i-check")}</span></div>
  <div class="scan__point scan__point--below" data-x="352" style="--x:44.06%;--y:28.00%"><span class="scan__dot"></span><span class="scan__label">Электроника {i("i-check")}</span></div>
  <div class="scan__point scan__point--below" data-x="614" style="--x:76.80%;--y:72.50%"><span class="scan__dot"></span><span class="scan__label">Тормоза {i("i-check")}</span></div>
</div>
</div>'''

# На компьютере кнопка открывает карточку с номерами (js/main.js, data-call), на телефоне — обычный звонок
CALL_PHONES_JSON = json.dumps([list(p_) for p_ in PHONES], ensure_ascii=False)
CALL_BTN = f'<a class="btn btn--ghost btn--lg" href="tel:{PHONES[0][0]}" data-call=\'{CALL_PHONES_JSON}\'>{i("i-phone")}Позвонить</a>'

def lift_point(name, px, py, below=False):
    # координаты эскиза 1672×941, кадр (0,100)–(1672,900) → viewBox 800×383
    k = 800 / 1672
    x, y = px * k, (py - 100) * k
    cls = 'scan__point scan__point--below' if below else 'scan__point'
    return f'<div class="{cls}" data-x="{x:.0f}" style="--x:{x / 8:.2f}%;--y:{y / 3.83:.2f}%"><span class="scan__dot"></span><span class="scan__label">{name} {i("i-check")}</span></div>'


LIFT_SCAN = f'''<div class="scan scan--lift" data-x0="10" data-x1="790" data-start="view" aria-hidden="true">
  <svg viewBox="0 0 800 383" preserveAspectRatio="xMidYMid meet">
    <defs>
      <linearGradient id="beamGrad2" x1="0" x2="1"><stop offset="0" stop-color="#e2633b" stop-opacity="0"/><stop offset="1" stop-color="#e2633b" stop-opacity=".3"/></linearGradient>
      <clipPath id="scanClip2"><rect x="0" y="0" width="0" height="383"/></clipPath>
    </defs>
    <image class="scan__img" href="img/lift-dim.webp" x="0" y="0" width="800" height="383" preserveAspectRatio="none"/>
    <g class="scan__litwrap" clip-path="url(#scanClip2)"><image href="img/lift-lit.webp" x="0" y="0" width="800" height="383" preserveAspectRatio="none"/></g>
    <g class="scan__line" transform="translate(10 0)"><rect x="-80" y="0" width="80" height="383" fill="url(#beamGrad2)"/><line x1="0" y1="0" x2="0" y2="383"/></g>
  </svg>
  {lift_point("Тормоза", 760, 690, below=True)}
  {lift_point("Подвеска", 825, 500)}
  {lift_point("Выхлоп", 1160, 650, below=True)}
  {lift_point("Кузов", 1330, 430)}
</div>'''

REPAIR_SECTION = f'''<section class="hero hero--repair">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="container hero__inner">
    <p class="eyebrow reveal">Ремонт и обслуживание</p>
    <h2 class="display reveal" style="--d:1">Ремонт, на&nbsp;который<br>можно положиться.</h2>
    <div class="hero__actions reveal" style="--d:2">
      <a class="btn btn--primary btn--lg" href="booking.html">Записаться</a>
      <a class="btn btn--ghost btn--lg" href="services.html">Все услуги</a>
    </div>
  </div>
  <div class="container">{LIFT_SCAN}</div>
</section>'''

TICKET = f'''<div class="ticket reveal" data-tilt>
  <span class="ticket__shine"></span>
  <div class="ticket__main">
    <span class="ticket__label">Билет участника</span>
    <span class="ticket__prize">Porsche Cayenne</span>
    <dl class="ticket__meta">
      <div><dt>Розыгрыш</dt><dd>{todo("дата")}</dd></div>
      <div><dt>Номер билета</dt><dd>после оплаты</dd></div>
    </dl>
  </div>
  <div class="ticket__stub"><span class="ticket__no">№</span><span class="ticket__code"></span></div>
</div>'''

ACTIONS = ('<button class="btn btn--primary btn--lg" type="button" data-add-to-cart>Добавить в корзину</button>'
           '<a class="btn btn--ghost btn--lg" href="booking.html">Записаться</a>') if SHOP else \
          ('<a class="btn btn--primary btn--lg" href="booking.html">Записаться</a>' + CALL_BTN)

PRIZE_SECTION = f'''<section class="section prize">
  <div class="container prize__grid">
    <div class="prize__text">
      <p class="eyebrow reveal">Акция</p>
      <h2 class="h2 reveal" style="--d:1">Каждая диагностика — билет в&nbsp;розыгрыше Porsche&nbsp;Cayenne.</h2>
      <p class="lead reveal" style="--d:2">Оплатите диагностику и&nbsp;автоматически станьте участником розыгрыша. Номер билета придёт после оплаты.</p>
      <div class="prize__rules reveal" style="--d:3">
        <span class="small">Сроки акции: {todo("с … по …")}</span>
        <a class="link" href="privacy.html#promo">Правила акции {i("i-arrow")}</a>
      </div>
    </div>
    {TICKET}
  </div>
</section>'''

index_body = f'''<section class="hero">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="container hero__inner">
    <p class="eyebrow reveal">Wagner Motors · автосервис</p>
    <h1 class="display reveal" style="--d:1">Диагностика,<br>которая видит всё.</h1>
    <div class="hero__actions reveal" style="--d:2">
      <a class="btn btn--primary btn--lg" href="booking.html">Записаться</a>
      {'<button class="btn btn--ghost btn--lg" type="button" data-add-to-cart>Купить за 5&nbsp;000&nbsp;₽</button>' if SHOP else CALL_BTN}
    </div>
  </div>
  <div class="container">{SCAN}</div>
</section>

{REPAIR_SECTION}

{PRIZE_SECTION if PROMO else ''}

<section class="section theme-light" id="diagnostics">
  <div class="container product">
    <div class="product__media product__media--photo reveal"><img src="img/gallery/g15-1600.webp" alt="Porsche Cayman на подъёмнике в Wagner Motors" loading="lazy" decoding="async"></div>
    <div class="product__body">
      <p class="eyebrow reveal">Главная услуга</p>
      <h2 class="h2 reveal" style="--d:1">Комплексная диагностика</h2>
      {'<div class="price reveal" style="--d:2"><span class="price__value">5&nbsp;000&nbsp;₽</span>' + (f'<span class="badge">{i("i-ticket")}+ билет в розыгрыше</span>' if PROMO else '') + '</div>' if SHOW_PRICE else ''}
      <ul class="checklist reveal" style="--d:3">{CHECKLIST}</ul>
      <div class="product__actions reveal">
        {ACTIONS}
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section__head">
      <p class="eyebrow reveal">Как это работает</p>
      <h2 class="h2 reveal" style="--d:1">Три шага до диагностики</h2>
    </div>
    <div class="steps">
      <div class="step reveal"><div class="step__top">{bicon("chat")}<span class="step__num">01</span></div><h3 class="h3">Оставьте заявку</h3><p class="small">Имя, телефон и&nbsp;автомобиль — меньше минуты.</p></div>
      <div class="step reveal" style="--d:1"><div class="step__top">{bicon("phone")}<span class="step__num">02</span></div><h3 class="h3">Мы перезвоним</h3><p class="small">Подберём удобное время и&nbsp;ответим на&nbsp;вопросы.</p></div>
      <div class="step reveal" style="--d:2"><div class="step__top">{bicon("tools")}<span class="step__num">03</span></div><h3 class="h3">Приезжайте</h3><p class="small">Проводим диагностику и&nbsp;выдаём отчёт.{' Оплаченная диагностика — ваш билет в&nbsp;розыгрыше.' if PROMO else ''}</p></div>
    </div>
  </div>
</section>

<section class="section theme-light">
  <div class="container">
    <div class="section__head section__head--row">
      <div>
        <p class="eyebrow reveal">Услуги</p>
        <h2 class="h2 reveal" style="--d:1">Диагностика — только начало</h2>
        <p class="lead reveal" style="--d:2">Найденное можно сразу устранить у&nbsp;нас.</p>
      </div>
      <a class="link reveal" href="services.html">Все услуги {i("i-arrow")}</a>
    </div>
    <div class="cards">{''.join(price_card(*g, n=n) for n, g in enumerate(PRICES))}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section__head section__head--row">
      <div>
        <p class="eyebrow reveal">Галерея</p>
        <h2 class="h2 reveal" style="--d:1">Мастерская изнутри</h2>
      </div>
      <a class="link reveal" href="gallery.html">Вся галерея {i("i-arrow")}</a>
    </div>
    <div class="bento reveal" data-gallery>
      {''.join(photo_item(*next(p_ for p_ in PHOTOS if p_[0] == k_)) for k_ in ('g01', 'g13', 'g18', 'g15'))}
    </div>
  </div>
</section>

<section class="section theme-light">
  <div class="container">
    <div class="section__head section__head--row">
      <div>
        <p class="eyebrow reveal">Отзывы</p>
        <h2 class="h2 reveal" style="--d:1">Что говорят клиенты</h2>
      </div>
      <a class="link reveal" href="reviews.html">Все отзывы {i("i-arrow")}</a>
    </div>
  </div>
  <div data-rail>
    <div class="rail reveal">{''.join(review(d, t) for d, t in REVIEWS[:6])}</div>
    <div class="container rail-nav">
      <button class="icon-btn" type="button" data-rail-prev aria-label="Предыдущие отзывы">{i("i-chev-left")}</button>
      <button class="icon-btn" type="button" data-rail-next aria-label="Следующие отзывы">{i("i-chev-right")}</button>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section__head">
      <p class="eyebrow reveal">Контакты</p>
      <h2 class="h2 reveal" style="--d:1">Как нас найти</h2>
    </div>
    <div class="contacts">
      {contacts_list()}
      {MAP}
    </div>
    <div class="cta reveal">
      <div>
        <h2 class="h2">Есть вопросы? Звоните, всегда на&nbsp;связи</h2>
        <p class="lead cta__phones">{PHONE_LINKS}</p>
      </div>
      <a class="btn btn--primary btn--lg" href="booking.html">Оставить заявку</a>
    </div>
  </div>
</section>'''

page('index.html', 'Wagner Motors — автосервис',
     'Автосервис Wagner Motors: комплексная диагностика автомобиля' + (' за 5 000 ₽' if SHOW_PRICE else '') + (' и участие в розыгрыше Porsche Cayenne.' if PROMO else ', ремонт и обслуживание.'),
     index_body, scripts=('hero.js', 'gallery.js'))

# ---------------------------------------------------------------- О КОМПАНИИ
about_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow reveal">О компании</p>
    <h1 class="h1 reveal" style="--d:1">Wagner Motors</h1>
    <p class="lead reveal" style="--d:2">{todo("короткое описание компании: кто вы, с какими машинами работаете, чем отличаетесь")}</p>
  </div>
</section>

<section class="section section--flush-top">
  <div class="container">
    <div class="stats">
      <div class="stat reveal"><div class="stat__value">{todo("N")}</div><p class="small">лет работы</p></div>
      <div class="stat reveal" style="--d:1"><div class="stat__value">{todo("N")}</div><p class="small">рабочих постов</p></div>
      <div class="stat reveal" style="--d:2"><div class="stat__value">{todo("N")}</div><p class="small">мастеров в команде</p></div>
      <div class="stat reveal" style="--d:3"><div class="stat__value">{todo("N")}</div><p class="small">автомобилей в год</p></div>
    </div>
  </div>
</section>

<section class="section theme-light">
  <div class="container split">
    <div class="split__media reveal">{ph("Фото фасада или команды", "i-camera", "warm")}</div>
    <div>
      <p class="eyebrow reveal">История</p>
      <h2 class="h2 reveal" style="--d:1">{todo("заголовок истории")}</h2>
      <div class="prose reveal" style="--d:2">
        <p style="margin-top:1.25rem"><span class="sk" style="--w:100%"></span><span class="sk" style="--w:94%"></span><span class="sk" style="--w:97%"></span><span class="sk" style="--w:70%"></span></p>
        <p><span class="sk" style="--w:98%"></span><span class="sk" style="--w:90%"></span><span class="sk" style="--w:55%"></span></p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section__head">
      <p class="eyebrow reveal">Принципы</p>
      <h2 class="h2 reveal" style="--d:1">Как мы работаем</h2>
    </div>
    <div class="cards">
      <div class="card reveal"><span class="card__icon">{i("i-gauge")}</span><h3 class="h3">Сначала диагностика</h3><p class="small">Показываем, что нашли, и&nbsp;объясняем, что срочно, а&nbsp;что может подождать.</p></div>
      <div class="card reveal" style="--d:1"><span class="card__icon">{i("i-doc")}</span><h3 class="h3">Понятная смета</h3><p class="small">Согласуем стоимость до&nbsp;начала работ.</p></div>
      <div class="card reveal" style="--d:2"><span class="card__icon">{i("i-shield")}</span><h3 class="h3">Гарантия</h3><p class="small">Условия гарантии: {todo("срок и на что распространяется")}</p></div>
    </div>
  </div>
</section>

<section class="section theme-light">
  <div class="container">
    <div class="section__head">
      <p class="eyebrow reveal">Команда</p>
      <h2 class="h2 reveal" style="--d:1">Люди, которые чинят ваш автомобиль</h2>
    </div>
    <div class="team">
      {''.join(f'<div class="person reveal" style="--d:{n}">{ph("Фото сотрудника", "i-user", t)}<div class="person__name"><span class="sk" style="--w:70%"></span><span class="sk" style="--w:45%"></span></div></div>' for n, t in enumerate(["steel", "cool", "warm", "olive"]))}
    </div>
  </div>
</section>'''
page('about.html', 'О компании — Wagner Motors', 'Wagner Motors: кто мы и как работаем.', about_body, active='about.html')

# ---------------------------------------------------------------- УСЛУГИ
services_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow reveal">Услуги</p>
    <h1 class="h1 reveal" style="--d:1">Всё для вашего автомобиля</h1>
    <p class="lead reveal" style="--d:2">Начните с&nbsp;диагностики: она покажет, что нужно сделать, а&nbsp;что можно не&nbsp;трогать.</p>
  </div>
</section>

<section class="section section--flush-top">
  <div class="container">
    <div class="feature reveal">
      <div>
        {f'<span class="badge" style="margin-bottom:1rem">{i("i-ticket")}+ билет в розыгрыше Porsche Cayenne</span>' if PROMO else ''}
        <h2 class="h2">Комплексная диагностика</h2>
        {'<div class="price"><span class="price__value">5&nbsp;000&nbsp;₽</span></div>' if SHOW_PRICE else ''}
        <div class="product__actions">
          {ACTIONS}
        </div>
      </div>
      <ul class="checklist">{CHECKLIST}</ul>
    </div>
  </div>
</section>

<section class="section theme-light">
  <div class="container">
    <div class="section__head section__head--row">
      <div>
        <div class="section__icon reveal">{bicon("tools")}</div>
        <h2 class="h2 reveal" style="--d:1">Ремонт и обслуживание</h2>
      </div>
      <p class="lead cta__phones reveal">{PHONE_LINKS}</p>
    </div>
    <nav class="chips reveal" aria-label="Разделы услуг">{''.join(f'<a class="chip" href="#{k}">{t}</a>' for k, _, t, _ in PRICES_PAIRED)}</nav>
    <div class="pricelist">{''.join(price_group(*g, n=n) for n, g in enumerate(PRICES_PAIRED))}</div>
  </div>
</section>'''
page('services.html', 'Услуги — Wagner Motors', 'Диагностика, обслуживание и ремонт автомобилей в Wagner Motors.', services_body, active='services.html')

# ---------------------------------------------------------------- ГАЛЕРЕЯ
gal = [
    ('Фото мастерской', 'warm', 'photo', 'workshop'), ('Видео: как проходит диагностика', 'cool', 'video', 'process'),
    ('Фото подъёмника', 'steel', 'photo', 'workshop'), ('Фото диагностического стенда', 'olive', 'photo', 'process'),
    ('Фото зоны ожидания', 'wine', 'photo', 'workshop'), ('Фото работы мастера', 'cool', 'photo', 'process'),
    ('Видео-экскурсия по сервису', 'warm', 'video', 'workshop'), ('Фото до/после ремонта', 'steel', 'photo', 'process'),
    ('Фото фасада', 'olive', 'photo', 'workshop'),
]
gal_items = ''.join(photo_item(*ph_) for ph_ in PHOTOS)
gallery_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow reveal">Галерея</p>
    <h1 class="h1 reveal" style="--d:1">Мастерская и работа</h1>
    <p class="lead reveal" style="--d:2">Как выглядит сервис и&nbsp;как мы работаем. Нажмите на&nbsp;кадр — листайте свайпом.</p>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container">
    <div class="chips reveal" data-filter-group="#galleryGrid" role="group" aria-label="Фильтр галереи">
      <button class="chip is-active" type="button" data-filter="all" aria-pressed="true">Все</button>
      <button class="chip" type="button" data-filter="workshop" aria-pressed="false">Мастерская</button>
      <button class="chip" type="button" data-filter="process" aria-pressed="false">Работа</button>
      <button class="chip" type="button" data-filter="cars" aria-pressed="false">Автомобили</button>
    </div>
    <div class="gallery-grid reveal" id="galleryGrid" data-gallery>{gal_items}</div>
  </div>
</section>'''
page('gallery.html', 'Галерея — Wagner Motors', 'Фото мастерской и работ автосервиса Wagner Motors.', gallery_body, active='gallery.html', scripts=('gallery.js',))

# ---------------------------------------------------------------- ОТЗЫВЫ
reviews_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow reveal">Отзывы</p>
    <h1 class="h1 reveal" style="--d:1">Что говорят клиенты</h1>
    <p class="lead reveal" style="--d:2">Спасибо большое за&nbsp;тёплые слова!</p>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container">
    <div class="reviews-grid">{''.join(review(d, t, ' reveal') for d, t in REVIEWS)}</div>
  </div>
</section>'''
page('reviews.html', 'Отзывы — Wagner Motors', 'Отзывы клиентов автосервиса Wagner Motors.', reviews_body, active='reviews.html')

# ---------------------------------------------------------------- КОНТАКТЫ
contacts_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow reveal">Контакты</p>
    <h1 class="h1 reveal" style="--d:1">Приезжайте</h1>
    <p class="lead reveal" style="--d:2">Или оставьте заявку — мы&nbsp;перезвоним сами.</p>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container">
    <div class="contacts">
      {contacts_list()}
      {MAP.replace('class="map reveal"', 'class="map map--tall reveal"')}
    </div>
    <div class="cta reveal">
      <div>
        <h2 class="h2">Как добраться</h2>
        <p class="lead">{SERVICE_ADDR}</p>
      </div>
      <a class="btn btn--primary btn--lg" href="booking.html">Записаться</a>
    </div>
  </div>
</section>'''
page('contacts.html', 'Контакты — Wagner Motors', 'Адрес, телефон и часы работы Wagner Motors.', contacts_body, active='contacts.html')

# ---------------------------------------------------------------- ЗАПИСЬ
booking_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow reveal">Запись</p>
    <h1 class="h1 reveal" style="--d:1">Запись на диагностику</h1>
    <p class="lead reveal" style="--d:2">Оставьте заявку — мы&nbsp;перезвоним и&nbsp;подберём удобное время.</p>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container booking">
    <aside class="reveal">
      <h2 class="h3">Что будет дальше</h2>
      <ul class="info-list">
        <li>{bicon("phone", " bicon--sm")}<div><strong>Перезвоним</strong><span class="small">в течение 15 минут в рабочее время</span></div></li>
        <li>{bicon("i-clock", " bicon--sm")}<div><strong>Согласуем время</strong><span class="small">в удобный для вас день</span></div></li>
        <li>{bicon("tools", " bicon--sm")}<div><strong>Проведём диагностику</strong><span class="small">и выдадим отчёт с рекомендациями</span></div></li>
      </ul>
      <p class="small" style="margin-top:1.75rem">Или позвоните сами — всегда на связи:</p>
      <p class="cta__phones" style="margin-top:.35rem;font-weight:600">{PHONE_LINKS}</p>
      <div class="mini-product">
        <div><strong>Комплексная диагностика</strong>{f'<br><span class="badge" style="margin-top:.4rem">{i("i-ticket")}+ билет в розыгрыше</span>' if PROMO else ''}</div>
        {'<span class="mini-product__price">5&nbsp;000&nbsp;₽</span>' if SHOW_PRICE else ''}
      </div>
    </aside>
    <div class="form-card reveal" style="--d:1" data-booking>
      <form class="form" action="#" method="post" data-guard>
        <div class="hp" aria-hidden="true"><label>Не заполняйте это поле<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
        <div class="form__row">
          <div class="field">
            <label class="field__label" for="b-name">Имя</label>
            <input class="input" id="b-name" name="name" autocomplete="name" maxlength="80" data-rule="name" placeholder="Как к вам обращаться">
            <span class="field__error" aria-live="polite"></span>
          </div>
          <div class="field">
            <label class="field__label" for="b-phone">Телефон</label>
            <input class="input" id="b-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" maxlength="24" data-rule="phone" placeholder="+7 (___) ___-__-__">
            <span class="field__error" aria-live="polite"></span>
          </div>
        </div>
        <div class="field">
          <span class="field__label" id="kind-label">Выберите услугу</span>
          <div class="segmented segmented--3" role="radiogroup" aria-labelledby="kind-label">
            <input type="radio" name="kind" id="kind-diag" value="Диагностика" checked><label for="kind-diag">Диагностика</label>
            <input type="radio" name="kind" id="kind-repair" value="Ремонт"><label for="kind-repair">Ремонт</label>
            <input type="radio" name="kind" id="kind-to" value="ТО"><label for="kind-to">ТО</label>
            <span class="segmented__thumb" aria-hidden="true"></span>
          </div>
        </div>
        <div class="field">
          <label class="field__label" for="b-car">Автомобиль <span class="field__opt">— необязательно</span></label>
          <input class="input" id="b-car" name="car" maxlength="80" placeholder="Марка, модель, год">
        </div>
        <div class="field">
          <label class="field__label" for="b-comment">Комментарий <span class="field__opt">— необязательно</span></label>
          <textarea class="input" id="b-comment" name="comment" maxlength="1000" placeholder="Что беспокоит в машине?"></textarea>
        </div>
        <div class="field">
          <label class="check"><input type="checkbox" name="consent" data-rule="consent"><span>Даю <a href="consent.html" target="_blank" rel="noopener">согласие на обработку персональных данных</a> и подтверждаю, что ознакомлен(а) с <a href="privacy.html" target="_blank" rel="noopener">политикой конфиденциальности</a></span></label>
          <span class="field__error" aria-live="polite"></span>
        </div>
        <button class="btn btn--primary btn--lg btn--block" type="submit">Оставить заявку</button>
      </form>
      <div class="success" role="status">
        <div class="success__icon">{i("i-check")}</div>
        <h2 class="h2" tabindex="-1">Заявка принята</h2>
        <p class="lead">Мы перезвоним и подберём удобное время.{' Хотите участвовать в&nbsp;розыгрыше Porsche&nbsp;Cayenne — оплатите диагностику онлайн.' if PROMO and SHOP else ''}</p>
        <div class="success__actions">
          {'<a class="btn btn--primary" href="cart.html" data-add-to-cart>Оплатить онлайн</a>' if SHOP else ''}
          <button class="btn btn--ghost" type="button" data-booking-again>Новая заявка</button>
        </div>
      </div>
    </div>
  </div>
</section>'''
page('booking.html', 'Запись на диагностику — Wagner Motors', 'Оставьте заявку на диагностику — мы перезвоним.', booking_body, scripts=('booking.js',))

# ---------------------------------------------------------------- КОРЗИНА
cart_body = f'''<div data-cart data-state="empty">
<section class="page-hero">
  <div class="container">
    <h1 class="h1 reveal">Корзина</h1>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container">
    <div class="cart-empty empty-state">
      <div class="empty-state__icon">{i("i-cart")}</div>
      <h2 class="h3">В корзине пока пусто</h2>
      <p class="lead">Комплексная диагностика — 5&nbsp;000&nbsp;₽ и&nbsp;билет в&nbsp;розыгрыше Porsche&nbsp;Cayenne.</p>
      <div class="success__actions"><button class="btn btn--primary btn--lg" type="button" data-add-to-cart>Добавить диагностику</button></div>
    </div>

    <div class="cart-done empty-state">
      <div class="success__icon">{i("i-check")}</div>
      <h2 class="h2">Оплата прошла</h2>
      <p class="lead">Тестовый режим: платёж не проводился. После подключения оплаты здесь будет номер билета и&nbsp;чек.</p>
      <div class="success__actions"><a class="btn btn--ghost btn--lg" href="index.html">На главную</a></div>
    </div>

    <div class="cart">
      <div class="cart__main">
        <div class="line-item">
          {ph("", "i-gauge", "warm").replace('class="ph ', 'class="ph line-item__thumb ')}
          <div>
            <h2 class="h3">Комплексная диагностика</h2>
            <p class="small">5&nbsp;000&nbsp;₽ за автомобиль · + билет в розыгрыше</p>
          </div>
          <div class="line-item__side">
            <span class="line-item__total" data-line-total>5&nbsp;000&nbsp;₽</span>
            <div class="line-item__actions">
              <div class="stepper" role="group" aria-label="Количество автомобилей">
                <button type="button" data-minus aria-label="Меньше">{i("i-minus")}</button>
                <output data-qty aria-live="polite">1</output>
                <button type="button" data-plus aria-label="Больше">{i("i-plus")}</button>
              </div>
              <button class="icon-btn" type="button" data-remove aria-label="Удалить из корзины">{i("i-trash")}</button>
            </div>
          </div>
        </div>

        <div class="form-card">
          <h2 class="h3 form-head" style="margin-bottom:1.25rem">Оформление</h2>
          <form class="form" id="checkout" action="#" method="post" data-guard>
            <div class="hp" aria-hidden="true"><label>Не заполняйте это поле<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
            <div class="form__row">
              <div class="field">
                <label class="field__label" for="c-name">Имя</label>
                <input class="input" id="c-name" name="name" autocomplete="name" maxlength="80" data-rule="name">
                <span class="field__error" aria-live="polite"></span>
              </div>
              <div class="field">
                <label class="field__label" for="c-phone">Телефон</label>
                <input class="input" id="c-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" maxlength="24" data-rule="phone" placeholder="+7 (___) ___-__-__">
                <span class="field__error" aria-live="polite"></span>
              </div>
            </div>
            <div class="form__row">
              <div class="field">
                <label class="field__label" for="c-email">Почта для чека</label>
                <input class="input" id="c-email" name="email" type="email" autocomplete="email" maxlength="120" data-rule="email" placeholder="name@example.ru">
                <span class="field__error" aria-live="polite"></span>
              </div>
              <div class="field">
                <label class="field__label" for="c-car">Автомобиль <span class="field__opt">— необязательно</span></label>
                <input class="input" id="c-car" name="car" maxlength="80" placeholder="Марка, модель, год">
              </div>
            </div>
            <div class="field">
              <span class="field__label" id="pm-label">Способ оплаты</span>
              <div class="segmented" role="radiogroup" aria-labelledby="pm-label">
                <input type="radio" name="pm" id="pm-card" value="card" checked><label for="pm-card">{i("i-card")}Картой</label>
                <input type="radio" name="pm" id="pm-sbp" value="sbp"><label for="pm-sbp">{i("i-qr")}СБП</label>
                <span class="segmented__thumb" aria-hidden="true"></span>
              </div>
            </div>
            <div class="field">
              <label class="check"><input type="checkbox" name="consent" data-rule="consent"><span>Даю <a href="consent.html" target="_blank" rel="noopener">согласие на обработку персональных данных</a> и подтверждаю, что ознакомлен(а) с <a href="privacy.html" target="_blank" rel="noopener">политикой конфиденциальности</a></span></label>
              <span class="field__error" aria-live="polite"></span>
            </div>
          </form>
        </div>
      </div>

      <aside class="cart__summary">
        <div class="summary">
          <h2 class="h3" style="margin-bottom:.75rem">Итого</h2>
          <div class="summary__row"><span data-sum-qty>Диагностика × 1</span><span data-line-total>5&nbsp;000&nbsp;₽</span></div>
          <div class="summary__row"><span>Билеты в розыгрыше</span><span data-sum-tickets>1 билет</span></div>
          <div class="summary__row summary__row--total"><span>К оплате</span><span data-sum-total>5&nbsp;000&nbsp;₽</span></div>
          <button class="btn btn--primary btn--lg btn--block" type="submit" form="checkout" data-pay>Оплатить 5&nbsp;000&nbsp;₽</button>
          <p class="dev-note" style="margin-top:.9rem">Черновик: оплата в тестовом режиме, платёжный сервис подключим позже</p>
        </div>
      </aside>
    </div>
  </div>
</section>
</div>

<div class="sheet" data-pay-sheet role="dialog" aria-modal="true" aria-labelledby="sheetTitle">
  <div class="sheet__grabber"></div>
  <h2 class="h3" id="sheetTitle">Оплата</h2>
  <p class="small">Здесь откроется страница платёжного сервиса. Сейчас — тестовый режим, деньги не списываются.</p>
  <div class="sheet__amount" data-sheet-amount>5&nbsp;000&nbsp;₽</div>
  <button class="btn btn--primary btn--lg btn--block" type="button" data-sheet-confirm data-autofocus>Имитировать оплату</button>
  <button class="btn btn--ghost btn--lg btn--block" type="button" data-sheet-close>Отмена</button>
</div>'''
page('cart.html', 'Корзина — Wagner Motors', 'Корзина и оплата диагностики Wagner Motors.', cart_body, scripts=('cart.js',))

# ---------------------------------------------------------------- ЮРИДИЧЕСКОЕ (152-ФЗ)
# Шаблон по 152-ФЗ «О персональных данных». Реквизиты оператора, сроки и подрядчиков
# заполнить данными клиента (не выдумывать), перед запуском — проверка юристом.
# Меняя смысл согласия, обнови LEGAL_DATE (и CONSENT_VERSION, когда заявки начнут уходить на сервер).
LEGAL_DATE = '12.10.2026'
# Реквизиты — из файла «Реквизиты ООО Вагнер Моторс.pdf» (получен 13.10.2026). ОГРН в файле нет.
OP_NAME = 'Общество с ограниченной ответственностью «ВАГНЕР МОТОРС» (ООО «ВАГНЕР МОТОРС»)'
OP_INN = '2623033488'
OP_KPP = '262301001'
OP_ADDR = 'Ставропольский край, Шпаковский р-н, г.&nbsp;Михайловск, ул.&nbsp;Буденного, домовладение&nbsp;57'
SITE = todo('адрес сайта')
PD_TERM = '1 (одного) года'
PROCESSORS = todo('перечень лиц, которым поручена обработка (хостинг сайта, облачный сервис приёма заявок, мессенджер для уведомлений) с наименованиями и адресами')

PD_LIST = ['имя', 'номер телефона', 'марка, модель и год выпуска автомобиля', 'выбранная услуга (диагностика, ремонт, ТО)',
           'текст комментария к заявке'] + (['адрес электронной почты (для отправки чека при онлайн-оплате)'] if SHOP else [])
PD_ITEMS = ''.join(f'<li>{x}</li>' for x in PD_LIST)
ACTIONS = ('сбор, запись, систематизация, накопление, хранение, уточнение (обновление, изменение), извлечение, '
           'использование, передача (предоставление, доступ) лицам, которым поручена обработка, блокирование, удаление, уничтожение')
OPERATOR_LINE = f'{OP_NAME}, ИНН {OP_INN}, КПП {OP_KPP}, адрес: {OP_ADDR}'

PROMO_RULES = f'''    <h2 class="h3" id="promo">Правила акции «Розыгрыш Porsche Cayenne»</h2>
    <p>{todo("организатор, сроки, порядок участия и определения победителя, вручение приза, налоги")}</p>'''

privacy_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow">Документы</p>
    <h1 class="h1">Политика конфиденциальности</h1>
    <p class="lead">Политика в отношении обработки персональных данных. Редакция от {LEGAL_DATE}.</p>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container legal">
    <h2 class="h3">1. Общие положения</h2>
    <p>1.1. Настоящая Политика определяет порядок обработки персональных данных и меры по обеспечению их безопасности и составлена в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных» (далее — Закон).</p>
    <p>1.2. Оператор персональных данных — {OPERATOR_LINE} (далее — Оператор).</p>
    <p>1.3. Политика применяется ко всей информации, которую Оператор получает о посетителях сайта {SITE} (далее — Сайт), и публикуется в свободном доступе в соответствии с ч. 2 ст. 18.1 Закона.</p>
    <p>1.4. Оператор ставит своей целью соблюдение прав и свобод человека и гражданина при обработке его персональных данных, в том числе защиту прав на неприкосновенность частной жизни, личную и семейную тайну.</p>

    <h2 class="h3">2. Основные понятия</h2>
    <p>Персональные данные — любая информация, относящаяся прямо или косвенно к определённому или определяемому физическому лицу (субъекту персональных данных). Обработка персональных данных — любое действие или совокупность действий с персональными данными, совершаемых с использованием средств автоматизации или без них. Иные термины используются в значениях, установленных Законом.</p>

    <h2 class="h3">3. Какие данные обрабатываются</h2>
    <p>3.1. Оператор обрабатывает персональные данные, которые пользователь сам указывает в формах на Сайте:</p>
    <ul>{PD_ITEMS}</ul>
    <p>3.2. Сайт не использует файлы cookie, системы веб-аналитики и счётчики посещений и не собирает данные о поведении пользователей. При открытии страниц технические данные (IP-адрес, сведения о браузере) могут автоматически фиксироваться в журналах хостинг-провайдера: {todo("наименование хостинг-провайдера и страна размещения серверов")}.</p>
    <p>3.3. Оператор не обрабатывает специальные категории персональных данных (сведения о здоровье, расовой и национальной принадлежности, политических взглядах, религиозных убеждениях) и биометрические персональные данные.</p>

    <h2 class="h3">4. Цели обработки</h2>
    <ul>
      <li>приём и обработка заявки на диагностику, ремонт или техническое обслуживание автомобиля;</li>
      <li>обратный звонок, консультация и согласование времени визита;</li>
      <li>исполнение договора на оказание услуг, стороной которого является пользователь.</li>
    </ul>

    <h2 class="h3">5. Правовые основания</h2>
    <p>Обработка осуществляется на основании согласия субъекта персональных данных (п. 1 ч. 1 ст. 6 Закона), которое пользователь даёт отдельно, отмечая соответствующее поле в форме, а также для заключения и исполнения договора, стороной которого является субъект персональных данных (п. 5 ч. 1 ст. 6 Закона). Текст согласия размещён на странице <a href="consent.html">«Согласие на обработку персональных данных»</a>.</p>

    <h2 class="h3">6. Порядок и условия обработки</h2>
    <p>6.1. Оператор совершает с персональными данными следующие действия: {ACTIONS}. Обработка ведётся с использованием средств автоматизации и без них (смешанная обработка).</p>
    <p>6.2. При сборе персональных данных граждан Российской Федерации запись, систематизация, накопление, хранение, уточнение и извлечение осуществляются с использованием баз данных, находящихся на территории Российской Федерации (ч. 5 ст. 18 Закона).</p>
    <p>6.3. Оператор вправе поручить обработку персональных данных другому лицу на основании договора (ч. 3 ст. 6 Закона). Такое лицо обязано соблюдать принципы и правила обработки, предусмотренные Законом, и конфиденциальность данных. Лица, которым поручена обработка: {PROCESSORS}.</p>
    <p>6.4. Трансграничная передача персональных данных не осуществляется.</p>
    <p>6.5. Оператор не распространяет персональные данные и не раскрывает их третьим лицам без согласия субъекта, если иное не предусмотрено федеральным законом.</p>

    <h2 class="h3">7. Сроки обработки и хранения</h2>
    <p>7.1. Персональные данные обрабатываются до достижения целей обработки или до отзыва согласия, но не дольше {PD_TERM} с момента получения, если более длительный срок не установлен федеральным законом или договором.</p>
    <p>7.2. При достижении целей обработки или отзыве согласия персональные данные уничтожаются в срок, не превышающий 30 дней, если иное не предусмотрено Законом (ч. 4 и 5 ст. 21 Закона).</p>

    <h2 class="h3">8. Права субъекта персональных данных</h2>
    <p>Пользователь имеет право:</p>
    <ul>
      <li>получать сведения об обработке своих персональных данных (ст. 14 Закона);</li>
      <li>требовать уточнения, блокирования или уничтожения данных, если они неполные, устаревшие, неточные, незаконно полученные или не нужны для заявленной цели;</li>
      <li>отозвать согласие на обработку персональных данных;</li>
      <li>обжаловать действия или бездействие Оператора в уполномоченный орган по защите прав субъектов персональных данных (Роскомнадзор) или в суд.</li>
    </ul>
    <p>Запросы и отзыв согласия направляются Оператору в письменной форме почтой по адресу: {OP_ADDR}. Оператор отвечает на запрос в течение 10 рабочих дней с даты получения; срок может быть продлён не более чем на 5 рабочих дней с уведомлением о причинах (ч. 3 ст. 14, ст. 20 Закона).</p>

    <h2 class="h3">9. Меры по защите персональных данных</h2>
    <p>Оператор принимает правовые, организационные и технические меры, необходимые для защиты персональных данных от неправомерного или случайного доступа, уничтожения, изменения, блокирования, копирования, предоставления и распространения (ст. 18.1 и 19 Закона): назначает лицо, ответственное за организацию обработки персональных данных, издаёт локальные акты по вопросам обработки, ограничивает доступ к данным, использует защищённое соединение (HTTPS) при передаче данных с Сайта, ведёт учёт машинных носителей и контроль принимаемых мер.</p>

    <h2 class="h3">10. Заключительные положения</h2>
    <p>Оператор вправе вносить изменения в Политику. Новая редакция вступает в силу с момента её размещения на Сайте. Действующая редакция всегда доступна на этой странице.</p>
{PROMO_RULES if PROMO else ''}
  </div>
</section>'''
page('privacy.html', 'Политика конфиденциальности — Wagner Motors', 'Политика Wagner Motors в отношении обработки персональных данных по 152-ФЗ.', privacy_body)

consent_body = f'''<section class="page-hero">
  <div class="container">
    <p class="eyebrow">Документы</p>
    <h1 class="h1">Согласие на обработку персональных данных</h1>
    <p class="lead">Редакция от {LEGAL_DATE}.</p>
  </div>
</section>
<section class="section section--flush-top">
  <div class="container legal">
    <p>Я, субъект персональных данных, отмечая поле «Даю согласие на обработку персональных данных» в форме на сайте {SITE} и отправляя форму, свободно, своей волей и в своём интересе, конкретно, предметно, информированно, сознательно и однозначно даю согласие на обработку моих персональных данных в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных» на следующих условиях.</p>

    <h2 class="h3">1. Оператор</h2>
    <p>{OPERATOR_LINE}.</p>

    <h2 class="h3">2. Цели обработки</h2>
    <p>Приём и обработка моей заявки на диагностику, ремонт или техническое обслуживание автомобиля, обратный звонок, консультация, согласование времени визита и оказание услуг.</p>

    <h2 class="h3">3. Перечень персональных данных</h2>
    <ul>{PD_ITEMS}</ul>

    <h2 class="h3">4. Действия с персональными данными и способы обработки</h2>
    <p>{ACTIONS[0].upper() + ACTIONS[1:]}. Обработка осуществляется с использованием средств автоматизации и без них. Хранение осуществляется в базах данных на территории Российской Федерации.</p>

    <h2 class="h3">5. Лица, которым может быть поручена обработка</h2>
    <p>{PROCESSORS}.</p>

    <h2 class="h3">6. Срок действия и порядок отзыва</h2>
    <p>Согласие действует до достижения целей обработки, но не дольше {PD_TERM} с момента его предоставления. Я вправе в любой момент отозвать согласие, направив Оператору письменное заявление почтой по адресу: {OP_ADDR}. В случае отзыва Оператор прекращает обработку и уничтожает персональные данные в срок, не превышающий 30 дней с даты поступления отзыва, если иное не предусмотрено федеральным законом (ч. 2 ст. 9, ч. 5 ст. 21 Закона).</p>

    <h2 class="h3">7. Подтверждение</h2>
    <p>Я подтверждаю, что ознакомлен(а) с <a href="privacy.html">Политикой в отношении обработки персональных данных</a>, а также с правами и обязанностями субъекта персональных данных, предусмотренными главой 3 Закона.</p>
  </div>
</section>'''
page('consent.html', 'Согласие на обработку персональных данных — Wagner Motors', 'Согласие на обработку персональных данных для заявок на сайте Wagner Motors.', consent_body)

print('ok')
