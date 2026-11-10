/* A transient image failure must not require a page reload. Two attempts only. */
(() => {
  'use strict';
  const states = new WeakMap();
  function failed(image) {
    if (!(image instanceof HTMLImageElement)) return;
    const source = image.getAttribute('src') || '';
    if (!source.startsWith('/photo-preview?') && !source.startsWith('/uploads/')) return;
    let state = states.get(image);
    if (!state) { state = { attempts: 0, pending: false, source }; states.set(image, state); }
    if (state.pending || state.attempts >= 2) return;
    state.pending = true;
    const attempt = ++state.attempts;
    setTimeout(() => {
      state.pending = false;
      if (!image.isConnected) return;
      // The final attempt can use the original if preview generation failed.
      const next = new URL(attempt === 2 ? image.dataset.photoOriginal || state.source : state.source, location.href);
      next.searchParams.set('cp_retry', String(attempt));
      image.src = next.pathname + next.search;
    }, attempt * 700);
  }
  document.addEventListener('error', event => failed(event.target), true);
  function scan() {
    document.querySelectorAll('img[data-photo-original]').forEach(image => {
      if (image.complete && !image.naturalWidth) failed(image);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan);
  else scan();
})();
