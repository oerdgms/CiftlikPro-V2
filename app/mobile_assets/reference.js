/* Reference mobile presentation: reuse live Enterprise forms and record handlers. */
(() => {
  'use strict';
  function start() {
    if (!matchMedia('(max-width:900px)').matches) return;
    const configNode = document.getElementById('cpAppConfig');
    if (!configNode) return;
    const config = JSON.parse(configNode.textContent);
    if (config.login || !config.reference_ui) return;
    const $ = (s, root = document) => root.querySelector(s);
    const $$ = (s, root = document) => [...root.querySelectorAll(s)];
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const path = location.pathname, params = new URL(config.request_url || location.href, location.origin).searchParams;
    const main = $('main.main'), title = $('#cpScreenTitle'), subtitle = $('#cpScreenSubtitle');
    const glyph = name => config.ref_icons?.[name] || $(`.cp-bottom-nav [data-cp-nav="${name}"] svg`)?.outerHTML || $('.cp-bottom-nav svg')?.outerHTML || '';
    const icon = name => config.ref_icons?.[name] || glyph(name);
    const motion = matchMedia('(prefers-reduced-motion:reduce)').matches ? 'auto' : 'smooth';
    const isModules = path === '/modules' || (path === '/' && params.get('app_view') === 'modules');
    if (path === '/' && params.get('edit') === '1') { location.replace('/home-layout'); return; }
    const isTasks = path === '/' && params.get('app_view') === 'tasks';
    const back = $('.cp-header-back');
    if (back) back.href = /^(\/animal|\/calf)(-edit)?$/.test(path) || ['/animal-add','/dairy-status'].includes(path) ? '/all-animals' : '/';
    if (path === '/' && !isModules && !isTasks) { title.textContent = 'ÇiftlikPro'; subtitle.textContent = 'Enterprise'; }
    if (/^\/(animal|calf)$/.test(path)) title.textContent = 'Hayvan Detayı';
    if (path === '/animal-add') title.textContent = params.get('entry') === 'calf' ? 'Yeni Buzağı Ekle' : 'Yeni Hayvan Ekle';
    const menuBackdrop = $('#cpRefMenuBackdrop'), menu = $('#cpRefMenu'), menuButton = $('#cpOpenMenu');
    let focusBeforeMenu, overflowBeforeMenu;
    function setMenu(open) {
      menuButton?.setAttribute('aria-expanded', String(open));
      if (open) {
        focusBeforeMenu = document.activeElement;
        overflowBeforeMenu = document.body.style.overflow;
        menuBackdrop.hidden = false;
        document.body.style.overflow = 'hidden';
        menu.focus();
      } else {
        menuBackdrop.hidden = true;
        document.body.style.overflow = overflowBeforeMenu || '';
        focusBeforeMenu?.focus();
      }
    }
    menuButton?.addEventListener('click', () => setMenu(true));
    $('#cpCloseMenu')?.addEventListener('click', () => setMenu(false));
    menuBackdrop?.addEventListener('click', e => { if (e.target === menuBackdrop) setMenu(false); });
    document.addEventListener('keydown', e => {
      if (menuBackdrop.hidden) return;
      if (e.key === 'Escape') setMenu(false);
      if (e.key !== 'Tab') return;
      const options = $$('a,button', menu).filter(x => !x.hidden);
      if (e.shiftKey && (document.activeElement === options[0] || document.activeElement === menu)) { options.at(-1).focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === options.at(-1)) { options[0].focus(); e.preventDefault(); }
    });
    function home() {
      const root = $('.cp-ref-home');
      if (!root) return;
      [...main.children].filter(x => x !== root && !['STYLE','SCRIPT'].includes(x.tagName) && !x.classList.contains('flash')).forEach(x => x.classList.add('cp-home-extra'));
      const rows = $$('[data-cp-state]', root), filters = $$('[data-cp-task-filter]', root);
      const empty = $('.cp-filter-empty', root), list = $('.cp-task-list', root);
      const dot = $('#cpNotificationDot');
      if (dot) dot.hidden = !rows.some(x => ['today','overdue'].includes(x.dataset.cpState));
      function filter(key) {
        let shown = 0;
        rows.forEach(row => {
          const display = key === 'all' || row.dataset.cpState === key;
          row.hidden = !display || (!isTasks && shown >= Number(root.dataset.taskLimit || 3));
          if (display && !row.hidden) shown++;
        });
        filters.forEach(b => { const active = b.dataset.cpTaskFilter === key; b.classList.toggle('active', active); b.setAttribute('aria-pressed', String(active)); });
        empty.hidden = shown !== 0;
        list.hidden = shown === 0;
      }
      filters.forEach(b => b.addEventListener('click', () => filter(b.dataset.cpTaskFilter)));
      filter(isTasks ? params.get('filter') || 'all' : 'all');
      if (isTasks) {
        $('.cp-home-jobs', root).hidden = false;
        title.textContent = 'Görev Yönetimi';
        $('.cp-section-head h2', root).textContent = 'Yapılacak İşler';
        $('.cp-section-head>a', root).hidden = true;
      }
    }
    function modules() {
      if (!isModules) return;
      const hub = $('#cpModuleDirectory');
      if (!hub) return;
      title.textContent = 'Modüller';
      $('#cpInstall',hub)?.addEventListener('click', () => { $('#cpQuickTitle').textContent = 'Ana ekrana yükle'; $('.cp-quick-grid').innerHTML = '<p>Tarayıcının paylaşım menüsünden “Ana Ekrana Ekle” seçeneğini kullanabilirsin.</p>';$('#cpGlobalAdd').click(); });
    }

    function herd() {
      if (path !== '/all-animals' || !$('.cp-ref-list')) return;
      let request, timer, sequence = 0, composing = false;
      function bindFilters() {
        const details = $('#cpRefFilters'), button = $('.cp-ref-filter-button');
        button?.addEventListener('click', () => { details.open = !details.open;button.setAttribute('aria-expanded',String(details.open)); });
      }
      bindFilters();
      function formURL() { const form = $('#cpRefHerdForm');return '/all-animals?'+new URLSearchParams(new FormData(form)); }
      async function load(url, {focus = false, push = true} = {}) {
        const serial = ++sequence;
        request?.abort();request = new AbortController();
        const root = $('.cp-ref-list'), query = $('[name=q]',root), caret = query.selectionStart;
        const filtersOpen = $('#cpRefFilters').open;
        $('#cpRefListResults').setAttribute('aria-busy','true');
        try {
          const response = await fetch(url, {signal:request.signal,headers:{'X-Requested-With':'CiftlikPro-Reference'}});
          if (response.redirected && !response.url.includes('/all-animals')) { location.href = response.url;return; }
          if (!response.ok) throw new Error('Liste yüklenemedi');
          const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
          const fresh = $('.cp-ref-list',doc);
          if (!fresh || serial !== sequence) return;
          root.replaceWith(fresh);bindFilters();
          window.CPTextSearch.syncHerd(doc,'mobile');
          $('#cpRefFilters').open = filtersOpen;
          $('.cp-ref-filter-button').setAttribute('aria-expanded',String(filtersOpen));
          if (push) history.pushState(null,'',url);
          if (focus) { const input = $('#cpRefHerdForm [name=q]');input.focus({preventScroll:true});try { input.setSelectionRange(caret,caret); } catch {} }
        } catch (e) {
          if (e.name !== 'AbortError') location.href = url;
        } finally { if (serial === sequence) $('#cpRefListResults')?.removeAttribute('aria-busy'); }
      }
      const schedule = e => {
        if (!e.target.matches('#cpRefHerdForm [name=q]')) return;
        clearTimeout(timer);++sequence;request?.abort();
        if (composing || e.isComposing) return;
        timer = setTimeout(() => load(formURL(), {focus:true}),300);
      };
      main.addEventListener('input', schedule);
      main.addEventListener('search', schedule);
      main.addEventListener('compositionstart', e => {if (e.target.matches('#cpRefHerdForm [name=q]')) {composing=true;clearTimeout(timer);++sequence;request?.abort();}});
      main.addEventListener('compositionend', e => {if (e.target.matches('#cpRefHerdForm [name=q]')) {composing=false;schedule(e);}});
      main.addEventListener('submit', e => { if (e.target.id !== 'cpRefHerdForm') return;e.preventDefault();clearTimeout(timer);load(formURL()); });
      main.addEventListener('click', e => { const a = e.target.closest('a[data-ref-list-link]');if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;e.preventDefault();clearTimeout(timer);load(a.getAttribute('href')); });
      window.addEventListener('popstate', () => load(location.pathname+location.search, {push:false}));
    }
    function entry() {
      if (path !== '/animal-add') return;
      const form = $('#smartAnimalForm');if (!form) return;
      const cards = $$('.smart-card',form);
      const primary = document.createElement('section');primary.className = 'cp-ref-entry-primary';
      const wrapper = document.createElement('div');wrapper.className = 'cp-ref-entry-sections';
      const kind = document.createElement('label');kind.className = 'cp-ref-entry-kind-select';
      kind.innerHTML = '<span>Kayıt türü</span><select aria-label="Kayıt türü"><option value="adult">Yetişkin Hayvan</option><option value="calf">Buzağı</option></select>';
      form.prepend(kind,primary,wrapper);
      const kindSelect = $('select',kind);kindSelect.value = params.get('entry') === 'calf' ? 'calf' : 'adult';
      kindSelect.addEventListener('change', () => { $(`[data-entry-kind="${kindSelect.value}"]`)?.click();title.textContent = kindSelect.value === 'calf' ? 'Yeni Buzağı Ekle' : 'Yeni Hayvan Ekle'; });
      const field = selector => $(selector,form)?.closest('.smart-field');
      const move = (selector, wide = false) => { const label = field(selector);if (!label) return null;if (wide) label.classList.add('cp-ref-wide');primary.append(label);return label; };
      move('#tagDigits',true);move('[name=nickname]',true);
      function choiceSelect(group,fieldId,labelText) {
        const original = $(`[data-choice-group="${group}"]`,form), canonical = $('#'+fieldId,form);
        if (!original || !canonical) return null;
        original.classList.add('cp-ref-choice-original');
        const label = document.createElement('label');label.className = 'smart-field';label.textContent = labelText;
        const select = document.createElement('select');select.id = 'cpRef'+group;label.append(select);
        function sync() { const options = $$('.choice-card',original);select.replaceChildren(...options.map(button => { const option = document.createElement('option');option.value = button.dataset.value;option.textContent = button.dataset.value;return option; }));select.value = canonical.value; }
        select.addEventListener('change', () => { const button = $$('.choice-card',original).find(b => b.dataset.value===select.value);button?.click();sync(); });
        const observer = new MutationObserver(sync);observer.observe(original,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});sync();
        return label;
      }
      const gender = choiceSelect('gender','genderValue','Cinsiyeti *');if (gender) primary.append(gender);
      move('#birthDate');move('#openBreed',true);move('#paddockId',true);
      const purpose = choiceSelect('purpose','purposeValue','Kullanım Amacı *');if (purpose) primary.append(purpose);
      const pregnancy = $('#femalePregnancyBox',form);
      if (pregnancy) { primary.append(pregnancy);pregnancy.classList.add('cp-ref-wide'); }
      const oldGender = $('[data-choice-group=gender]',form)?.closest('.smart-field');if (oldGender) oldGender.hidden = true;
      const oldPurpose = $('#purposeChoices',form)?.closest('.smart-field');if (oldPurpose) oldPurpose.hidden = true;
      function detail(label,body,type) {
        const element = document.createElement('details');element.className = 'cp-ref-entry-more';
        element.innerHTML = `<summary>${icon(type)}<span>${label}</span>${icon('down')}</summary><div></div>`;
        if (body) $('div',element).append(body);wrapper.append(element);return $('div',element);
      }
      const parent = detail('Anne – Baba Bilgileri',null,'animals');
      ['#motherId','[name=father_tag]'].forEach(selector => { const label = field(selector);if (label) { label.classList.remove('born-field','conditional');label.hidden = false;parent.append(label); } });
      const location = detail('Padok ve Geliş Bilgileri',null,'paddocks');
      const arrival = choiceSelect('arrival','arrivalValue','Geliş Kaynağı *');if (arrival) location.append(arrival);
      ['#entryDate','[name=animal_type]','[name=purchase_weight]','[name=transfer_from]'].forEach(selector => { const label = field(selector);if (label) location.append(label); });
      const purchase = detail('Alış Bilgileri',null,'finance');
      $$('.purchase-field',form).forEach(label => purchase.append(label));
      const management = detail('Sağlık ve Yönetim',null,'shield');
      if (cards[3]) management.append(cards[3]);
      if (cards[0]) detail('Fotoğraf Ekle',cards[0],'camera');
      cards.filter(card => card!==pregnancy && !card.closest('.cp-ref-entry-more') && !card.closest('.cp-ref-entry-primary')).forEach(card => { if (!$$('input,select,textarea',card).some(x => x.type!=='hidden' && !x.closest('[hidden]') && !x.closest('.cp-ref-choice-original'))) card.hidden = true; });
      $('.smart-savebar button',form).textContent = 'Kaydet';
      $('#openScanner').innerHTML = icon('camera');
      const updateEntryTitle=()=> {title.textContent=$('#recordType').value==='Buzağı'?'Yeni Buzağı Ekle':'Yeni Hayvan Ekle';};
      new MutationObserver(updateEntryTitle).observe($('#recordTypeBadge'),{childList:true});
      updateEntryTitle();
      // Keep native validity useful even when an optional group is collapsed.
      form.addEventListener('invalid', e => { let parent = e.target.parentElement;while (parent && parent!==form) { if (parent.tagName==='DETAILS') parent.open = true;parent = parent.parentElement; } },true);
      $('#birthDate')?.addEventListener('change', () => { kindSelect.value = $('#recordType').value==='Buzağı' ? 'calf' : 'adult'; });
      if (params.get('arrival') === 'born' && params.get('mother')) {
        $('[data-choice-group=arrival] [data-value="Çiftlikte Doğdu"]',form)?.click();
        const mother = $('#motherId',form);mother.value = params.get('mother');mother.dispatchEvent(new Event('change',{bubbles:true}));
        const today = new Date(), birth = $('#birthDate');birth.value = [today.getFullYear(),String(today.getMonth()+1).padStart(2,'0'),String(today.getDate()).padStart(2,'0')].join('-');birth.dispatchEvent(new Event('change',{bubbles:true}));
        parent.closest('details').open = true;
      }
    }
    function detail() {
      const root = $('.cp-ref-detail');if (!root) return;
      const source = root.dataset.refSource, sid = root.dataset.refId;
      const sections = $$('[data-ref-section]',root), tabs = $$('[data-ref-tab]',root), overview = $('.cp-ref-overview',root);
      const tabStrip = $('.cp-ref-detail-tabs',root), header = $('.cp-app-header');
      // The fixed header owns the docked strip. A stable slot stays in the
      // document, so docking cannot move the boundary that triggers docking.
      const tabSlot = document.createElement('div');
      tabSlot.className = 'cp-ref-tabs-slot';
      tabStrip.before(tabSlot);tabSlot.append(tabStrip);
      const marker = document.createElement('span');
      marker.className = 'cp-ref-tabs-marker';marker.setAttribute('aria-hidden','true');
      tabSlot.prepend(marker);
      const mobileTabs = matchMedia('(max-width:900px)');
      let tabObserver, headerHeight = 0, tabsDocked = false;
      function dockTabs(docked) {
        if (tabsDocked === docked) return;
        tabsDocked = docked;
        tabStrip.classList.toggle('cp-ref-tabs-docked',docked);
        (docked ? header : tabSlot).append(tabStrip);
      }
      function syncTabs() {
        dockTabs(mobileTabs.matches && tabSlot.getBoundingClientRect().top <= headerHeight);
      }
      function measureTabs() {
        if (!mobileTabs.matches) {
          dockTabs(false);tabObserver?.disconnect();tabObserver = null;
          tabSlot.style.removeProperty('height');return;
        }
        const height = Math.ceil(tabStrip.getBoundingClientRect().height);
        if (height && tabSlot.style.height !== height+'px') tabSlot.style.height = height+'px';
        const nextHeaderHeight = Math.ceil(header.getBoundingClientRect().height);
        if (!tabObserver || nextHeaderHeight !== headerHeight) {
          headerHeight = nextHeaderHeight;
          tabObserver?.disconnect();
          tabObserver = new IntersectionObserver(syncTabs,{rootMargin:`-${headerHeight}px 0px 0px 0px`,threshold:0});
          tabObserver.observe(marker);
        }
        syncTabs();
      }
      measureTabs();
      // Resize is for geometry changes, never a per-scroll position rewrite.
      window.addEventListener('resize',measureTabs,{passive:true});
      window.addEventListener('pageshow',measureTabs);
      new ResizeObserver(measureTabs).observe(header);
      function select(name,scroll = true,focusView = scroll || name!=='general') {
        if (name==='state') return state();
        overview.hidden = focusView;
        document.body.classList.toggle('cp-ref-detail-focused',focusView);
        const actual = ['paddock','ration'].includes(name) ? 'ration' : name;
        tabs.forEach(tab => { const active = tab.dataset.refTab===actual;tab.classList.toggle('active',active);tab.setAttribute('aria-selected',String(active)); });
        sections.forEach(section => {
          const display = name==='general' || section.dataset.refSection===name || name==='ration' && ['paddock','growth'].includes(section.dataset.refSection);
          section.hidden = !display;
          section.open = name==='general' ? section.dataset.refSection==='identity' : display;
        });
        syncTabs();
        if (scroll) {
          window.scrollTo({top:Math.max(0,tabSlot.getBoundingClientRect().top+window.scrollY-headerHeight),behavior:motion});
          const active = tabs.find(tab=>tab.dataset.refTab===actual);
          if (active) { const strip = active.parentElement;strip.scrollLeft = Math.max(0, active.offsetLeft-strip.clientWidth/2+active.clientWidth/2); }
        }
        if (name!=='general' || scroll) history.replaceState(null,'',location.pathname+location.search+'#'+name);
      }
      window.showAnimalPanel = name => select(name==='operations' ? 'operations' : name);
      tabs.forEach(tab => tab.addEventListener('click', () => select(tab.dataset.refTab)));
      back?.addEventListener('click',e=>{
        if (!overview.hidden) return;
        e.preventDefault();select('general',false,false);history.replaceState(null,'',location.pathname+location.search);window.scrollTo({top:0,behavior:'auto'});
      });
      root.addEventListener('click', e => { const action = e.target.closest('[data-ref-action]');if (action) select(action.dataset.refAction); });
      function movePanel(name) {
        const target = $(`[data-ref-legacy="${name}"]`,root), panel = $(`.main>[data-animal-panel="${name}"]`);
        if (!target || !panel) return;
        const details = document.createElement('details');details.className = 'cp-ref-legacy-records';details.innerHTML = '<summary>Kayıt ayrıntıları ve işlemler</summary>';
        panel.classList.remove('animal-card-panel');panel.classList.add('cp-ref-legacy-panel');
        details.append(panel);target.append(details);
        if (name==='growth' || name==='operations') details.open = true;
      }
      ['reproduction','health','growth','finance','history','operations'].forEach(movePanel);
      if (source==='calf') {
        const growth = $('[data-ref-legacy=growth]',root), finance = $('[data-ref-legacy=finance]',root);
        ['form[action="/calf/weight"]','form[action="/calf-internal-cost/save"]','form[action="/animal/sale"]','form[action="/animal/loss"]'].forEach(selector => {
          const form = $(selector,main);if (!form) return;
          const target = selector.includes('cost') ? finance : selector.includes('weight') ? growth : $('[data-ref-legacy=operations]',root);
          if (target) {
            const card = form.closest('.card');
            const block = document.createElement('div');block.className = 'cp-ref-legacy-panel';
            if (card && selector.includes('cost')) block.append(card);else block.append(form);target.append(block);
          }
        });
      }
      if (source==='calf') {
        const weightCard=$$('main.main>.card').find(card=>card.querySelector('h2')?.textContent.includes('Kilo Geçmişi'));
        if (weightCard) $('[data-ref-legacy=growth]',root)?.append(weightCard);
        const operation=$('[data-ref-section=operations] .cp-ref-accordion-body',root);
        if (operation) {const link=document.createElement('a');link.className='cp-ref-bar';link.href='/finance?app_action=add';link.textContent='Buzağı satışını Finans ekranından kaydet';operation.prepend(link);}
      }
      const upload = $(`form[action="/${source}/photo"]`,main), uploadTarget = $('[data-ref-upload]',root);
      if (upload && uploadTarget) {
        const box = document.createElement('details');box.className = 'cp-ref-upload';box.innerHTML='<summary>Fotoğraf seç ve yükle</summary>';box.append(upload);uploadTarget.append(box);
        upload.addEventListener('change', e => { if (e.target.type !== 'file') return;const label = $('summary',box);label.textContent = e.target.files.length ? e.target.files[0].name : 'Fotoğraf seç ve yükle'; });
        $$('[data-ref-photo-add]',root).forEach(button => button.addEventListener('click', () => { box.open = true;$('input[type=file]',upload)?.click(); }));
      }
      function state() {
        window.cpOpenAnimalState?.(`/animal-events?source=${source}&id=${sid}`,document.activeElement);
      }
      function more() {
        const content=document.createElement('section');content.className='cp-state-content';
        const hasRepro = !!$('[data-ref-section=reproduction]',root);
        const choice=(url,title,note,kind,tone,attrs='')=>`<a class="cp-state-choice" href="${url}" ${attrs}><span class="cp-state-icon cp-state-${tone}">${icon(kind)}</span><span><b>${title}</b><small>${note}</small></span>${icon('chevron')}</a>`;
        const links=choice(`/${source}-edit?id=${sid}`,'Hayvan bilgilerini düzenle','Kimlik, küpe ve temel bilgiler','edit','slate')
          +(hasRepro ? choice(`/dairy-status?animal=${sid}`,'Laktasyon durumunu düzenle','Sağmal, kuru veya düve durumu','milk','green')+choice(`/reproduction-center?animal=${sid}`,'Üreme / gebelik durumunu güncelle','Tohumlama ve gebelik kayıtları','heart','pink') : '')
          +choice('#operations','Satış / zayiat işlemleri','Satış, kesim veya kayıp kaydı','finance','blue','data-ref-state-sale')
          +choice('#operations','Hayvan kaydını sil','Silme seçeneklerini ve onayı aç','close','red','data-ref-state-delete')
          +(source==='animal' ? choice(`/animal/print?id=${sid}`,'Hayvan kartını yazdır','Kimlik ve kayıtları görüntüle','reports','slate') : '');
        content.innerHTML='<div class="cp-state-handle" aria-hidden="true"></div><header class="cp-state-head"><div><h2 id="cpStateTitle">Hayvan İşlemleri</h2></div><button type="button" class="cp-state-cancel" data-cp-state-close>Vazgeç</button></header><div class="cp-state-subject"><span class="cp-state-subject-icon">'+icon('animals')+'</span><div><b></b><small></small></div></div><div class="cp-state-body"><nav class="cp-state-choices" aria-label="Hayvan işlemleri">'+links+'</nav></div>';
        $('.cp-state-subject b',content).textContent=$('.cp-ref-profile h1',root).textContent;
        $('.cp-state-subject small',content).textContent=$$('.cp-ref-profile .cp-ref-badge',root).map(b=>b.textContent).join(' · ');
        window.cpOpenAnimalMenu(content,document.activeElement);
        $('[data-ref-state-sale]',content).addEventListener('click',e=>{e.preventDefault();window.cpCloseAnimalPanel();select('operations');});
        $('[data-ref-state-delete]',content).addEventListener('click',e=>{e.preventDefault();window.cpCloseAnimalPanel();select('operations');$('.cp-ref-delete',root).open=true;});
      }
      $('#cpAnimalMore')?.addEventListener('click',more);
      window.addEventListener('hashchange',()=>{
        const name=location.hash.slice(1);
        if (!name) return select('general',false,false);
        const target=['animalSale','animalLoss'].includes(name)?'operations':name;
        if (target==='general' || sections.some(section=>section.dataset.refSection===target)) select(target,false,true);
      });
      let initial = location.hash.slice(1);
      if (['animalSale','animalLoss'].includes(initial)) initial='operations';
      if (initial && (initial==='general' || sections.some(section=>section.dataset.refSection===initial))) select(initial,false,true);
      else select('general',false);
    }
    function healthTarget() {
      if (path !== '/health' || !params.get('subject')) return;
      const [source,sid] = params.get('subject').split(':');
      const wanted = (source==='calf' ? 'C:' : 'A:')+sid;
      const form = $('#healthForm');if (!form) return;
      const key = $('#healthSubjectKey',form), search = $('#healthSubjectSearch',form);
      if (key && search) {
        key.value = wanted;
        const choices = typeof healthSubjects !== 'undefined' ? healthSubjects : [];
        search.value = choices.find(item => item.key===wanted)?.label || params.get('search') || '';
      }
      const select = $('select[name=target]',form) || $('select[name=subject]',form);
      if (select && [...select.options].some(option=>option.value===wanted)) { select.value=wanted;select.dispatchEvent(new Event('change',{bubbles:true})); }
      const matching = $$('input[type=checkbox]',form).find(input=>input.value===wanted);
      if (matching) { matching.checked=true;matching.dispatchEvent(new Event('change',{bubbles:true})); }
    }
    home();modules();herd();entry();detail();healthTarget();
    if (isTasks || !['/','/all-animals','/animal','/calf','/animal-add','/animal-edit','/calf-edit','/dairy-status','/paddocks'].includes(path)) {
      $$('.cp-bottom-nav [data-cp-nav]').forEach(link=>{const active=link.dataset.cpNav==='modules';link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});
    }
    // Tiny, readable build marker makes an installed update easy to identify.
    document.documentElement.dataset.cpMobileBuild = config.build;
  }
  if (document.readyState === 'complete') start();
  else document.addEventListener('DOMContentLoaded',start,{once:true});
})();
