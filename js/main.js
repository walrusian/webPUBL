/* Wagner Motors — общие скрипты: навигация, меню, появление блоков, корзина, тосты, формы, шторка. */
(function () {
  'use strict';

  const { Spring, VelocityTracker, project, rubberband, reduceMotion } = window.Fluid;

  const PRICE = 5000;      // стоимость диагностики, ₽
  const MAX_QTY = 5;       // сколько диагностик можно положить в корзину
  const CART_KEY = 'wagner.cart';

  // iOS включает :active (мгновенный отклик кнопок) только при наличии touchstart-слушателя
  document.addEventListener('touchstart', () => {}, { passive: true });

  const plural = (n, [one, few, many]) => {
    const m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
  };
  const money = (n) => n.toLocaleString('ru-RU') + ' ₽';

  /* ---------- Навигация ---------- */
  const nav = document.querySelector('.nav');
  const lightSections = document.querySelectorAll('.theme-light');
  const onScroll = () => {
    if (!nav) return;
    nav.classList.toggle('is-scrolled', window.scrollY > 8);
    // Какая секция сейчас под шапкой — светлая или тёмная
    const y = nav.offsetHeight / 2;
    let light = false;
    lightSections.forEach((s) => {
      const r = s.getBoundingClientRect();
      if (r.top <= y && r.bottom >= y) light = true;
    });
    nav.classList.toggle('is-light', light);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Мобильное меню ---------- */
  const burger = document.querySelector('.burger');
  const menu = document.getElementById('menu');
  const menuScrim = document.querySelector('.menu-scrim');

  function setMenu(open) {
    if (!menu) return;
    menu.classList.toggle('is-open', open);
    menuScrim.classList.toggle('is-open', open);
    burger.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  }
  if (burger && menu) {
    burger.addEventListener('click', () => setMenu(!menu.classList.contains('is-open')));
    menuScrim.addEventListener('click', () => setMenu(false));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) { setMenu(false); burger.focus(); }
    });
    window.matchMedia('(min-width: 901px)').addEventListener('change', (e) => e.matches && setMenu(false));
  }

  /* ---------- Появление блоков при скролле ---------- */
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-visible'));
  }

  /* ---------- Корзина ---------- */
  // В localStorage только количество диагностик — никаких личных данных
  let memoryQty = 0;
  const Cart = {
    price: PRICE,
    max: MAX_QTY,
    get qty() {
      try {
        const v = JSON.parse(localStorage.getItem(CART_KEY));
        return Math.max(0, Math.min(MAX_QTY, (v && v.qty) | 0));
      } catch (e) { return memoryQty; }
    },
    set qty(n) {
      n = Math.max(0, Math.min(MAX_QTY, n | 0));
      memoryQty = n;
      try {
        if (n) localStorage.setItem(CART_KEY, JSON.stringify({ qty: n }));
        else localStorage.removeItem(CART_KEY);
      } catch (e) { /* приватный режим — живём в памяти */ }
      renderBadge(true);
      document.dispatchEvent(new CustomEvent('cart:change', { detail: { qty: n } }));
    },
  };

  const badges = document.querySelectorAll('.cart-btn__badge');
  // «Толчок» значка: пружина получает импульс и возвращается к 1 — отклик на действие
  const badgeSpring = new Spring(1, {
    damping: 0.6, response: 0.32, precision: 0.001,
    onUpdate: (v) => badges.forEach((b) => { b.style.transform = `scale(${v})`; }),
  });
  function renderBadge(animate) {
    const q = Cart.qty;
    badges.forEach((b) => { b.textContent = q; b.hidden = q === 0; });
    document.querySelectorAll('.cart-btn').forEach((btn) => {
      btn.setAttribute('aria-label', q ? `Корзина: ${q} ${plural(q, ['позиция', 'позиции', 'позиций'])}` : 'Корзина пуста');
    });
    if (animate && q > 0) badgeSpring.to(1, { velocity: 9 });
  }
  renderBadge(false);
  window.addEventListener('storage', (e) => { if (e.key === CART_KEY) renderBadge(true); });

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-add-to-cart]');
    if (!btn) return;
    if (Cart.qty > 0) {
      toast('Диагностика уже в корзине', { action: { label: 'Открыть', href: 'cart.html' } });
      return;
    }
    Cart.qty = 1;
    toast('Диагностика добавлена в корзину', { action: { label: 'Оформить', href: 'cart.html' } });
  });

  /* ---------- Тост ---------- */
  // Появляется снизу и уходит тем же путём
  let toastEl = null;
  let toastTimer = 0;
  function toast(text, opts = {}) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'toast';
      toastEl.setAttribute('role', 'status');
      toastEl.setAttribute('aria-live', 'polite');
      document.body.append(toastEl);
      toastEl.addEventListener('pointerenter', () => clearTimeout(toastTimer));
      toastEl.addEventListener('pointerleave', () => { toastTimer = setTimeout(hideToast, 2000); });
    }
    toastEl.textContent = '';
    const span = document.createElement('span');
    span.textContent = text;
    toastEl.append(span);
    if (opts.action) {
      const a = document.createElement(opts.action.href ? 'a' : 'button');
      a.className = 'btn btn--primary btn--sm';
      a.textContent = opts.action.label;
      if (opts.action.href) a.href = opts.action.href;
      else {
        a.type = 'button';
        a.addEventListener('click', () => { opts.action.onClick(); hideToast(); });
      }
      toastEl.append(a);
    }
    requestAnimationFrame(() => toastEl.classList.add('is-visible'));
    clearTimeout(toastTimer);
    toastTimer = setTimeout(hideToast, opts.duration || 4000);
  }
  function hideToast() { if (toastEl) toastEl.classList.remove('is-visible'); }

  /* ---------- Формы: маска телефона и проверка по месту ---------- */
  const RULES = {
    name: (v) => v.trim().length >= 2 || 'Как к вам обращаться?',
    phone: (v) => v.replace(/\D/g, '').length === 11 || 'Нужно 10 цифр после +7',
    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) || 'Проверьте адрес почты',
    required: (v) => v.trim().length > 0 || 'Заполните поле',
    consent: (v, inp) => inp.checked || 'Без согласия мы не сможем обработать заявку',
  };

  function formatPhone(raw) {
    let d = raw.replace(/\D/g, '');
    if (!d) return '';
    if (d.length > 11 && /^7[78]/.test(d)) d = '7' + d.slice(2); // вставили «+7 8…» — лишняя восьмёрка
    if (d[0] === '8') d = '7' + d.slice(1);
    if (d[0] !== '7') d = '7' + d;
    const p = d.slice(1, 11);
    let out = '+7';
    if (p.length) out += ' (' + p.slice(0, 3);
    if (p.length >= 3) out += ')';
    if (p.length > 3) out += ' ' + p.slice(3, 6);
    if (p.length > 6) out += '-' + p.slice(6, 8);
    if (p.length > 8) out += '-' + p.slice(8, 10);
    return out;
  }

  function checkField(inp) {
    const rule = RULES[inp.dataset.rule];
    if (!rule) return true;
    const res = rule(inp.value, inp);
    const ok = res === true;
    const field = inp.closest('.field');
    if (field) {
      field.classList.toggle('is-invalid', !ok);
      const err = field.querySelector('.field__error');
      if (err) err.textContent = ok ? '' : res;
    }
    inp.setAttribute('aria-invalid', String(!ok));
    return ok;
  }

  function initForm(form, onValid) {
    form.noValidate = true;
    form.querySelectorAll('input[type="tel"]').forEach((tel) => {
      tel.addEventListener('input', (e) => {
        if (e.inputType && e.inputType.startsWith('delete')) return; // не мешаем стирать
        tel.value = formatPhone(tel.value);
      });
      tel.addEventListener('blur', () => { if (tel.value.replace(/\D/g, '') === '7') tel.value = ''; });
    });
    const fields = [...form.querySelectorAll('[data-rule]')];
    const touched = new WeakSet();
    fields.forEach((inp) => {
      // Проверяем после ухода с поля, дальше — на каждом вводе, чтобы ошибка исчезала сразу
      inp.addEventListener('blur', () => { if (inp.type !== 'checkbox') { touched.add(inp); checkField(inp); } });
      inp.addEventListener(inp.type === 'checkbox' ? 'change' : 'input', () => {
        if (inp.type === 'checkbox' || touched.has(inp)) checkField(inp);
      });
    });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      let first = null;
      fields.forEach((inp) => {
        touched.add(inp);
        if (!checkField(inp) && !first) first = inp;
      });
      if (first) { first.focus(); return; }
      onValid(new FormData(form));
    });
  }

  /* ---------- Шторка снизу: тянется пальцем, бросок вниз закрывает ---------- */
  function createSheet(el) {
    const scrim = document.createElement('div');
    scrim.className = 'sheet-scrim';
    el.before(scrim);
    let isOpen = false;
    let height = 0;
    let lastFocus = null;

    const render = (v) => {
      el.style.transform = `translate(-50%, ${v}px)`;
      scrim.style.opacity = String(height ? Math.max(0, Math.min(1, 1 - v / height)) : 0);
    };
    const y = new Spring(0, {
      damping: 1, response: 0.38, precision: 0.5, onUpdate: render,
      onRest: () => { if (!isOpen) el.style.visibility = 'hidden'; },
    });

    function show() {
      lastFocus = document.activeElement;
      el.style.visibility = 'visible';
      height = el.offsetHeight + 24;
      if (!y.isAnimating && !isOpen) y.set(height); // из закрытого состояния — снизу; иначе с текущей точки
      isOpen = true;
      scrim.style.pointerEvents = 'auto';
      document.documentElement.classList.add('is-locked');
      y.to(0, { damping: 1, response: 0.38 });
      const f = el.querySelector('[data-autofocus]');
      if (f) f.focus({ preventScroll: true });
    }
    function hide(velocity = 0) {
      if (!isOpen) return;
      isOpen = false;
      height = el.offsetHeight + 24;
      scrim.style.pointerEvents = 'none';
      document.documentElement.classList.remove('is-locked');
      y.to(height, { velocity, damping: 1, response: 0.35 });
      if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    }

    scrim.addEventListener('click', () => hide());
    el.querySelectorAll('[data-sheet-close]').forEach((b) => b.addEventListener('click', () => hide()));
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isOpen) hide(); });

    // Перетаскивание: 1:1 за пальцем, вверх — резиновое сопротивление
    const tracker = new VelocityTracker();
    let drag = null;
    el.addEventListener('pointerdown', (e) => {
      if (!isOpen || e.button > 0 || e.target.closest('button, a, input, label')) return;
      el.setPointerCapture(e.pointerId);
      drag = { id: e.pointerId, y0: e.clientY, base: y.value };
      y.stop();
      tracker.reset();
      tracker.push(e.clientY);
    });
    el.addEventListener('pointermove', (e) => {
      if (!drag || e.pointerId !== drag.id) return;
      tracker.push(e.clientY);
      let v = drag.base + (e.clientY - drag.y0);
      if (v < 0) v = -rubberband(-v, height);
      y.set(v);
    });
    const end = (e) => {
      if (!drag || e.pointerId !== drag.id) return;
      drag = null;
      const v = tracker.velocity();
      const landing = y.value + project(v);
      if (landing > height * 0.5) hide(v);
      else y.to(0, { velocity: v, damping: 0.8, response: 0.3 }); // после броска — лёгкий отскок
    };
    el.addEventListener('pointerup', end);
    el.addEventListener('pointercancel', end);

    return { show, hide, get isOpen() { return isOpen; } };
  }

  /* ---------- Билет: наклон за курсором ---------- */
  // Оси X и Y — независимые пружины, чтобы движение не рассинхронизировалось
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
  document.querySelectorAll('[data-tilt]').forEach((card) => {
    if (!fine.matches || reduceMotion.matches) return;
    let rx, ry;
    const apply = () => {
      card.style.transform = `perspective(900px) rotateX(${rx.value}deg) rotateY(${ry.value}deg)`;
    };
    rx = new Spring(0, { damping: 1, response: 0.5, precision: 0.01, onUpdate: apply });
    ry = new Spring(0, { damping: 1, response: 0.5, precision: 0.01, onUpdate: apply });
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      ry.to(px * 12);
      rx.to(-py * 10);
      card.style.setProperty('--mx', `${(px + 0.5) * 100}%`);
      card.style.setProperty('--my', `${(py + 0.5) * 100}%`);
    });
    card.addEventListener('pointerleave', () => { rx.to(0); ry.to(0); });
  });

  /* ---------- Лента отзывов: кнопки листания ---------- */
  document.querySelectorAll('[data-rail]').forEach((wrap) => {
    const rail = wrap.querySelector('.rail');
    const prev = wrap.querySelector('[data-rail-prev]');
    const next = wrap.querySelector('[data-rail-next]');
    if (!rail || !prev || !next) return;
    const stepSize = () => (rail.firstElementChild ? rail.firstElementChild.offsetWidth + 16 : 300);
    const update = () => {
      prev.disabled = rail.scrollLeft <= 2;
      next.disabled = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 2;
    };
    const behavior = () => (reduceMotion.matches ? 'auto' : 'smooth');
    prev.addEventListener('click', () => rail.scrollBy({ left: -stepSize(), behavior: behavior() }));
    next.addEventListener('click', () => rail.scrollBy({ left: stepSize(), behavior: behavior() }));
    rail.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  /* ---------- Отзывы: одинаковые карточки, длинный текст — в шторке ---------- */
  const reviews = document.querySelectorAll('.review');
  if (reviews.length) {
    const sheetEl = document.createElement('div');
    sheetEl.className = 'sheet sheet--review';
    sheetEl.setAttribute('role', 'dialog');
    sheetEl.setAttribute('aria-modal', 'true');
    sheetEl.setAttribute('aria-label', 'Отзыв клиента');
    sheetEl.innerHTML = '<div class="sheet__grabber"></div><div data-review-body></div>' +
      '<button class="btn btn--ghost btn--lg btn--block" type="button" data-sheet-close>Закрыть</button>';
    document.body.append(sheetEl);
    const reviewSheet = createSheet(sheetEl);
    const body = sheetEl.querySelector('[data-review-body]');

    const markTruncated = () => {
      reviews.forEach((card) => {
        const text = card.querySelector('.review__text');
        let more = card.querySelector('.review__more');
        const cut = text.scrollHeight > text.clientHeight + 2;
        if (cut && !more) {
          more = document.createElement('button');
          more.type = 'button';
          more.className = 'review__more';
          more.textContent = 'Читать полностью';
          text.after(more);
          more.addEventListener('click', () => {
            body.textContent = '';
            body.append(card.querySelector('.stars').cloneNode(true), text.cloneNode(true));
            const date = card.querySelector('.review__who .small');
            if (date) {
              const d = document.createElement('p');
              d.className = 'small';
              d.textContent = date.textContent;
              body.append(d);
            }
            reviewSheet.show();
          });
        } else if (!cut && more) {
          more.remove();
        }
      });
    };
    markTruncated();
    let rt = 0;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(markTruncated, 150); });
  }

  document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });

  window.Wagner = { Cart, toast, initForm, createSheet, plural, money };
})();
