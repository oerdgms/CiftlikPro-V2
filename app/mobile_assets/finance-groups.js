/* Read-only filtering within one health expense; financial totals stay fixed. */
(() => {
  const initialize = () => {
    const input = document.querySelector('[data-finance-member-search]');
    if (!input || input.dataset.bound) return;
    input.dataset.bound = '1';
    const rows = [...document.querySelectorAll('[data-finance-member]')];
    const count = document.querySelector('[data-finance-member-count]');
    const empty = document.querySelector('[data-finance-members-empty]');
    input.addEventListener('input', () => {
      let visible = 0;
      for (const row of rows) {
        row.hidden = !CPTextSearch.matches(row.dataset.search, input.value);
        if (!row.hidden) visible++;
      }
      count.textContent = visible === rows.length ? rows.length + ' hayvan' : visible + ' / ' + rows.length + ' hayvan';
      empty.hidden = visible > 0;
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once:true});
  else initialize();
})();
