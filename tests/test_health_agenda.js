const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(require('path').join(__dirname,'../app/server.py'),'utf8');
const js=source.split('HOTFIX122AJ_AGENDA=r"""')[1].split('"""')[0].match(/<script>([\s\S]*?)<\/script>/)[1];
class El{
 constructor(){this.children=[];this.dataset={};this.style={};this.events={};this.attrs={};this.classList={toggle(){}};}
 append(...els){els.forEach(e=>{if(e.parent)e.parent.children=e.parent.children.filter(x=>x!==e);this.children.push(e);e.parent=this})}
 before(e){this.parent.append(e)}
 replaceChildren(){this.children.forEach(e=>e.parent=null);this.children=[]}
 setAttribute(k,v){this.attrs[k]=v}
 addEventListener(k,f){this.events[k]=f}
 querySelector(){return this.controls||null}
}
const storage=new Map();let notify;
function load(user='admin'){
 const host=new El(),list=new El();host.append(list);let cards=['2026-10-04','2026-10-02','2026-10-04'].map(d=>{const c=new El();c.dataset.healthDate=d;const a=new El(),controls=new El();c.controls=controls;c.append(a);a.append(controls);return c});list.append(...cards);
 list.querySelectorAll=()=>cards;
 const document={readyState:'complete',body:{dataset:{healthUser:user}},querySelector:()=>list,querySelectorAll:()=>[],createElement:()=>new El(),addEventListener(){}};
 vm.runInNewContext(js,{document,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},MutationObserver:class{constructor(f){notify=f}observe(){}},Date,Map,Array,String,Number});
 return{list,cards,switcher:host.children.find(e=>e.className==='health-view-switch')};
}
let p=load();assert.equal(p.list.children.length,2);assert.equal(p.list.children[0].children[1].children[0].dataset.healthDate,'2026-10-02');assert.equal(p.list.children[1].children[1].children.length,2);
// Existing controls remain the same elements inside disclosure menus.
assert.equal(p.cards[0].controls.parent.className,'health-more');
p.cards.filter(c=>c.dataset.healthDate==='2026-10-04').forEach(c=>c.style.display='none');notify();assert.equal(p.list.children[1].hidden,true);
p.switcher.children[1].events.click();assert.equal(p.list.children.length,3);assert.equal(p.list.children[0],p.cards[0]);
p=load();assert.equal(p.list.children.length,3);p=load('other');assert.equal(p.list.children.length,2);
p.switcher.children[1].events.click();p.switcher.children[0].events.click();assert.equal(p.list.children.length,2);
console.log('Agenda date ordering/grouping, filter visibility, preserved controls, view switching and user preference isolation: OK');
