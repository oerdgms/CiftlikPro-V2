/* Installation and update UI only. No offline record store or replay queue. */
(() => {
  'use strict';
  let promptEvent = null, registration = null, registrationError = false;
  let dirty = false, updateAvailable = false, previousFocus = null;
  const standalone = () => matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  const ios = () => /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); promptEvent = event; refresh();
  });
  window.addEventListener('appinstalled', () => { promptEvent = null; refresh(true); });
  function refresh(installed = false) {
    const state = document.querySelector('#cpPwaStatus');
    const action = document.querySelector('#cpPwaInstall');
    if (!state || !action) return;
    const added = installed || standalone();
    state.textContent = added ? 'Ana ekran uygulaması açık / yükleme tamamlandı.' : !isSecureContext
      ? 'Tam PWA desteği için bu sayfayı HTTPS adresinden açın. Mevcut HTTP adresinde normal kullanım devam eder.'
      : registrationError ? 'Çevrimdışı ekran hazırlanamadı. Bağlantıyı kontrol edip sayfayı yeniden açın.'
      : registration?.active ? 'Güvenli bağlantı ve çevrimdışı bağlantı ekranı hazır.' : 'Güvenli bağlantı hazır. Ana ekrana ekleyebilirsiniz.';
    action.hidden = added || !promptEvent || !isSecureContext;
    const guide = document.querySelector('#cpPwaGuide');
    guide.textContent = added ? 'Çiftlik sunucusu açık ve ağ / VPN bağlantısı etkin olmalıdır.'
      : ios() ? 'iPhone / iPad: Safari’de Paylaş → Ana Ekrana Ekle. Sunuluyorsa “Web Uygulaması Olarak Aç” seçeneğini açık tutun.'
      : 'Android: Chrome menüsü → Uygulamayı yükle / Ana ekrana ekle. Bilgisayarda tarayıcının yükleme simgesini kullanabilirsiniz.';
    document.querySelectorAll('[data-cp-pwa-open]').forEach(button => {
      button.hidden = false;
      button.textContent = added ? 'Uygulama ve güncellemeler' : 'Ana ekrana ekle';
    });
  }
  function init() {
    const config = document.querySelector('#cpAppConfig');
    if (!config) return;
    const build = JSON.parse(config.textContent).build;
    const dialog = document.createElement('dialog');
    dialog.id = 'cpPwaDialog'; dialog.className = 'cp-pwa-dialog';
    dialog.setAttribute('aria-labelledby','cpPwaTitle');
    dialog.innerHTML = '<div class="cp-pwa-heading"><img src="/app-assets/icon-192.png" width="48" height="48" alt=""><div><h2 id="cpPwaTitle">ÇiftlikPro uygulaması</h2><small>Ana ekrandan hızlı erişim</small></div><button type="button" id="cpPwaClose" aria-label="Kapat">×</button></div><p id="cpPwaStatus" role="status"></p><p id="cpPwaGuide"></p><button type="button" id="cpPwaInstall" hidden>Uygulamayı yükle</button><details id="cpPwaHttps"><summary>HTTPS bağlantısını hazırlama</summary><p>Çiftlik bilgisayarında Tailscale Serve ile HTTPS adresi oluşturabilirsiniz. Kurulum paketindeki PWA_KURULUM.md dosyasını izleyin. Telefonda bu yeni adresi kullanın; Tailscale bağlantısı açık kalmalı.</p></details><p class="cp-pwa-note">Bağlantı kesildiğinde yeniden bağlanma ekranı gösterilir. Kayıtları görüntülemek ve kaydetmek için çiftlik sunucusuna bağlantı gerekir.</p><div class="cp-pwa-update"><button type="button" id="cpPwaCheck">Güncellemeyi kontrol et</button><button type="button" id="cpPwaReload" hidden>Yeni sürümü aç</button><p id="cpPwaUpdateStatus" role="status" aria-live="polite"></p></div><small id="cpPwaBuild"></small>';
    document.body.append(dialog);
    document.querySelector('#cpPwaBuild').textContent = build;
    const menu = document.querySelector('#cpRefMenu');
    if (menu && !menu.querySelector('[data-cp-pwa-open]')) {
      const button = document.createElement('button'); button.type = 'button';
      button.className = 'cp-pwa-entry'; button.dataset.cpPwaOpen = '';
      menu.insertBefore(button,menu.querySelector('.cp-ref-logout'));
    }
    document.addEventListener('click', event => {
      if (!event.target.closest('[data-cp-pwa-open]')) return;
      event.preventDefault(); previousFocus = document.activeElement;
      if (menu?.contains(previousFocus)) {
        document.querySelector('#cpCloseMenu')?.click();
        previousFocus = document.querySelector('#cpOpenMenu');
      }
      refresh(); if (!dialog.open) dialog.showModal();
    });
    document.querySelector('#cpPwaClose').addEventListener('click',() => dialog.close());
    dialog.addEventListener('close',() => previousFocus?.focus());
    document.querySelector('#cpPwaInstall').addEventListener('click',async () => {
      if (!promptEvent) return;
      const event = promptEvent; promptEvent = null;
      try { await event.prompt(); const choice = await event.userChoice; refresh(choice.outcome === 'accepted'); }
      catch (_) { refresh(); }
    });
    const markDirty = event => { if (!dialog.contains(event.target) && event.target.closest('form')) dirty = true; };
    document.addEventListener('input', markDirty);
    document.addEventListener('change', markDirty);
    document.querySelector('#cpPwaCheck').addEventListener('click',async () => {
      const button = document.querySelector('#cpPwaCheck'), status = document.querySelector('#cpPwaUpdateStatus');
      button.disabled = true; status.textContent = 'Kontrol ediliyor…';
      const controller = new AbortController(), timeout = setTimeout(() => controller.abort(),6000);
      try {
        const response = await fetch('/app-build.json',{cache:'no-store',signal:controller.signal});
        if (!response.ok) throw Error('unreachable');
        const metadata = await response.json();
        if (metadata.app !== 'CiftlikPro' || !metadata.build) throw Error('invalid');
        updateAvailable = metadata.build !== build;
        status.textContent = updateAvailable ? 'Yeni sürüm hazır. Kaydedilmemiş değişikliklerinizi kaydettikten sonra açın.' : 'Güncel sürümü kullanıyorsunuz.';
        document.querySelector('#cpPwaReload').hidden = !updateAvailable;
        // Do not tie the bounded server probe to the worker update network request.
        registration?.update().catch(() => {});
      } catch (_) { status.textContent = 'Sunucuya ulaşılamadı. Ağ / VPN bağlantısını kontrol edin.'; }
      finally { clearTimeout(timeout); button.disabled = false; }
    });
    document.querySelector('#cpPwaReload').addEventListener('click',() => {
      if (!updateAvailable) return;
      if (dirty && !window.confirm('Bu sayfada değişiklik yaptınız. Kaydedilmeyen bilgiler kaybolabilir. Yeni sürüm açılsın mı?')) return;
      location.reload();
    });
    if ('serviceWorker' in navigator && isSecureContext) {
      navigator.serviceWorker.register('/app-service-worker.js',{scope:'/',updateViaCache:'none'})
        .then(value => { registration = value; registration.addEventListener('updatefound',() => {
          const worker = registration.installing;
          worker?.addEventListener('statechange',() => { if (worker.state === 'activated') refresh(); });
        }); refresh(); })
        .catch(() => { registrationError = true; refresh(); });
      // Activation never reloads an open form.
      navigator.serviceWorker.addEventListener('controllerchange',() => refresh());
    }
    matchMedia('(display-mode: standalone)').addEventListener('change',() => refresh());
    refresh();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
