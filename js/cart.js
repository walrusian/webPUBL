/* Корзина и оформление. Оплата — заглушка (тестовый режим), платёжный сервис ещё не выбран. */
(function () {
  'use strict';

  const { Cart, toast, initForm, createSheet, plural, money } = window.Wagner;
  const root = document.querySelector('[data-cart]');
  if (!root) return;

  const $ = (sel) => root.querySelector(sel);
  const qtyOut = $('[data-qty]');
  const btnMinus = $('[data-minus]');
  const btnPlus = $('[data-plus]');
  const btnRemove = $('[data-remove]');
  const form = $('form');
  const payBtn = $('[data-pay]');
  const sheetEl = document.querySelector('[data-pay-sheet]');
  const sheet = createSheet(sheetEl);
  const sheetAmount = sheetEl.querySelector('[data-sheet-amount]');
  const sheetConfirm = sheetEl.querySelector('[data-sheet-confirm]');
  let done = false;

  function render() {
    const q = Cart.qty;
    root.dataset.state = done ? 'done' : q ? 'filled' : 'empty';
    if (!q) return;
    const total = q * Cart.price;
    qtyOut.textContent = q;
    btnMinus.disabled = q <= 1;
    btnPlus.disabled = q >= Cart.max;
    root.querySelectorAll('[data-line-total], [data-sum-total]').forEach((el) => { el.textContent = money(total); });
    root.querySelector('[data-sum-qty]').textContent = `Диагностика × ${q}`;
    root.querySelector('[data-sum-tickets]').textContent = `${q} ${plural(q, ['билет', 'билета', 'билетов'])}`;
    payBtn.textContent = `Оплатить ${money(total)}`;
  }

  btnMinus.addEventListener('click', () => { Cart.qty = Cart.qty - 1; });
  btnPlus.addEventListener('click', () => { Cart.qty = Cart.qty + 1; });
  btnRemove.addEventListener('click', () => {
    const prev = Cart.qty;
    Cart.qty = 0;
    // Вместо диалога «вы уверены?» — возможность вернуть
    toast('Диагностика удалена из корзины', { action: { label: 'Вернуть', onClick: () => { Cart.qty = prev; } }, duration: 6000 });
  });
  document.addEventListener('cart:change', render);

  initForm(form, () => {
    sheetAmount.textContent = money(Cart.qty * Cart.price);
    sheet.show();
  });

  /*
   * TODO: настоящая оплата. Здесь серверная функция создаёт платёж у провайдера
   * (ЮKassa / Т-Банк / CloudPayments), браузер уходит на его страницу оплаты,
   * а подтверждение приходит на сервер (webhook) — только после него заказ считается оплаченным
   * и передаётся в CRM, а покупатель получает номер билета.
   */
  sheetConfirm.addEventListener('click', () => {
    sheetConfirm.classList.add('is-loading');
    setTimeout(() => {
      sheetConfirm.classList.remove('is-loading');
      sheet.hide();
      done = true;
      Cart.qty = 0;
      form.reset();
      render();
      window.scrollTo({ top: 0, behavior: window.Fluid.reduceMotion.matches ? 'auto' : 'smooth' });
    }, 900);
  });

  render();
})();
