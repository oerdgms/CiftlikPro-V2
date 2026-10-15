/* Presentation only: original forms, record IDs and Enterprise handlers stay intact. */
(() => {
  'use strict';
  function initialize() {
  const configNode = document.getElementById('cpAppConfig');
  if (!configNode) return;
  const config = JSON.parse(configNode.textContent);
  const mobile = window.matchMedia('(max-width:900px)');
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const path = location.pathname;
  const params = new URL(config.request_url || location.href,location.origin).searchParams;
  const main = $('main.main');
  let installPrompt = null;
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    installPrompt = event;
    const button = $('#cpInstall');
    if (button) button.hidden = false;
  });
  if ('serviceWorker' in navigator && window.isSecureContext) {
    navigator.serviceWorker.register('/app-service-worker.js', {scope:'/'}).catch(() => {});
  }
  if (!mobile.matches) {
    mobile.addEventListener('change', () => location.reload(), {once:true});
    return;
  }
  mobile.addEventListener('change', () => location.reload(), {once:true});
  function lockMobileViewport() {
    document.documentElement.classList.add('cp-viewport-locked');
    const stopGesture = event => event.preventDefault();
    ['gesturestart','gesturechange','gestureend'].forEach(name => document.addEventListener(name,stopGesture,{passive:false}));
    let tapStart = null;
    document.addEventListener('touchstart',event => {
      const touch = event.touches[0];
      tapStart = event.touches.length === 1 ? {time:event.timeStamp,x:touch.clientX,y:touch.clientY,moved:false} : null;
    },{passive:true});
    document.addEventListener('touchmove',event => {
      if (event.touches && event.touches.length > 1) event.preventDefault();
      const touch = event.touches[0];
      if (tapStart && touch && Math.hypot(touch.clientX-tapStart.x,touch.clientY-tapStart.y)>10) tapStart.moved = true;
    },{passive:false});
    // CSS contains horizontal overflow. Never interrupt native scroll momentum.
    let lastTap = null;
    document.addEventListener('touchend',event => {
      if (event.changedTouches.length !== 1 || event.touches.length || !tapStart || tapStart.moved || event.timeStamp-tapStart.time>300) { lastTap = null; return; }
      const touch = event.changedTouches[0], now = event.timeStamp;
      const interactive = event.target.closest('input,select,textarea,button,a,label,[role="button"],[contenteditable="true"]');
      if (!interactive && lastTap && lastTap.target===event.target && now-lastTap.time<350 && Math.hypot(touch.clientX-lastTap.x,touch.clientY-lastTap.y)<24) {
        event.preventDefault();
        lastTap = null;
      } else lastTap = {time:now,x:touch.clientX,y:touch.clientY,target:event.target};
      tapStart = null;
    },{passive:false});
    document.addEventListener('dblclick',event => {
      if (!event.target.closest('input,select,textarea,button,a,label,[role="button"],[contenteditable="true"]')) event.preventDefault();
    },{passive:false});
  }
  lockMobileViewport();
  if (config.login) {
    const logo = $('.login-logo');
    if (logo) logo.innerHTML = '<svg class="cp-icon" viewBox="0 0 24 24" fill="none" stroke="#9bd580" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="M12 21V9M12 14C3 15 3 5 3 5c8-1 10 3 9 9M12 10c0-8 9-8 9-8 1 7-3 10-9 8"/></svg> ÇiftlikPro';
    const description = $('.login-visual p');
    if (description) description.textContent = 'Sürü yönetimi her zaman yanında';
    return;
  }
  if (!main) return;
  const title = $('#cpScreenTitle');
  const subtitle = $('#cpScreenSubtitle');
  const nav = $('.cp-bottom-nav');
  const icons = Object.fromEntries($$('[data-cp-nav]').map(a => [a.dataset.cpNav, $('svg',a).outerHTML]));
  const quickOverlay = $('#cpQuickOverlay');
  const quickSheet = $('.cp-sheet', quickOverlay);
  const quickButton = $('#cpGlobalAdd');
  let previousFocus = null;
  let previousOverflow = '';
  function setQuick(open) {
    if (open) {
      previousFocus = document.activeElement;
      previousOverflow = document.body.style.overflow;
      quickOverlay.hidden = false;
      document.body.style.overflow = 'hidden';
      quickSheet.focus();
    } else {
      quickOverlay.hidden = true;
      document.body.style.overflow = previousOverflow;
      previousFocus?.focus();
    }
  }
  $('[data-cp-close]', quickOverlay).addEventListener('click', () => setQuick(false));
  quickOverlay.addEventListener('click', event => { if (event.target === quickOverlay) setQuick(false); });
  document.addEventListener('keydown', event => {
    if (quickOverlay.hidden) return;
    if (event.key === 'Escape') setQuick(false);
    if (event.key === 'Tab') {
      const focusable = $$('a,button',quickSheet);
      if (event.shiftKey && (document.activeElement === focusable[0] || document.activeElement === quickSheet)) {
        focusable.at(-1).focus(); event.preventDefault();
      } else if (!event.shiftKey && document.activeElement === focusable.at(-1)) {
        focusable[0].focus(); event.preventDefault();
      }
    }
  });
  const moduleView = path === '/' && params.get('app_view') === 'modules';
  const taskView = path === '/' && params.get('app_view') === 'tasks';
  const activeNav = moduleView ? 'modules' : taskView || path.startsWith('/health') ? 'jobs' : path === '/' ? 'home' : /animal|calf|archive|estrus|insemination|reproduction/.test(path) ? 'animals' : path.startsWith('/paddock') ? 'paddocks' : 'modules';
  $$('[data-cp-nav]',nav).forEach(a => {
    const active = a.dataset.cpNav === activeNav;
    a.classList.toggle('active',active);
    if (active) a.setAttribute('aria-current','page');
  });
  document.body.classList.toggle('cp-modules-route', moduleView);
  document.body.classList.toggle('cp-tasks-route', taskView);
  const routeTitles = {'/ration-workbench':'Rasyon Detayı','/animal-add':'Yeni Hayvan','/animal-edit':'Hayvanı Düzenle','/calf-edit':'Buzağıyı Düzenle','/finance/edit':'Finans Kaydı','/paddock-edit':'Padoku Düzenle'};
  if (routeTitles[path]) title.textContent = routeTitles[path];
  function networkStatus() { $('.cp-network-status').hidden = navigator.onLine; }
  window.addEventListener('online',networkStatus);
  window.addEventListener('offline',networkStatus);
  networkStatus();

  function home() {
    const homeElement = $('.cp-home',main);
    if (!homeElement) return;
    [...main.children].forEach(child => {
      if (child !== homeElement && !['STYLE','SCRIPT'].includes(child.tagName) && !child.classList.contains('flash')) child.classList.add('cp-home-extra');
    });
    if (taskView) {
      title.textContent = 'İşler';
      subtitle.textContent = 'Sağlık planları ve vadeli ödemeler';
      $('.cp-section-head h2',homeElement).textContent = 'Yapılacak işler';
      $('.cp-section-head a',homeElement).hidden = true;
    }
    const filters = $$('[data-cp-task-filter]',homeElement);
    const tasks = $$('[data-cp-state]',homeElement);
    function filterTasks(filter) {
      filters.forEach(button => {
        const selected = button.dataset.cpTaskFilter === filter;
        button.classList.toggle('active',selected);
        button.setAttribute('aria-pressed',String(selected));
      });
      tasks.forEach(row => { row.hidden = filter !== 'all' && row.dataset.cpState !== filter; });
      $('.cp-filter-empty',homeElement).hidden = tasks.some(row => !row.hidden);
      const count = tasks.filter(row => !row.hidden).length;
      $('.cp-total',homeElement).textContent = count;
      if (taskView) subtitle.textContent = count + ' iş · sağlık ve ödemeler';
    }
    filters.forEach(button => button.addEventListener('click', () => filterTasks(button.dataset.cpTaskFilter)));
    filterTasks(taskView ? 'all' : 'today');
    const dot = $('#cpNotificationDot');
    if (dot) dot.hidden = !tasks.some(row => ['today','overdue'].includes(row.dataset.cpState));
  }
  function moduleHub() {
    const sidebar = $('#sideMenu');
    const available = $$('a[href]',sidebar).map(a => ({url:a.getAttribute('href'),text:a.textContent.trim()}));
    const modules = [
      ['finance','Finans','Gelir, gider ve vadeli ödemeler','/finance'],
      ['feeds','Yem & Stok','Yem kataloğu ve stok hareketleri','/feeds'],
      ['ration','Rasyon','Reçeteler ve rasyon çözümleyici','/rations'],
      ['animals','Hayvanlar','Aktif sürü ve hayvan kartları','/all-animals'],
      ['paddocks','Padoklar','Hayvanlar, kapasite ve transfer','/paddocks'],
      ['health','Sağlık','Aşılar, tedaviler ve planlar','/health'],
      ['reproduction','Üreme','Kızgınlık, tohumlama ve gebelik','/reproduction-center'],
      ['milk','Süt','Günlük süt ve laktasyon','/milk-center'],
      ['farm','Tarım','Tarlalar, üretim ve hasat','/agriculture'],
      ['reports','Raporlar','Raporlar ve çıktı alma','/reports'],
      ['settings','Ayarlar','İşletme ve program ayarları','/farm-profile']
    ];
    const quickGlyphs = Object.fromEntries($$('a[data-cp-quick]',quickOverlay).map(a => [a.dataset.cpQuick,$('svg',a).outerHTML]));
    const glyph = type => icons[type] || quickGlyphs[type] || icons.modules;
    const primaryUrls = new Set(modules.map(x => x[3]));
    const extras = available.filter(x => !primaryUrls.has(x.url) && x.url !== '/');
    const hub = document.createElement('section');
    hub.className = 'cp-module-hub';
    hub.innerHTML = '<p class="cp-module-title">Çiftliğinin tüm işlemleri tek yerde</p><div class="cp-module-list">' + modules.map(([type,name,description,url]) => '<a href="'+url+'"><span class="cp-module-glyph">'+glyph(type)+'</span><div><b>'+name+'</b><small>'+description+'</small></div><span class="cp-chevron">›</span></a>').join('') + '</div><details class="cp-module-tools"><summary>Diğer ekranlar ve sistem araçları</summary>'+extras.map(item => '<a href="'+escape(item.url)+'">'+escape(item.text)+'</a>').join('')+'</details><div class="cp-module-footer"><button type="button" id="cpOpenQuick">Hızlı işlem +</button><a href="/logout">Çıkış yap</a></div><div class="cp-module-footer"><button type="button" id="cpInstall" hidden>Ana ekrana yükle</button></div>';
    main.prepend(hub);
    title.textContent = 'Modüller';
    subtitle.textContent = config.user;
    $('#cpOpenQuick',hub).addEventListener('click', () => setQuick(true));
    const install = $('#cpInstall',hub);
    install.hidden = !installPrompt;
    install.addEventListener('click',async () => {
      if (!installPrompt) return;
      await installPrompt.prompt();
      await installPrompt.userChoice;
      installPrompt = null;
      install.hidden = true;
    });
  }

  function animalEntry() {
    if (path !== '/animal-add') return;
    const form = $('#smartAnimalForm',main);
    const head = $('.smart-animal-head',main);
    if (!form || !head) return;
    const birth = $('#birthDate',form);
    const recordType = $('#recordType',form);
    const badge = $('#recordTypeBadge',main);
    const hint = $('#recordHint',form);
    const pageHeading = $('.smart-animal-head h1',main);
    if (!birth || !recordType || !badge || !hint) return;
    const chooser = document.createElement('section');
    chooser.className = 'cp-entry-kind';
    chooser.innerHTML = '<div><b>Kayıt türü</b><small>Yetişkin hayvan veya buzağı seç</small></div><div class="cp-entry-kind-buttons"><button type="button" data-entry-kind="adult">🐄 Yetişkin</button><button type="button" data-entry-kind="calf">🐮 Buzağı</button></div><p>Buzağı kaydında doğum tarihi zorunludur ve hayvan 10 aydan küçük olmalıdır.</p>';
    head.after(chooser);
    const buttons = $$('[data-entry-kind]',chooser);
    let mode = params.get('entry') === 'calf' ? 'calf' : 'adult';
    const today = new Date();
    const todayIso = [today.getFullYear(),String(today.getMonth()+1).padStart(2,'0'),String(today.getDate()).padStart(2,'0')].join('-');
    birth.max = todayIso;
    function ageMonths() {
      if (!birth.value) return null;
      const parts = birth.value.split('-').map(Number);
      if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
      return Math.max(0,(today.getFullYear()-parts[0])*12+today.getMonth()-(parts[1]-1)-(today.getDate()<parts[2]?1:0));
    }
    function updateAddress() {
      const url = new URL(location.href);
      url.searchParams.set('entry',mode);
      history.replaceState(null,'',url.pathname+url.search+url.hash);
    }
    function verifyCalfMode() {
      const age = ageMonths();
      birth.setCustomValidity('');
      if (mode === 'calf') {
        birth.required = true;
        title.textContent = 'Yeni Buzağı';
        if (pageHeading) pageHeading.textContent = '🐮 Yeni Buzağı';
        badge.textContent = 'Buzağı kaydı';
        if (age === null) {
          hint.textContent = 'Buzağı · doğum tarihi zorunlu';
        } else if (age >= 10) {
          birth.setCustomValidity('Buzağı kaydı için doğum tarihi 10 aydan küçük olmalıdır.');
          hint.textContent = age+' aylık · yetişkin kaydı seçilmeli';
        } else {
          recordType.value = 'Buzağı';
          hint.textContent = 'Buzağı · '+age+' aylık';
        }
      } else {
        birth.required = false;
        title.textContent = 'Yeni Hayvan';
        if (pageHeading) pageHeading.textContent = '🐄 Yeni Hayvan';
      }
    }
    function setMode(next,{focus=false,writeUrl=true}={}) {
      const age = ageMonths();
      mode = next === 'calf' || (age !== null && age < 10) ? 'calf' : 'adult';
      document.body.classList.toggle('cp-calf-entry-mode',mode === 'calf');
      buttons.forEach(button => {
        const selected = button.dataset.entryKind === mode;
        button.classList.toggle('active',selected);
        button.setAttribute('aria-pressed',String(selected));
      });
      verifyCalfMode();
      if (writeUrl) updateAddress();
      if (focus && mode === 'calf' && !birth.value) {
        birth.scrollIntoView({behavior:'smooth',block:'center'});
        setTimeout(() => birth.focus({preventScroll:true}),250);
      }
    }
    buttons.forEach(button => button.addEventListener('click',() => setMode(button.dataset.entryKind,{focus:true})));
    const syncFromBirth = () => {
      const age = ageMonths();
      if (age !== null && age < 10 && mode !== 'calf') setMode('calf');
      else verifyCalfMode();
    };
    birth.addEventListener('input',syncFromBirth);
    birth.addEventListener('change',syncFromBirth);
    form.addEventListener('submit',event => {
      verifyCalfMode();
      if (!birth.checkValidity()) {
        event.preventDefault();
        birth.reportValidity();
      }
    });
    setMode(mode,{writeUrl:false});
  }

  function animalCards() {
    if (path === '/animal') document.body.classList.add('cp-animal-card-compact');
    if (path !== '/calf') return;
    const profile = $('.profile',main);
    if (!profile || profile.dataset.cpCardLayout) return;
    profile.dataset.cpCardLayout = '1';
    profile.classList.add('cp-calf-profile');
    const info = profile.children[1];
    if (info) {
      info.classList.add('cp-calf-profile-info');
      const costboxes = [...info.children].filter(element => element.classList.contains('costbox'));
      if (costboxes.length) {
        const financial = document.createElement('section');
        financial.className = 'cp-calf-financial';
        financial.setAttribute('aria-label','Buzağı maliyet ve finans özeti');
        costboxes.forEach(box => financial.append(box));
        profile.append(financial);
      }
    }
    $('.calf-entry-grid',main)?.classList.add('cp-calf-entry');
    const internalForm = $('form[action="/calf-internal-cost/save"]',main);
    internalForm?.closest('.card')?.classList.add('cp-calf-internal');
  }

  function cardTable(table, finance = false) {
    if (!table || table.dataset.cpEnhanced) return;
    table.dataset.cpEnhanced = '1';
    table.classList.add('cp-record-table');
    const headers = $$('tr',table).find(row => $('th',row));
    const labels = headers ? $$('th',headers).map(th => th.textContent.trim()) : [];
    $$('tr',table).forEach(row => {
      const cells = [...row.children].filter(cell => cell.tagName === 'TD');
      if (cells.length < 2) return;
      row.classList.add('cp-record');
      cells.forEach((cell,index) => { cell.dataset.cpLabel = cell.dataset.label || labels[index] || ''; });
      const last = cells.at(-1);
      const containsActions = !!$('button,form,a',last);
      let actionsCell = last;
      if (!containsActions) {
        actionsCell = document.createElement('td');
        row.append(actionsCell);
      }
      actionsCell.classList.add('cp-actions-cell');
      const existing = document.createElement('div');
      existing.className = 'cp-existing-actions';
      while (actionsCell.firstChild) existing.append(actionsCell.firstChild);
      actionsCell.append(existing);
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'cp-row-toggle';
      button.textContent = '⋯';
      button.setAttribute('aria-label', cells[0].textContent.trim().slice(0,45) + ' bilgileri ve işlemleri');
      button.setAttribute('aria-expanded','false');
      button.addEventListener('click', () => {
        const expanded = row.classList.toggle('cp-row-open');
        button.setAttribute('aria-expanded',String(expanded));
      });
      actionsCell.prepend(button);
      if (finance && cells.length === 10) {
        row.classList.add('cp-finance-record');
        const income = cells[1].textContent.trim() === 'Gelir';
        row.classList.toggle('cp-income',income);
        const dateText = cells[0].textContent.trim();
        const dateParts = dateText.split('/');
        const month = ['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'][Number(dateParts[1])-1] || '';
        cells[0].innerHTML = '<time class="cp-finance-date" title="'+escape(dateText)+'"><b>'+escape(dateParts[0])+'</b><span>'+month+'</span></time>';
        const metadata = document.createElement('span');
        metadata.className = 'cp-finance-meta';
        metadata.textContent = cells[1].textContent.trim()+' · '+cells[6].textContent.trim();
        cells[3].append(metadata);
        const edit = $('a[href^="/finance/edit"]',existing);
        if (edit) {
          cells[3].classList.add('cp-finance-link');
          cells[3].addEventListener('click',event => {
            if (!event.target.closest('a,button,input,select,form')) location.href = edit.href;
          });
        }
        const amount = $('b',cells[8]);
        if (amount) amount.textContent = (income ? '+' : '−') + amount.textContent;
        cells[8].classList.add('cp-finance-amount');
        // Keep the disclosure inside the compact card header. The original
        // action cell remains available for the real Edit/Delete controls,
        // but no longer creates an empty row while the card is closed.
        cells[8].append(button);
      }
    });
  }
  function enhanceTables() {
    $$('.herd-table,.paddock-animal-table,.archive-animal-table,.mobile-animal-table,.health-group table',main).forEach(table => cardTable(table));
    cardTable($('.finance-table',main),true);
    if (path === '/feeds') $$('main table').forEach(table => { if ($$('th',table).length >= 8) cardTable(table); });
    if (path === '/calf') $$('.tablewrap table',main).forEach(table => {
      table.classList.add('cp-calf-record-table');
      cardTable(table);
      $$('.cp-record',table).forEach(row => {
        row.classList.add('cp-row-open');
        $('.cp-row-toggle',row)?.setAttribute('aria-expanded','true');
      });
    });
  }
  function herd() {
    const strip = $('.herd-category-strip');
    if (!strip || strip.dataset.cpEnhanced) return;
    strip.dataset.cpEnhanced = '1';
    const archiveLinks = $$('a[href^="/archive/"]',strip);
    const detail = document.createElement('details');
    detail.className = 'cp-archive-links';
    detail.innerHTML = '<summary>Satılan, kesilen ve ölen / kayıp hayvanlar</summary><div></div>';
    archiveLinks.forEach(a => $('div',detail).append(a));
    strip.append(detail);
    const filter = $('.herd-filter',main);
    if (filter) strip.before(filter);
    const filterDetails = $('.herd-filter-details',main);
    if (filterDetails) {
      filterDetails.open = !!new URLSearchParams(location.search).get('paddock');
      const header = $('.workspace-hero',main);
      const actions = $('.workspace-actions',header);
      if (actions) filterDetails.append(actions);
      const views = $('.herd-view-switch',main);
      if (views) {
        filterDetails.append(views);
        $$('button',views).forEach(button => button.addEventListener('click',() => {
          const detailMode = button.textContent.includes('Ayrıntı');
          $$('.herd-table .cp-record',main).forEach(row => {
            row.classList.toggle('cp-row-open',detailMode);
            $('.cp-row-toggle',row)?.setAttribute('aria-expanded',String(detailMode));
          });
        }));
      }
      if (header) header.classList.add('cp-herd-primary-header');
    }
    $$('.herd-photo',main).filter(photo => !$('img',photo)).forEach(photo => { photo.innerHTML = icons.animals; });
    const summary = $('.herd-result-summary');
    if (summary) subtitle.textContent = summary.textContent.trim();
  }
  function segment(select) {
    if (!select || !select.options.length) return;
    const box = document.createElement('div');
    box.className = 'cp-segment';
    const buttons = [...select.options].map(option => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option.textContent;
      button.dataset.value = option.value;
      button.addEventListener('click',() => {
        select.value = option.value;
        select.dispatchEvent(new Event('change',{bubbles:true}));
        refresh();
      });
      box.append(button);
      return button;
    });
    function refresh() {
      buttons.forEach(button => {
        const selected = button.dataset.value === select.value;
        button.classList.toggle('active',selected);
        button.setAttribute('aria-pressed',String(selected));
      });
    }
    select.classList.add('cp-sr-select');
    select.after(box);
    select.addEventListener('change',refresh);
    select.form?.addEventListener('change',() => requestAnimationFrame(refresh));
    refresh();
  }
  function finance() {
    const summary = $('main.main>.grid');
    if (summary) {
      const detail = document.createElement('details');
      detail.className = 'cp-summary-details';
      detail.innerHTML = '<summary>Finans özeti · gelir, gider ve net</summary>';
      summary.before(detail);
      detail.append(summary);
    }
    const form = $('.finance-toolbar');
    if (form) {
      const filters = document.createElement('details');
      filters.className = 'cp-filter-disclosure';
      filters.innerHTML = '<summary>Tarih aralığı ve diğer filtreler</summary><div class="cp-filter-more"></div>';
      const labels = [...form.children].filter(x => x.tagName==='LABEL');
      labels.slice(1).forEach(label => $('.cp-filter-more',filters).append(label));
      const actions = $('.finance-filter-actions',form);
      if (actions) $('.cp-filter-more',filters).append(actions);
      form.append(filters);
    }
    segment($('#tx'));
  }
  function paddocks() {
    const cards = $$('[data-paddock-card]');
    if (!cards.length) return;
    document.body.classList.toggle('cp-pad-list',!params.has('selected'));
    document.body.classList.toggle('cp-pad-detail',params.has('selected'));
    subtitle.textContent = cards.length + ' padok';
    let listScroll = 0;
    cards.forEach(card => {
      const panel = $('[data-paddock-panel="'+card.dataset.paddockCard+'"]');
      const info = $$('.paddock-info-grid>div',panel);
      const population = info.find(x => x.textContent.includes('Hayvan Sayısı'));
      const populationText = population ? $('b',population)?.textContent.trim() : '';
      const strong = $('.paddock-card-copy strong',card);
      if (strong && populationText) strong.textContent = populationText;
      const rationInfo = info.find(x => $('span',x)?.textContent.includes('Rasyon'));
      const rationName = rationInfo ? $('b',rationInfo)?.textContent : '';
      const ration = document.createElement('span');
      ration.className = 'cp-pad-ration';
      ration.textContent = rationName || 'Rasyon ataması yok';
      card.append(ration);
      const house = $('.paddock-house',card);
      if (house) house.innerHTML = icons.paddocks;
      card.addEventListener('click',() => {
        listScroll = window.scrollY;
        document.body.classList.remove('cp-pad-list');
        document.body.classList.add('cp-pad-detail');
        title.textContent = $('.paddock-panel-title h2',panel)?.textContent || 'Padok';
        window.scrollTo({top:0,behavior:'auto'});
      });
    });
    if (params.has('selected')) {
      const selected = $('[data-paddock-panel="'+params.get('selected')+'"]');
      if (selected) title.textContent = $('.paddock-panel-title h2',selected)?.textContent || 'Padok';
    }
    $('.cp-header-back').addEventListener('click',event => {
      if (!document.body.classList.contains('cp-pad-detail')) return;
      event.preventDefault();
      document.body.classList.add('cp-pad-list');
      document.body.classList.remove('cp-pad-detail');
      title.textContent = 'Padoklar';
      window.scrollTo({top:listScroll,behavior:'auto'});
    });
    const moveLaunch = document.createElement('button');
    moveLaunch.type = 'button';
    moveLaunch.className = 'btn alt cp-bulk-launch';
    moveLaunch.textContent = '⇄ Toplu hayvan taşı';
    $('.paddock-search-count')?.after(moveLaunch);
    moveLaunch.addEventListener('click',() => openBulkMove(''));
    $$('[data-move-paddock]').forEach(button => {
      const bulk = document.createElement('button');
      bulk.type = 'button';
      bulk.className = 'btn alt';
      bulk.textContent = 'Toplu taşı';
      bulk.addEventListener('click',() => openBulkMove(button.dataset.movePaddock));
      button.after(bulk);
    });
  }
  function openBulkMove(from) {
    const original = $('#paddockMoveDialog');
    if (!original) return;
    $('#cpBulkMoveDialog')?.remove();
    const sourceSelect = $('[name=animal_ref]',original);
    const targetSelect = $('[name=paddock_id]',original);
    const choices = [...sourceSelect.options].filter(option => option.value && (!from || option.dataset.paddock === String(from)));
    const dialog = document.createElement('dialog');
    dialog.id = 'cpBulkMoveDialog';
    dialog.className = 'paddock-dialog cp-bulk-move';
    dialog.innerHTML = '<div class="paddock-dialog-head"><div><h2>Padok taşıma</h2><span class="mut">Seçtiğin hayvanlar birlikte taşınır.</span></div><button type="button" class="paddock-dialog-close" id="cpMoveClose" aria-label="Kapat">×</button></div><div class="paddock-dialog-body"><form method="post" action="/paddock/assign-many" class="form"><input type="hidden" name="return_paddock_id" value="'+escape(from)+'"><input type="hidden" name="animal_refs" id="cpMoveRefs"><section class="cp-move-step"><h3><span>1</span> Taşınacak hayvanlar <small id="cpMoveCount">0 seçili</small></h3><input type="search" id="cpMoveSearch" placeholder="Küpe veya isim ara…"><div class="cp-move-tools"><button type="button" id="cpMoveAll">Görünenleri seç</button><button type="button" id="cpMoveClear">Temizle</button></div><div class="cp-move-choices">'+choices.map(option => '<label class="cp-move-choice" data-search="'+escape(option.textContent.toLocaleLowerCase('tr-TR'))+'"><input type="checkbox" value="'+escape(option.value)+'"><span>'+icons.animals+'</span><b>'+escape(option.textContent)+'</b></label>').join('')+'</div></section><section class="cp-move-step"><h3><span>2</span> Hedef padok</h3><label>Padok<select name="paddock_id" required id="cpMoveTarget">'+[...targetSelect.options].filter(option => option.value && option.value!==String(from)).map(option => '<option value="'+escape(option.value)+'">'+escape(option.textContent)+'</option>').join('')+'</select></label><label>Not<input name="notes" placeholder="İsteğe bağlı"></label></section><div class="paddock-dialog-actions"><button type="button" class="btn alt" id="cpMoveCancel">İptal</button><button type="submit" class="btn" id="cpMoveSubmit">Taşı (0)</button></div><p class="mut">Kapasite ve kayıtlar birlikte kontrol edilir. İşlem başarısızsa hiçbir hayvan taşınmaz.</p></form></div>';
    $('.paddock-page').append(dialog);
    const checks = $$('input[type=checkbox]',dialog);
    const submit = $('#cpMoveSubmit',dialog);
    function update() {
      const refs = checks.filter(input => input.checked).map(input => input.value);
      $('#cpMoveRefs',dialog).value = JSON.stringify(refs);
      $('#cpMoveCount',dialog).textContent = refs.length+' seçili';
      submit.textContent = 'Taşı ('+refs.length+')';
      submit.disabled = !refs.length;
    }
    checks.forEach(input => input.addEventListener('change',update));
    $('#cpMoveSearch',dialog).addEventListener('input',event => {
      const term = event.target.value.trim().toLocaleLowerCase('tr-TR');
      $$('.cp-move-choice',dialog).forEach(row => { row.hidden = !row.dataset.search.includes(term); });
    });
    $('#cpMoveAll',dialog).addEventListener('click',() => { checks.filter(input => !input.closest('.cp-move-choice').hidden).forEach(input => { input.checked = true; }); update(); });
    $('#cpMoveClear',dialog).addEventListener('click',() => { checks.forEach(input => { input.checked = false; }); update(); });
    ['cpMoveClose','cpMoveCancel'].forEach(id => $('#'+id,dialog).addEventListener('click',() => dialog.close()));
    $('form',dialog).addEventListener('submit',event => {
      update();
      if (!checks.some(input => input.checked)) { event.preventDefault(); return; }
      submit.disabled = true;
      submit.textContent = 'Taşınıyor…';
    });
    update();
    dialog.showModal();
  }
  function rations() {
    const grid = $('.ration-picker-grid');
    if (!grid) return;
    const cards = $$('.ration-picker-card',grid);
    const search = document.createElement('input');
    search.type = 'search';
    search.className = 'cp-list-search';
    search.placeholder = 'Rasyon adı ara…';
    search.setAttribute('aria-label','Rasyon ara');
    const filters = document.createElement('div');
    filters.className = 'cp-ration-filters';
    filters.innerHTML = ['Tümü','Süt','Besi','Buzağı'].map((name,index) => '<button type="button"'+(index===0?' class="active"':'')+'>'+name+'</button>').join('');
    grid.before(search,filters);
    const empty = document.createElement('div');
    empty.className = 'cp-empty';empty.textContent = 'Aramana uygun rasyon bulunamadı.';empty.hidden = true;grid.after(empty);
    let group = 'Tümü';
    function filter() {
      const term = search.value.trim().toLocaleLowerCase('tr-TR');
      cards.forEach(card => {
        const text = card.textContent.toLocaleLowerCase('tr-TR');
        card.hidden = !text.includes(term) || group !== 'Tümü' && !text.includes(group.toLocaleLowerCase('tr-TR'));
      });
      empty.hidden = cards.some(card => !card.hidden);
    }
    $$('button',filters).forEach(button => button.addEventListener('click',() => {
      group = button.textContent;
      $$('button',filters).forEach(b => b.classList.toggle('active',b===button));
      filter();
    }));
    search.addEventListener('input',filter);
    const meta = config.ration_meta || {};
    cards.forEach(card => {
      const id = new URL(card.href).searchParams.get('id');
      const item = meta[id];
      if (!item) return;
      const info = document.createElement('span');
      info.className = 'cp-ration-pads';
      info.innerHTML = item.paddocks.length ? '<b>'+item.paddocks.length+' padok</b> '+escape(item.paddocks.join(', ')) : escape(item.feed_count+' yem · Aktif padok ataması yok');
      card.append(info);
    });
    subtitle.textContent = cards.length+' rasyon';
  }
  function rationWorkbench() {
    const table = $('.ration-workbench-table');
    if (!table) return;
    const lockSync = [];
    $$('.ration-row',table).forEach(row => {
      // Keep the original button and its listeners; only change its placement.
      const lock = $('.hf119h-lock',row);
      const name = $('td:first-child',row);
      if (lock && name) {
        name.append(lock);
        // Enterprise stores this hidden field on the form, outside the row.
        const sync = () => {
          const field = row.closest('form')?.elements.namedItem('lock_'+row.dataset.itemId);
          if (field) field.value = row.dataset.locked === '1' ? '1' : '0';
          lock.setAttribute('aria-label',(row.dataset.feedName || 'Yem')+(row.dataset.locked === '1' ? ' miktar kilidini aç' : ' miktarını kilitle'));
        };
        lock.addEventListener('click',sync);
        lockSync.push(sync);
        sync();
      }
      const remove = $('.qty-zero',row);
      if (remove) {
        remove.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/></svg>';
        remove.setAttribute('aria-label',(row.dataset.feedName || 'Yem')+' rasyondan çıkar');
      }
    });
    const form = table.closest('form');
    const syncLocks = () => lockSync.forEach(sync => sync());
    form?.addEventListener('submit',syncLocks);
    form?.addEventListener('click',event => {
      if (event.target.closest('#ration-reset')) setTimeout(syncLocks,0);
    });
  }
  function reports() {
    if (path !== '/reports') return;
    const index = !params.has('tab');
    const tiles = [
      ['🐄','Sürü Raporları','Aktif, satılan, kesilen ve yaş grubu','/reports?tab=animals'],
      ['▦','Padok Özeti','Padok bazında hayvan ve rasyon','/paddocks'],
      ['♡','Sağlık Raporları','Aşı, tedavi ve bekleyen işler','/health/tasks/print?filter=all'],
      ['♀','Üreme Raporları','Tohumlama, gebelik ve doğum','/reproduction-center/print?stage=all'],
      ['₺','Finans Raporları','Gelir, gider, net ve vadeli ödemeler','/reports?tab=finance'],
      ['🌾','Yem & Stok Özeti','Stok, günlük tüketim ve yeterlilik','/feeds'],
      ['▱','Süt & Laktasyon','Günlük süt ve laktasyon verileri','/milk-center'],
      ['▥','Tarım Raporları','Tarla, ekim, hasat ve gelir-gider','/agriculture/reports']
    ];
    const hub = document.createElement('section');hub.className = 'cp-report-hub';
    hub.innerHTML = tiles.map(([symbol,name,detail,url]) => '<a class="cp-report-tile" href="'+url+'"><span style="font-size:24px;width:28px;text-align:center">'+symbol+'</span><div><b>'+name+'</b><small>'+detail+'</small></div><span>›</span></a>').join('');
    [...main.children].filter(x => !['SCRIPT','STYLE'].includes(x.tagName)).forEach(x => x.classList.add('cp-report-detail'));
    main.prepend(hub);
    document.body.classList.toggle('cp-report-index',index);
    if (!index) hub.hidden = true;
    // The legacy tab controller replaces the URL with only the tab name.
    // Retain submitted dates and animal filters when switching mobile tabs.
    const reportURL = new URL(config.request_url || location.href,location.origin);
    const keepFilters = tab => {
      if (tab) reportURL.searchParams.set('tab',tab);
      history.replaceState(null,'',reportURL.pathname+reportURL.search+reportURL.hash);
    };
    $$('[data-report-tab]',main).forEach(button => button.addEventListener('click',() => keepFilters(button.dataset.reportTab)));
    keepFilters();
  }
  home();
  if (moduleView) moduleHub();
  enhanceTables();
  herd();
  animalEntry();
  animalCards();
  if (path === '/finance') finance();
  if (path === '/paddocks') paddocks();
  if (path === '/health') {
    const cards = $$('button',main).find(button => button.textContent.trim()==='Kartlar');
    if (cards) cards.click();
  }
  if (path === '/rations') rations();
  // Enterprise queues one final layout pass after DOMContentLoaded.
  setTimeout(rationWorkbench,0);
  reports();
  // Enterprise live search replaces the main content without a navigation.
  // Reapply only the presentation to freshly returned tables and filters.
  const contentObserver = new MutationObserver(() => {
    if ($('.herd-table:not([data-cp-enhanced]),.archive-animal-table:not([data-cp-enhanced]),.mobile-animal-table:not([data-cp-enhanced]),.finance-table:not([data-cp-enhanced]),#feed-catalog-table:not([data-cp-enhanced])',main)) {
      enhanceTables();
      herd();
      const summary = $('.herd-result-summary',main);
      if (summary) subtitle.textContent = summary.textContent.trim();
    }
  });
  contentObserver.observe(main,{childList:true,subtree:true});
  function addAction(forceQuick = false) {
    if (forceQuick) return setQuick(true);
    if (path === '/finance' && typeof window.openFinanceDrawer === 'function') return window.openFinanceDrawer();
    if (path === '/health' && typeof window.toggleSectionDrawer === 'function') return window.toggleSectionDrawer('healthPlanDrawer',true);
    if (path === '/paddocks') return $('[data-open-paddock-create]')?.click();
    if (path === '/rations') return $('[data-open="rationAddDrawer"]')?.click();
    if (path === '/all-animals') return setQuick(true);
    setQuick(true);
  }
  quickButton.addEventListener('click',() => addAction());
  if (params.get('app_action') === 'add') addAction();
  if (path === '/paddocks' && params.get('app_action') === 'move') openBulkMove('');
  window.addEventListener('pageshow',event => {
    if (event.persisted) {
      $$('button[type=submit]').forEach(button => { button.disabled = false; });
      if (moduleView || taskView || path==='/') location.reload();
    }
  });
  }
  if (document.readyState === 'complete') initialize();
  else document.addEventListener('DOMContentLoaded', initialize, {once:true});
})();
