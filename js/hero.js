/*
 * Сцены со «сканированием» (главная): линия проходит по эскизу и проявляет оранжевые штрихи,
 * по пути загораются узлы. Каждая сцена проигрывается один раз.
 * data-x0 / data-x1 — откуда и докуда идёт линия (единицы viewBox);
 * data-start="view" — запускать, когда сцена появилась на экране (иначе — сразу при загрузке).
 */
(function () {
  'use strict';

  const DURATION = 2600;  // мс
  const DELAY = 450;
  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

  function setup(scan) {
    const clipRect = scan.querySelector('clipPath rect');
    const line = scan.querySelector('.scan__line');
    const width = scan.querySelector('svg').viewBox.baseVal.width;
    const x0 = Number(scan.dataset.x0) || 0;
    const x1 = Number(scan.dataset.x1) || width;
    const points = [...scan.querySelectorAll('.scan__point')].map((el) => ({ el, x: Number(el.dataset.x) }));

    const finish = () => {
      clipRect.setAttribute('width', String(width));
      points.forEach((p) => p.el.classList.add('is-on'));
      scan.classList.add('is-done');
    };
    if (window.Fluid.reduceMotion.matches) { finish(); return; }

    let start = 0;
    function frame(now) {
      if (!start) start = now;
      const t = Math.min((now - start) / DURATION, 1);
      const x = x0 + (x1 - x0) * ease(t);
      clipRect.setAttribute('width', x.toFixed(1));
      line.setAttribute('transform', `translate(${x.toFixed(1)} 0)`);
      points.forEach((p) => { if (x >= p.x) p.el.classList.add('is-on'); });
      if (t < 1) requestAnimationFrame(frame);
      else scan.classList.add('is-done');
    }
    const run = () => setTimeout(() => requestAnimationFrame(frame), DELAY);

    if (scan.dataset.start === 'view' && 'IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        if (entries.some((e) => e.isIntersecting)) { io.disconnect(); run(); }
      }, { threshold: 0.45 });
      io.observe(scan);
    } else {
      run();
    }
  }

  document.querySelectorAll('.scan').forEach(setup);
})();
