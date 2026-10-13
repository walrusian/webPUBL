/* Запись: «оставьте заявку — мы перезвоним». */
(function () {
  'use strict';

  const { initForm, toast } = window.Wagner;
  const card = document.querySelector('[data-booking]');
  if (!card) return;
  const form = card.querySelector('form');
  const submit = form.querySelector('[type="submit"]');

  /*
   * Отправка заявки — единственная точка, через которую данные покидают сайт.
   * Адрес обработчика берётся из <meta name="lead-api"> (server/api/lead.php на хостинге).
   * Если адреса нет (демо на GitHub Pages) — заявка никуда не уходит, показываем «успех».
   * Проверки в браузере — только удобство: сервер заново проверяет поля, ловушку и частоту заявок.
   */
  const LEAD_API = document.querySelector('meta[name="lead-api"]')?.content || '';
  const openedAt = Date.now();

  async function sendLead(fields) {
    if (!LEAD_API) return new Promise((resolve) => setTimeout(resolve, 700));
    const payload = {
      name: fields.name || '',
      phone: fields.phone || '',
      car: fields.car || '',
      kind: fields.kind || '',
      comment: fields.comment || '',
      consent: fields.consent === 'on',
      elapsed: Date.now() - openedAt,
    };
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 15000);
    try {
      const res = await fetch(LEAD_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'same-origin',
        signal: ctrl.signal,
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok || !body.ok) throw new Error(body.error || `http_${res.status}`);
    } finally {
      clearTimeout(timer);
    }
  }

  const PHONE_HINT = document.querySelector('.tel')?.textContent || '';

  initForm(form, async (data, { bot }) => {
    if (bot) { card.classList.add('is-done'); return; } // бот видит «успех», заявка никуда не уходит
    submit.disabled = true;
    submit.classList.add('is-loading');
    try {
      await sendLead(Object.fromEntries(data));
      card.classList.add('is-done');
      const title = card.querySelector('.success [tabindex]');
      if (title) title.focus();
    } catch (e) {
      const limited = e && e.message === 'rate_limit';
      toast(limited
        ? 'Слишком много заявок подряд. Позвоните нам' + (PHONE_HINT ? `: ${PHONE_HINT}` : '')
        : 'Не удалось отправить заявку. Попробуйте ещё раз или позвоните' + (PHONE_HINT ? `: ${PHONE_HINT}` : ''),
      { duration: 8000 });
    } finally {
      submit.disabled = false;
      submit.classList.remove('is-loading');
    }
  });

  card.querySelector('[data-booking-again]')?.addEventListener('click', () => {
    form.reset();
    card.classList.remove('is-done');
  });
})();
