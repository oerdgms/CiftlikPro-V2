(() => {
  'use strict';
  const workspace = document.getElementById('healthCenter');
  if (!workspace) return;
  const all = (selector, root = document) => [...root.querySelectorAll(selector)];
  const open = id => { const target = document.getElementById(id); if (target && !target.open) target.showModal(); };
  const close = dialog => { if (dialog?.open) dialog.close(); };
  all('[data-hc-open]').forEach(button => button.addEventListener('click', () => open(button.dataset.hcOpen)));
  all('.hc-dialog').forEach(dialog => {
    all('[data-hc-close]', dialog).forEach(button => button.addEventListener('click', () => close(dialog)));
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) close(dialog);
    });
  });
  const program = document.getElementById('hcProgram');
  const category = document.getElementById('hcProgramCategory');
  const product = document.getElementById('hcProduct');
  const definitions = JSON.parse(document.getElementById('hcDefinitionsData').textContent);
  function refreshDefinitions() {
    const list = document.getElementById('hcDefinitions');
    list.replaceChildren(...(definitions[category.value] || []).map(name => {
      const option = document.createElement('option'); option.value = name; return option;
    }));
  }
  const fixedControls = new Set(all('input:disabled,select:disabled',program));
  const scheduleMode = program.querySelector('[data-hc-schedule-mode]');
  function refreshSchedule() {
    const treatment = category.value === 'treatment';
    program.querySelector('[data-hc-treatment-options]').hidden = !treatment;
    const course = treatment && scheduleMode.value === 'course';
    program.querySelector('[data-hc-course]').hidden = !course;
    program.querySelector('[data-hc-repeat-fields]').hidden = course;
    program.querySelector('[data-hc-rapel-group]').hidden = course;
    for (const [selector,disabled] of [['[data-hc-schedule-mode]',!treatment],['[data-hc-course] input',!course],['[data-hc-repeat-fields] input,[data-hc-repeat-fields] select',course],['[data-hc-rapel-group] input,[data-hc-rapel-group] select',course]]) {
      all(selector,program).forEach(control => { control.disabled = fixedControls.has(control) || disabled; });
    }
    const rapelInput=program.querySelector('[data-hc-rapel-days] input');
    rapelInput.required=!course && program.querySelector('[data-hc-rapel]').value==='yes' && !rapelInput.disabled;
  }
  refreshDefinitions(); refreshSchedule();
  category.addEventListener('change', () => {refreshDefinitions();refreshSchedule();});
  scheduleMode.addEventListener('change',refreshSchedule);
  all('[data-hc-program-category]').forEach(button => button.addEventListener('click', () => {
    category.value = button.dataset.hcProgramCategory; refreshDefinitions(); refreshSchedule(); open('hcProgram');
  }));
  all('[data-hc-choice]').forEach(button => button.addEventListener('click', () => {
    close(document.getElementById('hcChooser'));
    const choice = button.dataset.hcChoice;
    if (choice === 'sync') {
      const editor = document.getElementById('syncEditor');
      if (editor) { editor.showModal(); return; }
      location.href = '/health?category=sync&new=1'; return;
    }
    if (choice === 'treatment') { open('hcCase'); return; }
    if (!category.disabled) category.value = choice;
    refreshDefinitions(); refreshSchedule(); open('hcProgram');
  }));
  all('[data-hc-rapel]').forEach(select => {
    const update = () => {
      const label = select.closest('.hc-form-grid').querySelector('[data-hc-rapel-days]');
      const input = label.querySelector('input');
      label.hidden = select.value !== 'yes'; input.required = select.value === 'yes' && !input.disabled && !program.querySelector('[data-hc-rapel-group]').hidden;
    };
    select.addEventListener('change', update); update();
  });
  const normalize = value =>CPTextSearch.normalize(value);
  all('[data-hc-picker]').forEach(picker => {
    const checks = all('input[type=checkbox]', picker);
    const rows = all('.hc-animal-option', picker);
    const selected = picker.querySelector('[data-hc-selected]');
    const stored = picker.querySelector('[name=subjects_json]');
    const search = picker.querySelector('[data-hc-animal-search]');
    const paddock = picker.querySelector('[data-hc-paddock]');
    const gender = picker.querySelector('[data-hc-gender]');
    const saved = new Set(JSON.parse(stored.value || '[]'));
    function sync() {
      checks.forEach(input => { if (input.checked) saved.add(input.value); else saved.delete(input.value); });
      stored.value = JSON.stringify([...saved]); selected.textContent = saved.size + ' seçili';
      picker.closest('form').querySelector('.hc-form-error').hidden = true;
    }
    const filter = () => {
      const term = normalize(search.value); let visible = 0;
      rows.forEach(row => {
        const show = (!term || CPTextSearch.matches(row.dataset.search,term)) && (!paddock.value || row.dataset.paddock === paddock.value) && (!gender.value || row.dataset.gender === gender.value);
        row.hidden = !show; if (show) visible++;
      });
      picker.querySelector('[data-hc-picker-empty]').hidden = visible !== 0;
    };
    checks.forEach(input => input.addEventListener('change', sync));
    search.addEventListener('input', filter); paddock.addEventListener('change', filter); gender.addEventListener('change', filter);
    picker.querySelector('[data-hc-select-visible]')?.addEventListener('click', () => { rows.filter(row => !row.hidden).forEach(row => { const input = row.querySelector('input'); if (!input.disabled) input.checked = true; }); sync(); });
    picker.querySelector('[data-hc-clear]')?.addEventListener('click', () => { checks.filter(input => !input.disabled).forEach(input => { input.checked = false; }); sync(); });
    picker.closest('form').addEventListener('submit', event => {
      sync();
      if (saved.size) return;
      event.preventDefault(); const error = picker.closest('form').querySelector('.hc-form-error');
      error.textContent = 'En az bir hayvan seçin.'; error.hidden = false; picker.scrollIntoView({block:'center'});
    });
    filter();
  });
  all('[data-hc-complete]').forEach(button => button.addEventListener('click', () => {
    const dialog = document.getElementById('hcComplete');
    dialog.querySelector('[name=task_id]').value = button.dataset.hcComplete;
    dialog.querySelector('.hc-complete-label').textContent = button.dataset.hcTitle + '\n' + button.dataset.hcSubject;
    open('hcComplete');
  }));
  const batchDialog = document.getElementById('hcBatchComplete');
  const batchForm = document.getElementById('hcBatchForm');
  const batchGroups = JSON.parse(document.getElementById('hcBatchData')?.textContent || '{}');
  if (batchForm) {
    const options = batchForm.querySelector('[data-hc-batch-options]');
    const search = batchForm.querySelector('[data-hc-batch-search]');
    const paddock = batchForm.querySelector('[data-hc-batch-paddock]');
    const save = batchForm.querySelector('[data-hc-batch-save]');
    const error = batchForm.querySelector('.hc-form-error');
    const money = new Intl.NumberFormat('tr-TR', {style:'currency',currency:'TRY'});
    const rows = () => all('.hc-animal-option', options);
    function updateBatch() {
      const selected = rows().filter(row => row.querySelector('input').checked);
      batchForm.querySelector('[name=task_ids]').value = JSON.stringify(selected.map(row => Number(row.querySelector('input').value)));
      batchForm.querySelector('[data-hc-batch-selected]').textContent = selected.length + ' seçili';
      const cost = selected.reduce((total,row) => total + Number(row.dataset.cost),0);
      batchForm.querySelector('[data-hc-batch-summary]').textContent = selected.length + ' hayvan · Toplam ' + money.format(cost / 100);
      save.textContent = selected.length + ' Hayvana Yapıldı Olarak Kaydet';
      save.disabled = selected.length === 0; error.hidden = true;
    }
    function filterBatch() {
      const term = normalize(search.value);
      rows().forEach(row => { row.hidden = !((!term || CPTextSearch.matches(row.dataset.search,term)) && (!paddock.value || row.dataset.paddock === paddock.value)); });
      batchForm.querySelector('[data-hc-batch-empty]').hidden = rows().some(row => !row.hidden);
    }
    all('[data-hc-batch]').forEach(button => button.addEventListener('click', () => {
      const group = batchGroups[button.dataset.hcBatch]; if (!group) return;
      batchForm.reset(); options.replaceChildren();
      batchForm.querySelector('[name=batch_ref]').value = button.dataset.hcBatch;
      batchForm.querySelector('[data-hc-batch-title]').textContent = group.title + '\n' + group.detail + ' · Planlanan ' + group.date;
      const pads = [...new Set(group.members.map(member => member.paddock))].sort((a,b) => a.localeCompare(b,'tr'));
      paddock.replaceChildren(...['',...pads].map(name => {const option=document.createElement('option');option.value=name;option.textContent=name || 'Tüm padoklar';return option;}));
      group.members.forEach(member => {
        const row=document.createElement('label');row.className='hc-animal-option';row.dataset.search=member.search;row.dataset.paddock=member.paddock;row.dataset.cost=member.cost;
        const input=document.createElement('input');input.type='checkbox';input.value=member.id;input.checked=true;input.addEventListener('change',updateBatch);
        const identity=document.createElement('span'),tag=document.createElement('b'),detail=document.createElement('small');tag.textContent=member.tag;detail.textContent=member.detail;identity.append(tag,detail);row.append(input,identity);options.append(row);
      });
      filterBatch(); updateBatch(); open(batchDialog.id);
    }));
    search.addEventListener('input',filterBatch);paddock.addEventListener('change',filterBatch);
    search.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();filterBatch();}});
    batchForm.querySelector('[data-hc-batch-all]').addEventListener('click',()=>{rows().forEach(row=>row.querySelector('input').checked=true);updateBatch();});
    batchForm.querySelector('[data-hc-batch-visible]').addEventListener('click',()=>{rows().forEach(row=>row.querySelector('input').checked=!row.hidden);updateBatch();});
    batchForm.querySelector('[data-hc-batch-clear]').addEventListener('click',()=>{rows().forEach(row=>row.querySelector('input').checked=false);updateBatch();});
    batchForm.addEventListener('submit',event=>{
      updateBatch();
      if (save.disabled) {event.preventDefault();error.textContent='En az bir hayvan seçin.';error.hidden=false;}
    });
  }
  all('[data-hc-confirm]').forEach(form => form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.hcConfirm)) event.preventDefault();
  }));
  // Confirmations and selection validation run before the submission lock.
  all('form', workspace).concat(all('.hc-dialog form')).forEach(form => form.addEventListener('submit', event => {
    if (event.defaultPrevented || form.method.toLowerCase() !== 'post') return;
    const button = form.querySelector('button[type=submit]');
    if (button) { button.disabled = true; button.dataset.hcOriginal = button.textContent; button.textContent = 'Kaydediliyor…'; }
  }));
  document.addEventListener('click', event => { all('.hc-more[open]').forEach(menu => { if (!menu.contains(event.target)) menu.open = false; }); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') all('.hc-more[open]').forEach(menu => { menu.open = false; }); });
  window.addEventListener('pageshow', () => { all('[data-hc-original]').forEach(button => { button.disabled = false; button.textContent = button.dataset.hcOriginal; }); });
  const auto = document.querySelector('.hc-dialog[data-hc-auto]');
  if (auto) open(auto.id); else if (workspace.hasAttribute('data-hc-add-auto')) open('hcChooser');
  // Keep the existing global mobile + button contextual to this hub.
  document.getElementById('cpGlobalAdd')?.addEventListener('click', event => {
    event.stopImmediatePropagation();
    const quick = document.getElementById('cpQuickOverlay'); if (quick) quick.hidden = true;
    document.body.style.overflow = ''; open('hcChooser');
  }, true);
})();
