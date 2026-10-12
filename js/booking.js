/* Запись на диагностику: «оставьте заявку — мы перезвоним». */
(function () {
  'use strict';

  const { initForm } = window.Wagner;
  const card = document.querySelector('[data-booking]');
  if (!card) return;
  const form = card.querySelector('form');
  const submit = form.querySelector('[type="submit"]');

  /*
   * TODO: отправка заявки. Сейчас это заглушка — данные никуда не уходят.
   * Сюда подключается серверная функция (хранение в РФ), а из неё — CRM (amoCRM / Битрикс24 и т.п.).
   * Это единственная точка, через которую заявка покидает сайт.
   * Проверки в браузере (ловушка, маска телефона, maxlength) — только удобство:
   * сервер обязан заново проверить все поля, длины и частоту заявок (rate limit) сам.
   */
  async function sendLead(data) {
    void data;
    return new Promise((resolve) => setTimeout(resolve, 700));
  }

  // «Диагностика» / «Ремонт»: список под переключателем меняется, выбор по умолчанию — первый пункт
  const service = form.querySelector('#b-service');
  const serviceLabel = form.querySelector('[data-service-label]');
  const LISTS = {
    'Диагностика': { label: 'Какая диагностика', items: JSON.parse(service.dataset.diag) },
    'Ремонт': { label: 'Какой ремонт', items: JSON.parse(service.dataset.repair) },
  };
  function fillService(kind) {
    const list = LISTS[kind];
    if (!list) return;
    serviceLabel.textContent = list.label;
    service.textContent = '';
    list.items.forEach((t) => {
      const o = document.createElement('option');
      o.textContent = t;
      service.append(o);
    });
  }
  form.querySelectorAll('input[name="kind"]').forEach((r) => {
    r.addEventListener('change', () => { if (r.checked) fillService(r.value); });
  });
  const checkedKind = form.querySelector('input[name="kind"]:checked');
  if (checkedKind) fillService(checkedKind.value);

  initForm(form, async (data, { bot }) => {
    if (bot) { card.classList.add('is-done'); return; } // бот видит «успех», заявка никуда не уходит
    submit.disabled = true;
    submit.classList.add('is-loading');
    try {
      await sendLead(Object.fromEntries(data));
      card.classList.add('is-done');
      const title = card.querySelector('.success [tabindex]');
      if (title) title.focus();
    } finally {
      submit.disabled = false;
      submit.classList.remove('is-loading');
    }
  });

  card.querySelector('[data-booking-again]')?.addEventListener('click', () => {
    form.reset();
    fillService('Диагностика');
    card.classList.remove('is-done');
  });
})();
