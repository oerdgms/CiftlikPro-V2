/* Shared search text rules; GET searches never submit a record-editing form. */
(() => {
  'use strict';
  const normalize = value => String(value ?? '').toLocaleLowerCase('tr-TR').replace(/ı/g,'i')
    .normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^\p{L}\p{N}]+/gu,' ').trim().replace(/\s+/g,' ');
  const matches = (value, query) => normalize(query).split(' ').filter(Boolean).every(word => normalize(value).includes(word));
  function syncForm(selector, doc) {
    const form=document.querySelector(selector), fresh=doc.querySelector(selector);
    if (!form || !fresh) return;
    for (const input of form.elements) {
      if (!input.name || !['INPUT','SELECT'].includes(input.tagName)) continue;
      const next=[...fresh.elements].find(item=>item.name===input.name && item.tagName===input.tagName);
      if (!next || input.value===next.value) continue;
      if (input.tagName==='SELECT' && ![...input.options].some(option=>option.value===next.value)) continue;
      input.value=next.value;
    }
  }
  function syncHerd(doc, except) {
    if (except!=='desktop') {
      const list=document.querySelector('.cp-wide-herd .cp-shared-list'), fresh=doc.querySelector('.cp-wide-herd .cp-shared-list');
      if (list && fresh) list.replaceChildren(...fresh.childNodes);
      const count=document.querySelector('.cp-wide-herd .cp-shared-result>b'), freshCount=doc.querySelector('.cp-wide-herd .cp-shared-result>b');
      if (count && freshCount) count.textContent=freshCount.textContent;
      const size=document.querySelector('.cp-herd-options>summary>small'), freshSize=doc.querySelector('.cp-herd-options>summary>small');
      if (size && freshSize) size.textContent=freshSize.textContent;
      const chips=document.querySelector('.cp-wide-herd .cp-shared-chips'), freshChips=doc.querySelector('.cp-wide-herd .cp-shared-chips');
      if (chips && freshChips) chips.replaceChildren(...freshChips.childNodes);
      syncForm('.cp-shared-filter',doc);
    }
    if (except!=='mobile') {
      const mobile=document.querySelector('.cp-ref-list'), fresh=doc.querySelector('.cp-ref-list');
      if (!mobile || !fresh) return;
      for (const selector of ['#cpRefListResults','.cp-ref-list-status','.cp-ref-chips']) {
        const current=mobile.querySelector(selector), next=fresh.querySelector(selector);
        if (current && next) current.replaceChildren(...next.childNodes);
      }
      syncForm('#cpRefHerdForm',doc);
    }
  }
  window.CPTextSearch = {normalize, matches, syncHerd};
  const states = new WeakMap(), focusKey = 'cp-live-search-focus';
  const specialized = '#cpRefHerdForm,#archiveSearchForm,#feed-catalog-search-form,.herd-filter';
  function queryInput(target) {
    if (!(target instanceof HTMLInputElement) || !['q','search','term'].includes(target.name)) return null;
    const form = target.form;
    if (!form || form.method.toLowerCase() !== 'get' || form.matches(specialized)) return null;
    return target;
  }
  function state(form) {
    if (!states.has(form)) states.set(form, {timer:0, serial:0, composing:false, request:null});
    return states.get(form);
  }
  function formURL(form) {
    const url = new URL(form.action || location.href, location.href);
    const params = new URLSearchParams();
    new FormData(form).forEach((value,key) => {if (!(value instanceof File)) params.append(key,value);});
    params.delete('page');url.search=params.toString();
    return url;
  }
  function remember(input) {
    try {sessionStorage.setItem(focusKey,JSON.stringify({path:new URL(input.form.action).pathname,name:input.name,
      value:input.value,start:input.selectionStart,end:input.selectionEnd,y:scrollY,time:Date.now()}));} catch {}
  }
  async function herdSearch(input, current) {
    const form=input.form, serial=current.serial, url=formURL(form);
    const request=new AbortController();current.request=request;input.setAttribute('aria-busy','true');
    try {
      const response=await fetch(url,{signal:request.signal,headers:{'X-Requested-With':'CiftlikPro-LiveSearch'}});
      if (response.redirected && new URL(response.url).pathname !== '/all-animals') {location.assign(response.url);return;}
      if (!response.ok) throw new Error('Search failed');
      const doc=new DOMParser().parseFromString(await response.text(),'text/html');
      if (serial!==current.serial || request.signal.aborted) return;
      const list=document.querySelector('.cp-wide-herd .cp-shared-list'), fresh=doc.querySelector('.cp-wide-herd .cp-shared-list');
      if (!list || !fresh) throw new Error('Search results missing');
      syncHerd(doc);
      history.replaceState(history.state,'',url.pathname+url.search);
    } catch(error) {
      if (error.name!=='AbortError' && serial===current.serial) {remember(input);location.assign(url);}
    } finally {if (serial===current.serial) input.removeAttribute('aria-busy');}
  }
  function run(input) {
    const form=input.form,current=state(form);clearTimeout(current.timer);
    if (current.composing || !form.checkValidity()) return;
    if (form.matches('.cp-shared-filter') && new URL(form.action).pathname==='/all-animals') return herdSearch(input,current);
    remember(input);form.requestSubmit();
  }
  function schedule(event) {
    const input=queryInput(event.target);if (!input) return;
    const current=state(input.form);clearTimeout(current.timer);++current.serial;current.request?.abort();
    if (current.composing || event.isComposing) return;
    current.timer=setTimeout(()=>run(input),350);
  }
  document.addEventListener('input',schedule,true);
  document.addEventListener('search',schedule,true);
  document.addEventListener('compositionstart',event=>{
    const input=queryInput(event.target);if (!input)return;const current=state(input.form);
    current.composing=true;clearTimeout(current.timer);++current.serial;current.request?.abort();
  },true);
  document.addEventListener('compositionend',event=>{
    const input=queryInput(event.target);if (!input)return;state(input.form).composing=false;schedule(event);
  },true);
  document.addEventListener('submit',event=>{
    const form=event.target;if (!(form instanceof HTMLFormElement) || form.method.toLowerCase()!=='get' || form.matches(specialized)) return;
    const input=[...form.elements].find(el=>queryInput(el));if (!input)return;
    const current=state(form);clearTimeout(current.timer);++current.serial;current.request?.abort();
    if (form.matches('.cp-shared-filter') && new URL(form.action).pathname==='/all-animals') {event.preventDefault();herdSearch(input,current);}
    else if (document.activeElement===input) remember(input);
  },true);
  document.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(()=>{
    try {
      const saved=JSON.parse(sessionStorage.getItem(focusKey)||'null');sessionStorage.removeItem(focusKey);
      if (!saved || saved.path!==location.pathname || Date.now()-saved.time>15000) return;
      const input=[...document.querySelectorAll('input')].find(el=>queryInput(el) && el.name===saved.name && el.value===saved.value && el.getClientRects().length);
      if (!input)return;input.focus({preventScroll:true});input.setSelectionRange(saved.start,saved.end);scrollTo(0,saved.y);
    } catch {}
  }),{once:true});
})();
