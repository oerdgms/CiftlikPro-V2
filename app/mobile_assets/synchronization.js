(function () {
  'use strict';
  const editor = document.getElementById('syncEditor');
  const closeEditor = () => { if (editor?.open) editor.close(); };
  document.querySelectorAll('[data-sync-open]').forEach(button => button.addEventListener('click', () => editor?.showModal()));
  document.querySelectorAll('[data-sync-close]').forEach(button => button.addEventListener('click', closeEditor));
  if (editor) {
    editor.addEventListener('click', event => { if (event.target === editor) { const box = editor.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closeEditor(); } });
    if (editor.hasAttribute('data-open')) editor.showModal();
  }
  document.querySelectorAll('[data-sync-confirm]').forEach(form => form.addEventListener('submit', event => { if (!window.confirm(form.dataset.syncConfirm)) event.preventDefault(); }));
  document.querySelectorAll('form.sync-action-form').forEach(form => form.addEventListener('submit', event => {
    if (event.defaultPrevented) return;
    const button = form.querySelector('button[type=submit],button:not([type])');
    if (button) { button.disabled = true; button.textContent = 'Kaydediliyor…'; }
  }));
  if (location.hash.startsWith('#sync-step-')) {
    const item = document.getElementById(location.hash.slice(1));
    if (item) {
      const animal = item.closest('details'); if (animal) animal.open = true;
      item.classList.add('sync-focused');
      requestAnimationFrame(() => item.scrollIntoView({ block: 'center' }));
    }
  }
  if (!editor) return;
  const form = document.getElementById('syncPlanForm');
  const config = JSON.parse(document.getElementById('syncEditorData').textContent);
  const protocol = document.getElementById('syncProtocol');
  const start = document.getElementById('syncStart');
  const group = document.getElementById('syncGroup');
  const area = document.getElementById('syncStepEditor');
  const error = document.getElementById('syncFormError');
  const animalRows = [...editor.querySelectorAll('.sync-animal-row')];
  const countLabel = document.getElementById('syncSelectedCount');
  const search = document.getElementById('syncAnimalSearch');
  let steps = structuredClone(config.steps);
  let dirtySteps = false;
  const normalize = value =>CPTextSearch.normalize(value);
  const wallTime = value => Date.parse(value + 'Z');
  const pad = value => String(value).padStart(2, '0');
  function displayWall(ms) {
    if (!Number.isFinite(ms)) return 'Başlangıç tarih ve saatini seçin';
    const d = new Date(ms);
    return pad(d.getUTCDate()) + '/' + pad(d.getUTCMonth() + 1) + '/' + d.getUTCFullYear() + ' ' + pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes());
  }
  function node(tag, props = {}, text = '') {
    const el = document.createElement(tag);
    Object.entries(props).forEach(([key, value]) => { if (key === 'className') el.className = value; else el.setAttribute(key, value); });
    if (text) el.textContent = text;
    return el;
  }
  function control(label, key, value, attrs = {}, options = null) {
    const wrap = node('label', {}, label);
    const input = node(options ? 'select' : 'input', { 'data-sync-field': key, ...attrs });
    if (options) Object.entries(options).forEach(([val, text]) => input.append(node('option', { value: val }, text)));
    input.value = value ?? '';
    wrap.append(input);
    return wrap;
  }
  function storeSteps() {
    steps = [...area.querySelectorAll('.sync-edit-step')].map(row => {
      const value = key => row.querySelector('[data-sync-field="' + key + '"]').value;
      const minutes = Number(value('days')) * 1440 + Number(value('hours')) * 60;
      return { name: value('name'), kind: value('kind'), hormone: value('hormone'), offset_minutes: Math.round(minutes),
        product: value('product'), dose: value('dose'), unit: value('unit'), route: value('route') };
    });
  }
  function datePreviews() {
    const base = wallTime(start.value);
    area.querySelectorAll('.sync-edit-step').forEach(row => {
      const days = Number(row.querySelector('[data-sync-field=days]').value);
      const hours = Number(row.querySelector('[data-sync-field=hours]').value);
      row.querySelector('.sync-date-preview').textContent = displayWall(base + (days * 1440 + hours * 60) * 60000);
    });
  }
  function renderSteps() {
    area.replaceChildren();
    steps.forEach((s, index) => {
      const row = node('section', { className: 'sync-edit-step' });
      const heading = node('div', { className: 'sync-edit-step-head' });
      heading.append(node('b', {}, (index + 1) + '. Uygulama'));
      const remove = node('button', { type: 'button', className: 'sync-remove', 'aria-label': (index + 1) + '. uygulamayı kaldır' }, 'Kaldır');
      remove.addEventListener('click', () => { storeSteps(); steps.splice(index, 1); dirtySteps = true; renderSteps(); });
      heading.append(remove); row.append(heading);
      const fields = node('div', { className: 'sync-fields' });
      fields.append(control('Adım adı *', 'name', s.name, { required: '', maxlength: '120' }));
      fields.append(control('İşlem türü', 'kind', s.kind, {}, { medicine: 'Hormon / ilaç', device: 'CIDR / cihaz', insemination: 'Tohumlama', check: 'Kontrol' }));
      fields.append(control('Başlangıçtan kaç gün sonra?', 'days', Math.floor(s.offset_minutes / 1440), { type: 'number', min: '0', max: '366', step: '1', required: '', inputmode: 'numeric' }));
      fields.append(control('Ek saat', 'hours', (s.offset_minutes % 1440) / 60, { type: 'number', min: '0', max: '23.98333333333333', step: 'any', required: '', inputmode: 'decimal' }));
      fields.append(control('Hormon / etken grubu', 'hormone', s.hormone, { maxlength: '100', placeholder: 'Veteriner planından' }));
      fields.append(control('Ürün', 'product', s.product, { maxlength: '150', placeholder: 'Veteriner planından' }));
      fields.append(control('Doz', 'dose', s.dose, { maxlength: '30', inputmode: 'decimal', placeholder: 'Dozu girin' }));
      fields.append(control('Birim', 'unit', s.unit, { maxlength: '30', placeholder: 'ml, mg, µg, adet…' }));
      fields.append(control('Uygulama yolu', 'route', s.route, { maxlength: '80', placeholder: 'Veteriner planından' }));
      row.append(fields, node('div', { className: 'sync-date-preview' }));
      row.addEventListener('input', () => { dirtySteps = true; datePreviews(); });
      area.append(row);
    });
    datePreviews();
  }
  function selectedCount() {
    const count = editor.querySelectorAll('input[name=animal_id]:checked:not(:disabled)').length;
    countLabel.textContent = count + ' seçili';
    const fees = Number(form.elements.vet_fee.value || 0) + Number(form.elements.hormone_fee.value || 0);
    const money = new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' });
    document.getElementById('syncCostPreview').textContent = count + ' hayvan × ' + money.format(fees) + ' = ' + money.format(count * fees) + '. Planı kaydetmek gider oluşturmaz; plan ayrıntısından finansa işleyebilirsiniz.';
  }
  function filterAnimals() {
    const term = normalize(search.value);
    const audience = config.protocols[protocol.value]?.audience || 'all';
    animalRows.forEach(row => {
      const groups = row.dataset.syncGroup.split(' ');
      const compatible = audience === 'all' || (audience === 'heifer' ? groups.includes('heifer') : !groups.includes('heifer'));
      row.hidden = !(compatible && (group.value === 'all' || groups.includes(group.value)) && (!term || normalize(row.dataset.syncSearch).includes(term)));
    });
  }
  group.addEventListener('change', () => {
    animalRows.forEach(row => { if (group.value !== 'all' && !row.dataset.syncGroup.split(' ').includes(group.value)) row.querySelector('input').checked = false; });
    filterAnimals(); selectedCount();
  });
  search.addEventListener('input', filterAnimals);
  animalRows.forEach(row => row.querySelector('input').addEventListener('change', selectedCount));
  document.getElementById('syncSelectVisible').addEventListener('click', () => { animalRows.filter(row => !row.hidden).forEach(row => { const box = row.querySelector('input'); if (!box.disabled) box.checked = true; }); selectedCount(); });
  document.getElementById('syncClearSelection').addEventListener('click', () => { animalRows.forEach(row => row.querySelector('input').checked = false); selectedCount(); });
  for (const key of ['vet_fee', 'hormone_fee']) form.elements[key].addEventListener('input', selectedCount);
  start.addEventListener('input', datePreviews);
  let previousProtocol = protocol.value;
  protocol.addEventListener('change', () => {
    if (dirtySteps && !confirm('Takvim değişince düzenlediğiniz adımlar ve doz alanları sıfırlanır. Devam edilsin mi?')) { protocol.value = previousProtocol; return; }
    previousProtocol = protocol.value;
    const template = config.protocols[protocol.value];
    steps = template ? structuredClone(template.steps) : [];
    dirtySteps = false;
    const note = document.getElementById('syncTemplateNote');
    note.replaceChildren(document.createTextNode(template ? 'Gün / saat aralıkları düzenlenebilir. İlaç ve dozları veteriner planından girin. ' : 'Takvim seçerek başlayın.'));
    if (template?.source) note.append(node('a', { href: template.source, target: '_blank', rel: 'noopener' }, 'Takvim kaynağı: DCRC'));
    if (template?.audience === 'heifer') { group.value = 'heifer'; group.dispatchEvent(new Event('change')); }
    else if (template?.audience === 'cow' && group.value === 'heifer') { group.value = 'all'; group.dispatchEvent(new Event('change')); }
    animalRows.forEach(row => {
      if ((template?.audience === 'cow' && row.dataset.syncGroup.includes('heifer')) ||
          (template?.audience === 'heifer' && !row.dataset.syncGroup.includes('heifer'))) row.querySelector('input').checked = false;
    });
    filterAnimals(); selectedCount();
    renderSteps();
  });
  document.getElementById('syncAddStep').addEventListener('click', () => {
    storeSteps();
    if (steps.length >= 30) { error.textContent = 'En çok 30 adım tanımlayabilirsiniz.'; error.hidden = false; return; }
    steps.push({ offset_minutes: steps.at(-1)?.offset_minutes || 0, name: '', kind: 'medicine', hormone: '', product: '', dose: '', unit: '', route: '' });
    dirtySteps = true; renderSteps();
  });
  form.addEventListener('submit', event => {
    storeSteps(); error.hidden = true;
    let message = '';
    if (!editor.querySelector('input[name=animal_id]:checked:not(:disabled)')) message = 'En az bir uygun hayvan seçin.';
    else if (!steps.length) message = 'En az bir uygulama adımı ekleyin.';
    else if (steps.some((s, i) => !Number.isInteger(s.offset_minutes) || s.offset_minutes < 0 || s.offset_minutes > 527040 || (i && s.offset_minutes < steps[i - 1].offset_minutes))) message = 'Adımları başlangıçtan itibaren artan gün / saat sırasıyla girin.';
    if (message) { event.preventDefault(); error.textContent = message; error.hidden = false; error.scrollIntoView({ block: 'center' }); return; }
    document.getElementById('syncStepsJson').value = JSON.stringify(steps);
    const button = document.getElementById('syncSave'); button.disabled = true; button.textContent = 'Kaydediliyor…';
  });
  renderSteps(); filterAnimals(); selectedCount();
})();
