(() => {
  function mountInProfile() {
    const bar = document.querySelector('.cp-dm-rate-bar');
    const root = bar?.closest('.workbench-shell');
    if (!bar || !root) return;
    const desktop = window.matchMedia('(min-width:901px)');
    let observer;
    function place() {
      const profile = root.querySelector(desktop.matches ? '.wb2-desktop-profile' : '.wb2-mobile-profile');
      if (!profile) return false;
      if (bar.parentNode !== profile) profile.appendChild(bar);
      observer?.disconnect();
      return true;
    }
    function watch() {
      if (place()) return;
      observer?.disconnect();
      observer = new MutationObserver(place);
      observer.observe(root, { childList: true, subtree: true });
    }
    watch();
    desktop.addEventListener('change', watch);
  }
  function init() {
    mountInProfile();
    const solve = document.querySelector('#rationSolveDrawer form');
    const basisNode = document.getElementById('cpDmSolveBasis');
    if (solve && basisNode) {
      let basis = null;
      try { basis = JSON.parse(basisNode.textContent); } catch (_) {}
      if (basis) {
        for (const [name, value] of Object.entries(basis)) {
          const field = solve.elements.namedItem(name);
          if (field && name !== 'feed_ids') field.value = String(value);
        }
        const ids = new Set(basis.feed_ids || []);
        solve.querySelectorAll('input[type="checkbox"][name^="feed_"]').forEach(input => {
          input.checked = ids.has(input.name.slice(5));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
        solve.querySelector('[name="ration_type"]')?.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    document.querySelectorAll('[data-dm-rate-form], #rationSolveDrawer form').forEach(form => {
      const rate = form.querySelector('[name="target_dm_pct_bw"]');
      const weight = form.querySelector('[name="target_weight_kg"]');
      const output = form.querySelector('[data-dm-preview]');
      if (!rate || !output) return;
      const number = value => Number(String(value).replace(',', '.'));
      const fmt = value => value.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      function update() {
        const kg = number(weight ? weight.value : form.dataset.weight);
        const pct = number(rate.value);
        output.textContent = Number.isFinite(kg) && Number.isFinite(pct) && pct > 0 && pct <= 100
          ? `${kg.toLocaleString('tr-TR')} kg × %${fmt(pct)} = ${fmt(kg * pct / 100)} kg KM/gün`
          : 'Geçerli bir KM oranı girin.';
      }
      form.addEventListener('submit', event => {
        if (event.submitter?.getAttribute('formaction') === '/ration/recalculate') event.submitter.textContent = 'Hesaplanıyor…';
      });
      rate.addEventListener('input', update);
      weight?.addEventListener('input', update);
      update();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
