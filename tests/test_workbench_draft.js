// Execute the shipped draft script against a minimal event/DOM harness.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(require('path').join(__dirname,'../app/server.py'),'utf8');
const script=source.split('HOTFIX122AH_DRAFT=r"""')[1].split('"""')[0].replace(/<\/?script>/g,'');
const storage=new Map();
function load({rid='1',items,selected='3',quantity='0.5',fail=false}){
 const listeners={},locks={},rows=items.map((item,i)=>{
  const input={value:item.value,dataset:{original:item.value},dispatchEvent(){}};
  const row={dataset:{itemId:String(i+1),feedId:item.feed,locked:item.lock||'0'},querySelector(s){return s==='.ration-qty'?input:{click(){locks['lock_'+(i+1)].value=locks['lock_'+(i+1)].value==='1'?'0':'1';}};}};
  locks['lock_'+(i+1)]={value:item.lock||'0'};return row;
 });
 const add={querySelector(s){return{value:s.includes('feed_id')?selected:quantity}},checkValidity(){return true},addEventListener(t,f){listeners[t]=f;}};
 const form={querySelector(s){if(s.includes('ration_id'))return{value:rid};return locks[s.match(/name="([^"]+)/)[1]]},querySelectorAll(){return rows},prepend(){}};
 const quick={value:''},buttons=items.map(item=>({dataset:{feedId:item.feed},addEventListener(t,f){this.click=f}}));
 const document={body:{dataset:{draftUser:'admin'}},readyState:'complete',getElementById(id){return id==='ration-bulk-form'?form:id==='quick-feed-form'?add:quick},querySelectorAll(){return buttons},createElement(){return{};}};
 vm.runInNewContext(script,{document,requestAnimationFrame:f=>f(),sessionStorage:{setItem(k,v){if(fail)throw Error('blocked');storage.set(k,v)},getItem:k=>storage.get(k),removeItem:k=>storage.delete(k)},Event:class{},alert(){},Date,Number,Array,JSON,Math});
 return {rows,locks,buttons,quick,submit(){let prevented=false;listeners.submit({defaultPrevented:false,preventDefault(){prevented=true},stopImmediatePropagation(){}});return prevented;}};
}
let page=load({items:[{feed:'1',value:'1'},{feed:'2',value:'1'}]});
page.rows[0].querySelector('.ration-qty').value='2.75';page.rows[1].querySelector('.ration-qty').value='0';page.locks.lock_1.value='1';
page.buttons[0].click();assert.equal(page.quick.value,'2.75');assert.equal(page.submit(),false);
page=load({items:[{feed:'1',value:'1'},{feed:'2',value:'1'},{feed:'3',value:'0.5'}]});
assert.equal(page.rows[0].querySelector('.ration-qty').value,'2.75');assert.equal(page.rows[1].querySelector('.ration-qty').value,'0');assert.equal(page.locks.lock_1.value,'1');assert.equal(storage.size,0);
// Existing feed update wins for that feed, while other draft amounts survive.
page=load({items:[{feed:'1',value:'1'},{feed:'2',value:'1'}],selected:'1',quantity:'4'});page.rows[0].querySelector('.ration-qty').value='2';page.rows[1].querySelector('.ration-qty').value='3';page.submit();
page=load({items:[{feed:'1',value:'4'},{feed:'2',value:'1'}]});assert.equal(page.rows[0].querySelector('.ration-qty').value,'4');assert.equal(page.rows[1].querySelector('.ration-qty').value,'3');
// Failed update keeps the draft; another ration cannot inherit it.
page=load({items:[{feed:'1',value:'1'}],selected:'1',quantity:'4'});page.rows[0].querySelector('.ration-qty').value='2';page.submit();
const other=load({rid:'2',items:[{feed:'1',value:'1'}]});assert.equal(other.rows[0].querySelector('.ration-qty').value,'1');
page=load({items:[{feed:'1',value:'1'}]});assert.equal(page.rows[0].querySelector('.ration-qty').value,'2');
assert.equal(load({items:[{feed:'1',value:'1'}],fail:true}).submit(),true);
console.log('Draft preservation, locks, zero removal, same-feed update, rejected update, ration isolation, and storage failure: OK');
