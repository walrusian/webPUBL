/*
 * Физика движения в духе Apple (WWDC «Designing Fluid Interfaces»), без библиотек.
 * Spring — пружина в «дизайнерских» параметрах: damping (1 — без отскока, <1 — с отскоком)
 * и response (секунды, насколько быстро доходит до цели; это не длительность).
 * Пружину можно перехватить в любой момент: новая цель подхватывает текущие значение и скорость.
 */
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const STEP = 1 / 240; // шаг интегрирования, с

  class Spring {
    constructor(value = 0, opts = {}) {
      this.value = value;
      this.target = value;
      this.velocity = 0;
      this.damping = opts.damping ?? 1;
      this.response = opts.response ?? 0.4;
      this.precision = opts.precision ?? 0.01;
      this.onUpdate = opts.onUpdate || (() => {});
      this.onRest = opts.onRest || null;
      this.raf = 0;
      this.last = 0;
      this.tick = this.tick.bind(this);
    }

    get isAnimating() { return this.raf !== 0; }

    /* Новая цель. velocity — начальная скорость (ед/с), например скорость пальца при отпускании */
    to(target, opts = {}) {
      this.target = target;
      if (opts.velocity != null) this.velocity = opts.velocity;
      if (opts.damping != null) this.damping = opts.damping;
      if (opts.response != null) this.response = opts.response;
      if (reduceMotion.matches) {
        this.set(target);
        if (this.onRest) this.onRest(target);
        return this;
      }
      if (!this.raf) {
        this.last = performance.now();
        this.raf = requestAnimationFrame(this.tick);
      }
      return this;
    }

    /* Мгновенно поставить значение (например, 1:1 за пальцем) */
    set(value) {
      this.stop();
      this.value = value;
      this.target = value;
      this.velocity = 0;
      this.onUpdate(value);
      return this;
    }

    stop() {
      if (this.raf) cancelAnimationFrame(this.raf);
      this.raf = 0;
      return this;
    }

    tick(now) {
      const dt = Math.min((now - this.last) / 1000, 1 / 20);
      this.last = now;
      const k = Math.pow((2 * Math.PI) / this.response, 2);     // жёсткость
      const c = (4 * Math.PI * this.damping) / this.response;   // вязкость
      const steps = Math.max(1, Math.ceil(dt / STEP));
      const h = dt / steps;
      for (let i = 0; i < steps; i++) {
        const force = -k * (this.value - this.target) - c * this.velocity;
        this.velocity += force * h;
        this.value += this.velocity * h;
      }
      const resting = Math.abs(this.value - this.target) < this.precision &&
                      Math.abs(this.velocity) < this.precision * 10;
      if (resting) {
        this.value = this.target;
        this.velocity = 0;
        this.raf = 0;
        this.onUpdate(this.value);
        if (this.onRest) this.onRest(this.value);
        return;
      }
      this.onUpdate(this.value);
      this.raf = requestAnimationFrame(this.tick);
    }
  }

  /* Скорость по короткой истории движений указателя (последние ~100 мс), ед/с */
  class VelocityTracker {
    constructor() { this.samples = []; }
    reset() { this.samples.length = 0; }
    push(value, time = performance.now()) {
      this.samples.push({ value, time });
      while (this.samples.length > 2 && time - this.samples[0].time > 100) this.samples.shift();
    }
    velocity() {
      const s = this.samples;
      if (s.length < 2) return 0;
      const first = s[0];
      const last = s[s.length - 1];
      if (performance.now() - last.time > 80) return 0; // палец остановился перед отпусканием
      const dt = (last.time - first.time) / 1000;
      return dt > 0 ? (last.value - first.value) / dt : 0;
    }
  }

  /* Куда «докатится» элемент по инерции (функция из примеров Apple) */
  function project(velocity, decelerationRate = 0.998) {
    return ((velocity / 1000) * decelerationRate) / (1 - decelerationRate);
  }

  /* Резиновый край: чем дальше за границу, тем сильнее сопротивление */
  function rubberband(overshoot, dimension, constant = 0.55) {
    return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
  }

  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));

  window.Fluid = { Spring, VelocityTracker, project, rubberband, clamp, reduceMotion };
})();
