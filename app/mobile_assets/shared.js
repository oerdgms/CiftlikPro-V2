/* Same settings and actions on every screen width. */
(() => {
  'use strict';
  function start() {
    if (window.cpSharedStarted) return;
    window.cpSharedStarted = true;
    animalStates();
    const form = document.querySelector('[data-layout-form]');
    if (!form) return;
    const refresh = () => {
      form.querySelectorAll('.cp-layout-choices').forEach(list => {
        const rows = [...list.children];
        rows.forEach((row, i) => {
          row.querySelector('[data-layout-up]').disabled = i === 0;
          row.querySelector('[data-layout-down]').disabled = i === rows.length - 1;
        });
      });
    };
    form.addEventListener('click', event => {
      const button = event.target.closest('[data-layout-up],[data-layout-down]');
      if (!button) return;
      const row = button.closest('[data-layout-item]');
      if (button.hasAttribute('data-layout-up')) row.previousElementSibling?.before(row);
      else row.nextElementSibling?.after(row);
      refresh();
      button.focus();
    });
    form.addEventListener('submit', event => {
      if (event.submitter?.value === 'reset') return;
      const valid = ['sections','cards'].every(name => form.querySelector(`input[name="${name}"]:checked`));
      if (!valid) {
        event.preventDefault();
        form.querySelector('[data-layout-message]').textContent = 'En az bir bölüm ve bir sürü kartı seç.';
      }
    },true);
    refresh();
  }
  function animalStates() {
    let dialog, controller, serial = 0, previousFocus, previousOverflow, previousGutter;
    const isPlainClick = event => event.button === 0 && !event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey;
    function close() { dialog?.close(); }
    function createDialog(trigger) {
      if (dialog?.open) return;
      dialog = document.createElement('dialog');
      dialog.id = 'cpAnimalStateDialog';dialog.className = 'cp-state-dialog';
      dialog.setAttribute('aria-labelledby','cpStateTitle');
      dialog.setAttribute('aria-modal','true');
      previousFocus = trigger || document.activeElement;
      previousOverflow = document.body.style.overflow;
      previousGutter = document.documentElement.style.scrollbarGutter;
      if (innerWidth > document.documentElement.clientWidth) document.documentElement.style.scrollbarGutter = 'stable';
      document.body.style.overflow = 'hidden';
      dialog.addEventListener('close', () => {
        ++serial;controller?.abort();
        document.body.style.overflow = previousOverflow;
        document.documentElement.style.scrollbarGutter = previousGutter;
        previousFocus?.focus({preventScroll:true});
        dialog.remove();dialog = null;
      },{once:true});
      dialog.addEventListener('click', event => {
        if (event.target !== dialog) return;
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) close();
      });
      document.body.append(dialog);
    }
    async function open(url, trigger) {
      createDialog(trigger);
      const requested = ++serial;
      controller?.abort();controller = new AbortController();
      const current = dialog;
      current.innerHTML = '<div class="cp-state-loading"><h2 id="cpStateTitle">Durum Ekle</h2><p role="status">Yükleniyor…</p><button type="button" class="cp-state-cancel" data-cp-state-close>Vazgeç</button></div>';
      if (!current.open) current.showModal();
      try {
        const target = new URL(url,location.origin);target.searchParams.set('fragment','1');
        const response = await fetch(target,{signal:controller.signal,headers:{'X-Requested-With':'CiftlikPro-State'}});
        if (new URL(response.url).pathname !== '/animal-events') { location.assign(response.url);return; }
        if (!response.ok) throw new Error('Kayıt ekranı açılamadı. Hayvanın aktif olduğunu kontrol et.');
        const documentResponse = new DOMParser().parseFromString(await response.text(),'text/html');
        const content = documentResponse.querySelector('[data-cp-state-content]');
        if (!content) throw new Error('Kayıt ekranı yüklenemedi.');
        if (requested !== serial || !current.open) return;
        current.replaceChildren(content);
        const heading = current.querySelector('h2');heading.tabIndex = -1;heading.focus({preventScroll:true});
      } catch (error) {
        if (error.name === 'AbortError' || requested !== serial || !current.open) return;
        current.querySelector('[role=status]').textContent = error.message;
        const fallback = document.createElement('a');fallback.href = url;fallback.textContent = 'Kayıt ekranını aç';fallback.className = 'cp-state-save';
        current.firstElementChild.append(fallback);
      }
    }
    window.cpOpenAnimalState = open;
    document.addEventListener('click', event => {
      const cancel = event.target.closest('[data-cp-state-close]');
      if (cancel && dialog?.contains(cancel)) { event.preventDefault();close();return; }
      const link = event.target.closest('a[data-cp-state-url],a[data-cp-state-step]');
      if (!link || !isPlainClick(event)) return;
      if (link.hasAttribute('data-cp-state-step') && !dialog?.contains(link)) return;
      event.preventDefault();open(link.href,link);
    });
    document.addEventListener('submit', event => {
      if (!event.target.matches('.cp-state-form')) return;
      const form = event.target;
      if (form.dataset.cpStateSaving) { event.preventDefault();return; }
      form.dataset.cpStateSaving = '1';
      setTimeout(() => {const button = form.querySelector('[type=submit]');button.disabled = true;button.textContent = 'Kaydediliyor…';},0);
    });
    window.addEventListener('pageshow', () => document.querySelectorAll('.cp-state-form').forEach(form => {
      delete form.dataset.cpStateSaving;
      form.querySelector('[type=submit]').disabled = false;
    }));
    const params = new URLSearchParams(location.search);
    if (/^\/(animal|calf)-edit$/.test(location.pathname) && params.get('focus') === 'notes') {
      const notes = document.querySelector('form textarea[name=notes]');
      notes?.scrollIntoView({block:'center'});notes?.focus({preventScroll:true});
    }
    if (location.pathname === '/health' && params.has('subject')) {
      const [source,id] = params.get('subject').split(':');
      if (!['animal','calf'].includes(source) || !/^\d+$/.test(id)) return;
      const key = (source === 'calf' ? 'C:' : 'A:')+id;
      const scope = document.getElementById('healthScope');
      if (scope) { scope.value = 'single';scope.dispatchEvent(new Event('change',{bubbles:true})); }
      const hidden = document.getElementById('healthSubjectKey'), search = document.getElementById('healthSubjectSearch');
      if (hidden && search) {
        hidden.value = key;
        search.value = (typeof healthSubjects !== 'undefined' ? healthSubjects.find(item => item.key === key)?.label : '') || params.get('search') || '';
      }
      if (params.get('app_action') === 'add') {
        if (typeof window.toggleSectionDrawer === 'function') window.toggleSectionDrawer('healthPlanDrawer',true);
        else document.getElementById('healthForm')?.scrollIntoView({block:'start'});
      }
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
