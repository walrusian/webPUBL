/*
 * Галерея: лайтбокс со свайпами.
 * — открывается из той плитки, по которой нажали, и закрывается обратно в неё;
 * — свайп влево/вправо идёт 1:1 за пальцем, бросок «докатывается» по инерции к ближайшему кадру;
 * — у краёв резиновое сопротивление; смахивание вниз закрывает;
 * — любую анимацию можно перехватить пальцем на середине.
 */
(function () {
  'use strict';

  const { Spring, VelocityTracker, project, rubberband, clamp } = window.Fluid;
  const groups = document.querySelectorAll('[data-gallery]');
  if (!groups.length) return;

  const icon = (id) => `<svg class="i" aria-hidden="true"><use href="#${id}"/></svg>`;
  const lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Просмотр галереи');
  lb.innerHTML = `
    <div class="lightbox__backdrop"></div>
    <div class="lightbox__track"></div>
    <div class="lightbox__ui">
      <span class="lightbox__counter" aria-live="polite"></span>
      <button class="lb-btn lightbox__close" type="button" aria-label="Закрыть">${icon('i-close')}</button>
    </div>
    <button class="lb-btn lightbox__prev" type="button" aria-label="Предыдущее">${icon('i-chev-left')}</button>
    <button class="lb-btn lightbox__next" type="button" aria-label="Следующее">${icon('i-chev-right')}</button>
    <p class="lightbox__caption"></p>`;
  document.body.append(lb);

  const backdrop = lb.querySelector('.lightbox__backdrop');
  const track = lb.querySelector('.lightbox__track');
  const ui = [lb.querySelector('.lightbox__ui'), lb.querySelector('.lightbox__caption'),
    lb.querySelector('.lightbox__prev'), lb.querySelector('.lightbox__next')];
  const counter = lb.querySelector('.lightbox__counter');
  const caption = lb.querySelector('.lightbox__caption');
  const btnClose = lb.querySelector('.lightbox__close');
  const btnPrev = lb.querySelector('.lightbox__prev');
  const btnNext = lb.querySelector('.lightbox__next');

  let items = [];
  let index = 0;
  let W = window.innerWidth;
  let H = window.innerHeight;
  let isOpen = false;
  let origin = null;       // откуда «вырастает» кадр: смещение и масштаб плитки
  let medias = [];

  const sx = new Spring(0, { damping: 1, response: 0.4, precision: 0.5, onUpdate: render });  // лента по X
  const sy = new Spring(0, { damping: 1, response: 0.35, precision: 0.5, onUpdate: render }); // смахивание по Y
  const sp = new Spring(0, {                                                                   // присутствие 0…1
    damping: 1, response: 0.38, precision: 0.002, onUpdate: render,
    onRest: (v) => {
      if (!isOpen && v === 0) { lb.classList.remove('is-open'); track.textContent = ''; medias = []; }
    },
  });

  function render() {
    track.style.transform = `translate3d(${sx.value}px, ${sy.value}px, 0)`;
    const presence = clamp(sp.value, 0, 1);
    const pull = Math.min(Math.abs(sy.value) / (H * 0.6), 1);
    const fade = presence * (1 - pull);
    backdrop.style.opacity = String(fade);
    ui.forEach((el) => { el.style.opacity = String(Math.max(0, presence - pull * 2)); });

    const media = medias[index];
    if (!media) return;
    const q = sp.value;
    const shrink = 1 - pull * 0.2;
    let tx = 0, ty = 0, sc = 1;
    if (origin) {
      tx = origin.dx * (1 - q);
      ty = origin.dy * (1 - q);
      sc = origin.s + (1 - origin.s) * q;
    } else {
      sc = 0.9 + 0.1 * q;
    }
    media.style.transform = `translate3d(${tx}px, ${ty}px, 0) scale(${sc * shrink})`;
    media.style.opacity = String(clamp(q * 1.6, 0, 1));
  }

  // Смещение и масштаб от центра экрана к плитке — чтобы кадр вырастал из неё и возвращался в неё
  function computeOrigin(i) {
    const tile = items[i] && items[i].el;
    const media = medias[i];
    if (!tile || !media || !tile.offsetParent) return null;
    const r = tile.getBoundingClientRect();
    if (r.bottom < 0 || r.top > H) return null;
    return {
      dx: r.left + r.width / 2 - W / 2,
      dy: r.top + r.height / 2 - H / 2,
      s: r.width / media.offsetWidth,
    };
  }

  function setIndex(i) {
    if (i === index) return;
    const prevMedia = medias[index];
    if (prevMedia) { prevMedia.style.transform = ''; prevMedia.style.opacity = ''; }
    index = i;
    updateUI();
    render();
  }

  function updateUI() {
    counter.textContent = `${index + 1} / ${items.length}`;
    caption.textContent = items[index] ? items[index].caption : '';
    btnPrev.disabled = index === 0;
    btnNext.disabled = index === items.length - 1;
  }

  function open(list, i) {
    W = window.innerWidth;
    H = window.innerHeight;
    items = list;
    index = i;
    track.textContent = '';
    medias = items.map((it) => {
      const slide = document.createElement('div');
      slide.className = 'lightbox__slide';
      const media = document.createElement('div');
      media.className = 'lightbox__media';
      const src = it.el.dataset.src;
      if (src) {
        const img = document.createElement('img');
        img.src = src;
        img.alt = it.caption;
        img.draggable = false;
        media.append(img);
      } else {
        const ph = it.el.querySelector('.ph');
        if (ph) media.append(ph.cloneNode(true));
      }
      slide.append(media);
      track.append(slide);
      return media;
    });
    lb.classList.add('is-open');
    isOpen = true;
    document.documentElement.classList.add('is-locked');
    sx.set(-index * W);
    sy.set(0);
    origin = computeOrigin(index);
    if (!sp.isAnimating) sp.set(0);
    sp.to(1);
    updateUI();
    btnClose.focus({ preventScroll: true });
  }

  function close(velocityY = 0) {
    if (!isOpen) return;
    isOpen = false;
    origin = computeOrigin(index);
    sp.to(0);
    sy.to(0, { velocity: velocityY });
    document.documentElement.classList.remove('is-locked');
    const tile = items[index] && items[index].el;
    if (tile) tile.focus({ preventScroll: true });
  }

  function go(i) {
    i = clamp(i, 0, items.length - 1);
    setIndex(i);
    sx.to(-i * W, { damping: 1, response: 0.4 });
  }

  /* --- Открытие по плитке --- */
  groups.forEach((group) => {
    group.addEventListener('click', (e) => {
      const tile = e.target.closest('.g-item');
      if (!tile) return;
      const list = [...group.querySelectorAll('.g-item')]
        .filter((el) => !el.hidden)
        .map((el) => ({ el, caption: el.dataset.caption || '' }));
      open(list, list.findIndex((it) => it.el === tile));
    });
  });

  btnClose.addEventListener('click', () => close());
  btnPrev.addEventListener('click', () => go(index - 1));
  btnNext.addEventListener('click', () => go(index + 1));

  document.addEventListener('keydown', (e) => {
    if (!isOpen) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowRight') go(index + 1);
    else if (e.key === 'ArrowLeft') go(index - 1);
    else if (e.key === 'Tab') {
      // Фокус не выходит из лайтбокса
      const f = [btnClose, btnPrev, btnNext].filter((b) => !b.disabled && b.offsetParent);
      const pos = f.indexOf(document.activeElement);
      e.preventDefault();
      const next = e.shiftKey ? (pos <= 0 ? f.length - 1 : pos - 1) : (pos + 1) % f.length;
      if (f[next]) f[next].focus();
    }
  });

  window.addEventListener('resize', () => {
    if (!isOpen) return;
    W = window.innerWidth;
    H = window.innerHeight;
    sx.set(-index * W);
  });

  /* --- Жесты --- */
  const tx = new VelocityTracker();
  const ty = new VelocityTracker();
  let drag = null;
  const SLOP = 10; // порог, после которого решаем направление жеста

  track.addEventListener('pointerdown', (e) => {
    if (!isOpen || e.button > 0) return;
    track.setPointerCapture(e.pointerId);
    // Берём текущее экранное положение — так перехват на лету идёт без скачка
    drag = { id: e.pointerId, x0: e.clientX, y0: e.clientY, bx: sx.value, by: sy.value, axis: null, downOnMedia: !!e.target.closest('.lightbox__media') };
    sx.stop();
    sy.stop();
    tx.reset(); ty.reset();
    tx.push(e.clientX); ty.push(e.clientY);
  });

  track.addEventListener('pointermove', (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    tx.push(e.clientX);
    ty.push(e.clientY);
    let dx = e.clientX - drag.x0;
    let dy = e.clientY - drag.y0;
    if (!drag.axis) {
      if (Math.hypot(dx, dy) < SLOP) return;
      drag.axis = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
      // Вычитаем только сам порог — без скачка и без потери пройденного пути
      if (drag.axis === 'x') drag.x0 += Math.sign(dx) * SLOP;
      else drag.y0 += Math.sign(dy) * SLOP;
      dx = e.clientX - drag.x0;
      dy = e.clientY - drag.y0;
    }
    if (drag.axis === 'x') {
      let x = drag.bx + dx;
      const min = -(items.length - 1) * W;
      if (x > 0) x = rubberband(x, W);
      else if (x < min) x = min - rubberband(min - x, W);
      sx.set(x);
      setIndex(clamp(Math.round(-x / W), 0, items.length - 1));
    } else {
      let y = drag.by + dy;
      if (y < 0) y = -rubberband(-y, H);
      sy.set(y);
    }
  });

  const end = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag;
    drag = null;
    if (d.axis === 'x') {
      const v = tx.velocity();
      // Куда докатится лента, если отпустить с этой скоростью, — к ближайшему от этой точки кадру
      const landing = sx.value + project(v);
      const from = clamp(Math.round(-d.bx / W), 0, items.length - 1);
      const i = clamp(clamp(Math.round(-landing / W), from - 1, from + 1), 0, items.length - 1);
      const flick = Math.abs(v) > 400;
      setIndex(i);
      sx.to(-i * W, { velocity: v, damping: flick ? 0.85 : 1, response: 0.4 });
    } else if (d.axis === 'y') {
      const v = ty.velocity();
      if (sy.value + project(v) > H * 0.22) close(v);
      else sy.to(0, { velocity: v, damping: 1, response: 0.35 });
    } else if (e.type === 'pointerup' && !d.downOnMedia) {
      close(); // тап мимо кадра
    } else {
      sx.to(-index * W);
      sy.to(0);
    }
  };
  track.addEventListener('pointerup', end);
  track.addEventListener('pointercancel', end);

  /* --- Фильтр на странице галереи --- */
  document.querySelectorAll('[data-filter-group]').forEach((chips) => {
    const grid = document.querySelector(chips.dataset.filterGroup);
    if (!grid) return;
    chips.addEventListener('click', (e) => {
      const chip = e.target.closest('[data-filter]');
      if (!chip) return;
      chips.querySelectorAll('[data-filter]').forEach((c) => {
        const on = c === chip;
        c.classList.toggle('is-active', on);
        c.setAttribute('aria-pressed', String(on));
      });
      const f = chip.dataset.filter;
      grid.querySelectorAll('.g-item').forEach((it) => {
        const show = f === 'all' || it.dataset.type === f;
        const was = !it.hidden;
        it.hidden = !show;
        it.classList.remove('is-entering');
        if (show && !was) { void it.offsetWidth; it.classList.add('is-entering'); }
      });
    });
  });
})();
