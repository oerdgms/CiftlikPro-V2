/* Compact daily entry; original field names and the Enterprise save route. */
(() => {
  'use strict';
  const start = () => {
    const form = document.querySelector('[data-milk-entry-form]');
    if (!form || form.dataset.milkReady) return;
    form.dataset.milkReady = '1';
    const rows = [...form.querySelectorAll('[data-milk-animal]')];
    const save = form.querySelector('[data-milk-save]');
    const total = form.querySelector('[data-milk-list-total]');
    const status = form.querySelector('[data-milk-save-status]');
    const search = document.querySelector('[data-milk-search]');
    const filter = document.querySelector('.cp-milk-filter');
    const counter = document.querySelector('[data-milk-visible-count]');
    const empty = form.querySelector('[data-milk-empty]');
    const format = new Intl.NumberFormat('tr-TR', {minimumFractionDigits:1,maximumFractionDigits:1});
    const liters = value => format.format(value) + ' L';
    const signature = value => value.trim() === '' ? '' : String(Number(value));
    const fields = row => [...row.querySelectorAll('input.milk-entry')];
    const changed = row => fields(row).some(input => signature(input.value) !== signature(input.defaultValue));
    let dirty = [], submitting = false, leaving = false;
    function update() {
      dirty = rows.filter(changed);
      let sum = 0;
      rows.forEach(row => {
        const edited = dirty.includes(row);
        const value = edited ? fields(row).reduce((n, input) => n + Math.max(0, Number(input.value) || 0), 0) : Number(row.dataset.milkSavedTotal);
        sum += value;
        row.classList.toggle('cp-milk-dirty', edited);
        row.querySelector('[data-milk-row-total]').textContent = liters(value);
        row.querySelector('[data-milk-total-label]').textContent = edited ? 'Giriş toplamı' : 'Günlük toplam';
        row.querySelector('[data-milk-unsaved]').hidden = !edited;
      });
      total.textContent = liters(sum);
      status.textContent = dirty.length ? dirty.length + ' hayvanda kaydedilmemiş giriş' : rows.length + ' hayvanlık liste · Değişiklik yok';
      save.disabled = submitting || !dirty.length;
      save.textContent = submitting ? 'Kaydediliyor…' : dirty.length ? dirty.length + ' Hayvanı Kaydet' : 'Sütleri Kaydet';
    }
    function find() {
      let count = 0;
      rows.forEach(row => {
        row.hidden = !CPTextSearch.matches(row.dataset.search, search.value);
        if (!row.hidden) count++;
      });
      counter.textContent = count + ' hayvan';
      empty.hidden = count > 0;
    }
    form.addEventListener('input', event => { if (event.target.matches('.milk-entry')) update(); });
    form.addEventListener('keydown', event => {
      if (event.key !== 'Enter' || !event.target.matches('.milk-entry')) return;
      event.preventDefault();
      const visible = rows.filter(row => !row.hidden).flatMap(fields);
      const index = visible.indexOf(event.target);
      const next = visible[index + 1];
      if (next) { next.focus();next.select(); }
      else if (!save.disabled) save.focus();
    });
    search.addEventListener('input', find);
    search.addEventListener('keydown', event => { if (event.key === 'Enter') event.preventDefault(); });
    filter.addEventListener('submit', event => {
      if (dirty.length && !confirm('Kaydedilmemiş süt girişleri var. Kaydetmeden listeyi değiştirmek istiyor musun?')) {
        event.preventDefault();return;
      }
      leaving = true;
    });
    form.addEventListener('submit', event => {
      update();
      if (submitting || !dirty.length) { event.preventDefault();return; }
      // Omitted animals are skipped by the existing handler. Preserve their
      // unchanged records, including any quality data and notes.
      for (const row of rows) {
        const inputs = fields(row);
        if (!dirty.includes(row)) inputs.forEach(input => { input.disabled = true; });
        else if (inputs.every(input => input.value.trim() === '') && row.dataset.milkHasEntry === '1') {
          inputs.forEach(input => { input.value = '0'; });
        }
      }
      submitting = true;
      form.dataset.milkSubmitted = '1';
      update();
    });
    window.addEventListener('beforeunload', event => {
      if (dirty.length && !submitting && !leaving) { event.preventDefault();event.returnValue = ''; }
    });
    window.addEventListener('pageshow', event => {
      if (event.persisted && form.dataset.milkSubmitted) { location.reload();return; }
      submitting = false;leaving = false;
      rows.flatMap(fields).forEach(input => { input.disabled = false; });
      update();
    });
    find();update();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
