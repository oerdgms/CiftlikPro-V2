const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(require('path').join(__dirname,'../app/server.py'),'utf8');
const js=source.split('HOTFIX122AJ_AGENDA=r"""')[1].split('"""')[0].match(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/)[1];
assert(js.includes("toggle.type='button'"));
assert(js.includes("toggle.setAttribute('aria-expanded','false')"));
assert(js.includes('controls.hidden=true'));
assert(js.includes('event.stopPropagation()'));
assert(!js.includes("document.createElement('details')"));
class El{
 constructor(){this.children=[];this.dataset={};this.style={};this.events={};this.attrs={};this.className='';this.hidden=false;const self=this;this.classList={contains(n){return self.className.split(/\s+/).includes(n)},toggle(n,on){const names=new Set(self.className.split(/\s+/).filter(Boolean)),next=on===undefined?!names.has(n):!!on;if(next)names.add(n);else names.delete(n);self.className=[...names].join(' ');return next}};}
 append(...els){els.forEach(e=>{if(e.parent)e.parent.children=e.parent.children.filter(x=>x!==e);this.children.push(e);e.parent=this})}
 before(e){this.parent.append(e)}
 replaceChildren(){this.children.forEach(e=>e.parent=null);this.children=[]}
 setAttribute(k,v){this.attrs[k]=v}
 addEventListener(k,f){this.events[k]=f}
 querySelector(selector){const match=e=>selector.startsWith('.')&&e.classList.contains(selector.slice(1));for(const child of this.children){if(match(child))return child;const nested=child.querySelector(selector);if(nested)return nested}return null}
 closest(selector){for(let cur=this;cur;cur=cur.parent)if(selector.startsWith('.')&&cur.classList.contains(selector.slice(1)))return cur;return null}
 contains(target){for(let cur=target;cur;cur=cur.parent)if(cur===this)return true;return false}
}
const storage=new Map();let notify;
function load(user='admin'){
 const host=new El(),list=new El(),documentEvents={};list.className='health-plan-list';host.append(list);let cards=['2026-10-04','2026-10-02','2026-10-04'].map(d=>{const c=new El();c.className='health-plan-card';c.dataset.healthDate=d;const a=new El(),controls=new El();a.className='health-plan-action';controls.className='health-plan-controls';c.controls=controls;c.append(a);a.append(controls);return c});list.append(...cards);
 list.querySelectorAll=()=>cards;
 const all=()=>{const result=[];function walk(el){result.push(el);el.children.forEach(walk)}walk(host);return result};
 const document={readyState:'complete',body:{dataset:{healthUser:user}},querySelector:()=>list,querySelectorAll:selector=>selector==='.health-more.open'?all().filter(e=>e.classList.contains('health-more')&&e.classList.contains('open')):[],createElement:()=>new El(),addEventListener(k,f){documentEvents[k]=f}};
 vm.runInNewContext(js,{document,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},MutationObserver:class{constructor(f){notify=f}observe(){}},Date,Map,Array,String,Number});
 return{host,list,cards,documentEvents,switcher:host.children.find(e=>e.className==='health-view-switch')};
}
let p=load();assert.equal(p.list.children.length,2);assert.equal(p.list.children[0].children[1].children[0].dataset.healthDate,'2026-10-02');assert.equal(p.list.children[1].children[1].children.length,2);
// Existing controls remain the same elements inside disclosure menus.
assert.equal(p.cards[0].controls.parent.className,'health-more');
const menu=p.cards[0].controls.parent,toggle=menu.children[0];
assert.equal(p.cards[0].controls.hidden,true);assert.equal(toggle.attrs['aria-expanded'],'false');
toggle.events.click({preventDefault(){},stopPropagation(){}});assert(menu.classList.contains('open'));assert.equal(p.cards[0].controls.hidden,false);assert.equal(toggle.attrs['aria-expanded'],'true');
p.documentEvents.click({target:p.host});assert(!menu.classList.contains('open'));assert.equal(p.cards[0].controls.hidden,true);
toggle.events.click({preventDefault(){},stopPropagation(){}});p.documentEvents.keydown({key:'Escape'});assert(!menu.classList.contains('open'));
p.cards.filter(c=>c.dataset.healthDate==='2026-10-04').forEach(c=>c.style.display='none');notify();assert.equal(p.list.children[1].hidden,true);
p.switcher.children[1].events.click();assert.equal(p.list.children.length,3);assert.equal(p.list.children[0],p.cards[0]);
p=load();assert.equal(p.list.children.length,3);p=load('other');assert.equal(p.list.children.length,2);
p.switcher.children[1].events.click();p.switcher.children[0].events.click();assert.equal(p.list.children.length,2);
console.log('Agenda date ordering/grouping, filter visibility, preserved controls, view switching and user preference isolation: OK');
