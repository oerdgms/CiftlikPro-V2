/* Keep each tab, form and AJAX request bound to the enterprise that rendered it. */
(() => {
 'use strict';
 const node=document.getElementById('cpEnterpriseConfig');if(!node)return;
 const farm=JSON.parse(node.textContent).id;
 const skip=u=>u.origin!==location.origin||u.pathname.startsWith('/app-assets/')||['/app-manifest.json','/app-service-worker.js','/app-build.json','/login','/forgot-password','/forgot-verify','/forgot-reset','/license','/app-install'].includes(u.pathname);
 function scoped(value){const u=new URL(value,location.href);if(!skip(u)&&!u.searchParams.has('farm'))u.searchParams.set('farm',farm);return u;}
 const nativeFetch=window.fetch.bind(window);
 window.fetch=(input,init)=>{
  const value=input instanceof Request?input.url:input;
  const u=new URL(value,location.href);
  if(skip(u))return nativeFetch(input,init);
  const options={...init,headers:new Headers(init?.headers||(input instanceof Request?input.headers:undefined))};
  options.headers.set('X-CiftlikPro-Farm',farm);
  return nativeFetch(input instanceof Request?input:scoped(value).href,options);
 };
 const open=XMLHttpRequest.prototype.open;
 XMLHttpRequest.prototype.open=function(method,url,...args){return open.call(this,method,scoped(url).href,...args)};
 function formScope(form){
  const url=scoped(form.getAttribute('action')||location.href);form.action=url.href;
  if(url.origin!==location.origin||skip(url))return;
  form.querySelectorAll('[formaction]').forEach(button=>{button.setAttribute('formaction',scoped(button.getAttribute('formaction')).href);});
  let field=form.querySelector('input[name="farm"]');
  if(!field){field=document.createElement('input');field.type='hidden';field.name='farm';form.appendChild(field);}
  field.value=url.searchParams.get('farm')||farm;
 }
 document.addEventListener('submit',event=>{if(event.target instanceof HTMLFormElement)formScope(event.target);},true);
 const submit=HTMLFormElement.prototype.submit;
 HTMLFormElement.prototype.submit=function(){formScope(this);return submit.call(this)};
 document.addEventListener('click',event=>{
  const a=event.target.closest('a[href]');if(!a||a.getAttribute('href').startsWith('#'))return;
  a.href=scoped(a.href).href;
 },true);
 function start(){
  document.querySelectorAll('form').forEach(formScope);
  const form=document.querySelector('.cp-enterprises');
  if(form)form.addEventListener('click',event=>{
   const button=event.target.closest('button[type="submit"],button:not([type])');
   if(!button)return;
   const dirty=[...document.querySelectorAll('form')].some(f=>f.dataset.cpDirty==='1');
   if(dirty&&button.form?.action.includes('/farms/switch')&&!confirm('Kaydedilmemiş değişiklikler olabilir. İşletme değiştirilsin mi?'))event.preventDefault();
  });
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
