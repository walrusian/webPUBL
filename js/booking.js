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
   */
  async function sendLead(data) {
    void data;
    return new Promise((resolve) => setTimeout(resolve, 700));
  }

  initForm(form, async (data) => {
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
    card.classList.remove('is-done');
  });
})();
