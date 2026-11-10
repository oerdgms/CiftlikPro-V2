/* Upload and preview in the same application window; no business record is saved here. */
(() => {
 'use strict';
 if(location.pathname==='/animals/import-preview'){
  const top=()=>window.scrollTo({top:0,left:0,behavior:'instant'});
  window.addEventListener('pageshow',event=>{if(!event.persisted)top();},{once:true});
  requestAnimationFrame(top);
  return;
 }
 const form=document.querySelector('[data-animal-import-form]');if(!form)return;
 const button=form.querySelector('[data-import-submit]'),status=form.querySelector('[data-import-status]');
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(button.disabled||!form.reportValidity())return;
  const file=form.querySelector('[name=animal_file]').files[0];
  if(file.size>12*1024*1024){status.textContent='Dosya 12 MB sınırını aşıyor.';return;}
  button.disabled=true;button.textContent='Dosya okunuyor…';status.textContent='Dosya yükleniyor ve önizleme hazırlanıyor. Bu aşamada kayıt aktarılmaz.';
  try {
   const response=await fetch(form.action,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'},credentials:'same-origin'});
   const type=response.headers.get('Content-Type')||'';
   if(!type.includes('application/json'))throw Error('Oturum veya bağlantı doğrulanamadı. Tekrar giriş yapıp deneyin.');
   const result=await response.json();
   if(!response.ok||!result.ok)throw Error(result.message||'Dosya okunamadı.');
   const next=new URL(result.redirect,location.href);
   if(next.origin!==location.origin)throw Error('Önizleme adresi doğrulanamadı.');
   location.assign(next.href);
  }catch(error){
   status.textContent=error.message==='Failed to fetch'?'Bağlantı kesildi. Dosya seçiminiz korunuyor; bağlantı gelince yeniden deneyin.':error.message;
   button.disabled=false;button.textContent='Dosyayı Oku ve Önizle';
  }
 });
})();
