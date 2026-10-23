/* Manual dairy status works on desktop and mobile. No inferred selection. */
(() => {
  'use strict';
  function start() {
    const form = document.querySelector('[data-dairy-form]');
    if (!form) return;
    const rows = [...form.querySelectorAll('[data-dairy-search]')];
    const status = form.elements.status;
    const save = form.querySelector('[type=submit]');
    function update() {
      const count = rows.filter(r => r.querySelector('input').checked).length;
      const counter = form.querySelector('[data-dairy-count]');
      if (counter) counter.textContent = `${count} hayvan seçili`;
      save.disabled = count === 0;
      save.textContent = count ? `${count} hayvan için kaydet` : 'Hayvan seç';
      const fields = form.querySelector('[data-dairy-lactation-fields]');
      fields.hidden = status.value !== 'lactating';
      fields.querySelectorAll('input').forEach(input => { input.disabled = fields.hidden; });
      const msg = form.querySelector('[data-dairy-message]');
      msg.textContent = status.value === 'dry' ? 'Seçili hayvanlar durum tarihinde kuruya çıkarılır.' : 'Seçili hayvanların laktasyon ve kuru durumu bu seçime göre güncellenir.';
    }
    form.addEventListener('change', update);
    form.querySelector('[data-dairy-search-input]')?.addEventListener('input', e => {
      const words = CPTextSearch.normalize(e.target.value).split(/\s+/);
      rows.forEach(row => { row.hidden = !words.every(word => CPTextSearch.normalize(row.dataset.dairySearch).includes(word)); });
      form.querySelector('.cp-dairy-no-results').hidden = rows.some(row => !row.hidden);
    });
    form.querySelector('[data-dairy-select]')?.addEventListener('click', () => { rows.filter(r => !r.hidden).forEach(r => { r.querySelector('input').checked = true; }); update(); });
    form.querySelector('[data-dairy-clear]')?.addEventListener('click', () => { rows.forEach(r => { r.querySelector('input').checked = false; }); update(); });
    form.addEventListener('submit', e => {
      if (save.disabled) { e.preventDefault(); return; }
      // Prevent duplicate taps while the normal Enterprise redirect completes.
      save.disabled = true;
      save.textContent = 'Kaydediliyor…';
    });
    addEventListener('pageshow', update);
    update();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
