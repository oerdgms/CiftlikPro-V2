"""Shared module directory, herd workflows and manual dairy presentation."""
import re
from collections import defaultdict
from datetime import date, timedelta
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urlparse

import dairy_management as dairy
from text_search import matches as search_matches
import home_layout
import mobile_reference as ref

esc=ref.esc
MODULES = [
    ('ration','Rasyon','/rations','blue'),('paddocks','Padoklar','/paddocks','blue'),
    ('shield','Sağlık Yönetimi','/health','green'),('heart','Üreme','/reproduction-center','pink'),
    ('finance','Finans','/finance','orange'),('feeds','Yem & Stok','/feeds','blue'),
    ('jobs','Görevler','/?app_view=tasks','green'),('reports','Raporlar','/reports','blue'),
    ('settings','Ayarlar','/farm-profile','blue'),('milk','Süt & Laktasyon','/milk-center','blue'),
    ('farm','Tarım Yönetimi','/agriculture','green'),
    ('animals','Hayvan Arşivi','/archive/sold','orange'),('settings','Veri & Yedekleme','/backups','purple')]


def modules_markup(icon):
    tiles=''.join(f'<a href="{url}" class="cp-module-tile"><span class="cp-module-icon cp-module-{tone}">{ref.glyph(kind,icon)}</span><b>{label}</b></a>' for kind,label,url,tone in MODULES)
    return '<section class="cp-module-directory cp-ref-modules" id="cpModuleDirectory"><header class="cp-shared-head"><div><h1>Modüller</h1><p>Tüm işlemler tek ekranda.</p></div></header><div class="cp-module-grid">'+tiles+'</div><button class="cp-ref-install" id="cpInstall" hidden>Ana ekrana yükle</button></section>'


def summary(ns, username):
    with ns['db']() as c:
        cards=ref.summary_cards(ns['dashboard_herd_counts'](c),ref.herd_records(ns,c))
    config=home_layout.load(ns,username);lookup={card['key']:card for card in cards}
    tiles=''.join(f'<a class="cp-shared-stat cp-bg-{lookup[key]["tone"]}" href="{esc(lookup[key]["url"])}"><span>{esc(lookup[key]["label"])}</span><b>{lookup[key]["count"]}</b></a>' for key in config['cards'])
    return '<section class="cp-wide-only cp-shared-summary"><header class="cp-shared-head"><h2>Sürü Özeti</h2></header><div class="cp-shared-stats">'+tiles+'</div></section>'


def _element_end(markup, tag, class_name):
    """Locate the complete KPI element, including nested classic card divs."""
    offsets = [0]
    for line in markup.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    class Slot(HTMLParser):
        depth = 0
        end = None
        def handle_starttag(self, name, attrs):
            if self.end is not None or name != tag:
                return
            if self.depth:
                self.depth += 1
            elif class_name in (dict(attrs).get('class') or '').split():
                self.depth = 1
        def handle_endtag(self, name):
            if self.end is not None or name != tag or not self.depth:
                return
            self.depth -= 1
            if not self.depth:
                line, column = self.getpos()
                self.end = markup.index('>', offsets[line - 1] + column) + 1
    slot = Slot()
    slot.feed(markup)
    return slot.end


def home_body(ns, body, username, icon):
    """Render greeting, totals and herd summary in order before first paint."""
    settings = ('<a class="cp-desktop-home-settings" href="/home-layout" '
                'aria-label="Ana Sayfa Düzeni" title="Ana Sayfa Düzeni">'
                + icon('settings') + '<span>Ana Sayfayı Düzenle</span></a>')
    body = body.replace('<div class="v122k-dashboard-tools">', settings + '<div class="v122k-dashboard-tools">', 1)
    herd = summary(ns, username)
    end = _element_end(body, 'section', 'v117-kpis') or _element_end(body, 'div', 'summary-grid')
    if end is not None:
        return body[:end] + herd + body[end:]
    return body + herd


def desktop_navigation(document, path, icon):
    """Keep the module directory available beside the configurable shortcuts."""
    marker = '<a data-qid="reports"'
    if marker not in document:
        return document
    current = ' aria-current="page"' if path == '/modules' else ''
    badge = ('<a class="cp-desktop-modules-badge" href="/modules"' + current + '>'
             + icon('modules') + '<span>Modüller</span></a>')
    return document.replace(marker, badge + marker, 1)


def herd_markup(ns, request_url, username='admin'):
    view=ref.herd_selection(ns,request_url)
    link=view['link'];selected=view['selected'];page=view['page'];size=view['size']
    def options(values,current):
        return ''.join(f'<option value="{esc(key)}" {"selected" if key==current else ""}>{esc(label)}</option>' for key,label in values)
    kinds=options([('all','Tüm hayvanlar'),('female','Dişi'),('male','Erkek'),('calf','Buzağı')],view['kind'])
    groups=options([('','Tüm durumlar'),('lactating','Sağmal / Laktasyonda'),('dry','Kuru'),('heifer','Düve'),('pregnant','Gebe'),('heat','Kızgın')],view['group'])
    pads=options([('','Tüm padoklar')]+[(p,p) for p in view['paddocks']],view['pad'])
    sort=options([('animal','Küpe no'),('age','Yaş'),('breed','Irk'),('paddock','Padok'),('status','Durum')],view['sort'])
    direction=options([('asc','Artan'),('desc','Azalan')],'desc' if view['reverse'] else 'asc')
    sizes=options([(str(n),str(n)+' kayıt') for n in (10,15,30)],str(size))
    chips=''.join(f'<a class="{"active" if view["group"]==key else ""}" href="{esc(link(group=key,page=1))}">{label}</a>' for key,label in [('','Tümü'),('lactating','Sağmal'),('dry','Kuru'),('heifer','Düve'),('pregnant','Gebe'),('heat','Kızgın')])
    rows=''
    for r in selected[(page-1)*size:page*size]:
        source=r['source'];sid=r['id'];url=('/animal' if source=='animal' else '/calf')+'?id='+str(sid)
        management=f'<a class="cp-shared-state-link" data-cp-state-url href="/animal-events?source={source}&amp;id={sid}" aria-haspopup="dialog" aria-label="{esc(r["tag"])} için durum ekle"><span aria-hidden="true">＋</span> Durum Ekle</a>'
        identity=f'<div class="herd-animal-cardhead"><a class="herd-photo" href="{url}">{ref.photo(r["list_photo"],r["tag"],False)}</a><div class="herd-identity"><a class="animal-tag-btn" href="{url}">{esc(r["tag"])}</a><div class="herd-animal-name">{esc(r.get("nickname"))}</div><div class="cp-shared-badges" data-dairy-status="{esc(r["dairy_status"])}">{ref.badges(r)}</div></div></div>'
        actions=f'<div class="cp-shared-actions cp-shared-row-actions"><a class="btn alt" href="{url}">Görüntüle</a><a class="btn alt" href="/{source}-edit?id={sid}">Düzenle</a><form method="post" action="/{source}-delete" onsubmit="return confirm(\'Bu hayvan ve bağlı kayıtları kalıcı olarak silinsin mi?\')"><input type="hidden" name="id" value="{sid}"><button class="btn red">Sil</button></form></div>'
        rows+=f'<tr><td data-label="Hayvan">{identity}</td><td data-label="Tür">{esc("Buzağı" if source=="calf" else r["gender"])}</td><td data-label="Irk">{esc(r.get("breed") or "—")}</td><td data-label="Padok">{esc(r.get("paddock") or "Padoksuz")}</td><td data-label="Yaş">{esc(ns["age_text"](r.get("birth_date")))}</td><td data-label="Durum"><div class="cp-shared-status"><div class="cp-shared-badges">{ref.badges(r)}</div>{management}</div></td><td data-label="İşlemler">{actions}</td></tr>'
    rows=rows or '<tr><td colspan="7">Filtrelerine uygun hayvan bulunamadı.</td></tr>'
    pager=(f'<a class="btn alt" href="{esc(link(page=page-1))}">‹ Önceki</a>' if page>1 else '')+f'<span>Sayfa {page} / {view["pages"]}</span>'+(f'<a class="btn alt" href="{esc(link(page=page+1))}">Sonraki ›</a>' if page<view['pages'] else '')
    modes=''.join(f'<button type="button" data-herd-view-button="{key}" class="herd-view-button" aria-pressed="{str(ns["herd_view"](username)==key).lower()}">{label}</button>' for key,label in [('details','Ayrıntı'),('cards','Kart'),('compact','Kompakt')])
    return f'''<section class="cp-wide-herd cp-wide-only"><header class="cp-shared-head"><div><h1>Sürü Merkezi</h1><p>Laktasyon durumu, fotoğraflar ve hayvan işlemleri.</p></div><div class="cp-shared-actions"><a class="btn" href="/animal-add">＋ Hayvan Ekle</a><a class="btn alt" href="/dairy-status">Laktasyon Belirle</a><a class="btn alt" href="/reports#animal-report">Rapor Al</a></div></header><nav class="cp-shared-chips">{chips}</nav><form class="card cp-shared-filter" method="get" action="/all-animals"><label class="cp-shared-search">Hayvan ara<input type="search" name="q" value="{esc(view['term'])}" placeholder="Küpe, ad, ırk veya padok"></label><label>Tür<select name="kind">{kinds}</select></label><label>Durum<select name="group">{groups}</select></label><label>Padok<select name="paddock">{pads}</select></label><label>Sıralama<select name="sort">{sort}</select></label><label>Sıra<select name="dir">{direction}</select></label><label>Göster<select name="per_page">{sizes}</select></label><div class="cp-shared-filter-actions"><button class="btn">Filtrele</button><a class="btn alt" href="/all-animals">Temizle</a></div></form><div class="cp-shared-result"><b role="status">{len(selected)} hayvan</b><div class="herd-view-switch">{modes}</div><nav class="cp-shared-actions"><a href="/archive/sold">Satılan</a><a href="/archive/slaughtered">Kesilen</a><a href="/archive/lost">Ölen / Kayıp</a></nav></div><section class="card cp-shared-list"><div class="cp-shared-table-scroll"><table class="herd-table cp-shared-herd-table"><thead><tr><th>Hayvan</th><th>Tür</th><th>Irk</th><th>Padok</th><th>Yaş</th><th>Durum</th><th>İşlemler</th></tr></thead><tbody>{rows}</tbody></table></div><nav class="cp-shared-pagination">{pager}</nav></section></section>'''


def milk_summary(c, animal, statuses=None):
    state=dairy.current_status(c,animal,statuses)
    today=date.today();daily=defaultdict(float)
    for row in c.execute('select measure_date,liters from milk where animal_id=? and measure_date<=?',(animal['id'],today.isoformat())):
        daily[row['measure_date']]+=float(row['liters'] or 0)
    def average(days):
        cutoff=(today-timedelta(days=days-1)).isoformat()
        values=[value for stamp,value in daily.items() if stamp>=cutoff]
        return sum(values)/len(values) if values else 0
    total=sum(value for stamp,value in daily.items() if stamp>=state['lactation_start']) if state['status']=='lactating' and state.get('lactation_start') else None
    return dict(state=state,today=daily.get(today.isoformat(),0),avg7=average(7),avg30=average(30),total=total,
        projected305=total/max(1,state['dim']+1)*305 if total is not None and state['dim'] is not None else None)


def dairy_card(ns, animal, summary, active=True):
    state=summary['state'];fmt=ns['fmt_date']
    values=[('Laktasyon Durumu',state['label']),('Başlangıç',fmt(state.get('lactation_start'))),('Laktasyon Sırası',state.get('lactation_number')),('Sağım Günü',str(state['dim'])+' gün' if state['dim'] is not None else None)]
    sid=str(animal['id'])
    actions='<div class="cp-shared-actions"><a class="btn" data-cp-state-url aria-haspopup="dialog" href="/animal-events?source=animal&amp;id='+sid+'">＋ Durum Ekle</a><a class="btn alt" data-cp-state-url aria-haspopup="dialog" href="/animal-events?source=animal&amp;id='+sid+'&amp;event=birth">Doğum Ekle</a></div>' if active else ''
    return '<section class="card cp-wide-only cp-wide-dairy"><header class="cp-shared-head"><h2>Laktasyon Durumu</h2>'+actions+'</header>'+ref.keyvalues(values)+'</section>'


def animal_document(ns, document, aid):
    with ns['db']() as c:
        animal=c.execute('select * from animals where id=?',(aid,)).fetchone()
        if not animal or animal['gender']!='Dişi':return document
        summary=milk_summary(c,animal)
        active=(animal['status'] or 'Aktif')=='Aktif' and not c.execute('select 1 from animal_losses where animal_id=?',(aid,)).fetchone()
    state=summary['state']
    metrics=[('Laktasyon Günü',str(state['dim'])+' gün' if state['dim'] is not None else '—'),('Bugün',f'{summary["today"]:.1f} L'),('7 Gün Ort.',f'{summary["avg7"]:.1f} L'),('Laktasyon Toplamı',f'{summary["total"]:.0f} L' if summary['total'] is not None else '—'),('305 Gün Tahmini',f'{summary["projected305"]:.0f} L' if summary['projected305'] is not None else '—')]
    metric_html='<div class="quick-metrics">'+''.join('<span class="pill">'+label+'<br><b>'+value+'</b></span>' for label,value in metrics)+'</div>'
    document=re.sub(r"<div class='quick-metrics'>.*?</div>",lambda m:metric_html if 'Laktasyon Günü' in m.group() else m.group(),document,flags=re.S)
    document=document.replace('DIM ve performans doğum/süt kayıtlarından otomatik hesaplanır.','Laktasyon durumu elle belirlenir. Başlangıç bilinmiyorsa sağım günü ve laktasyon tahmini gösterilmez.')
    return re.sub(r'(<main\b[^>]*>)',lambda m:m.group()+dairy_card(ns,animal,summary,active),document,count=1)


def milk_markup(ns, request_url):
    query=parse_qs(urlparse(request_url).query);group=(query.get('group') or ['lactating'])[0]
    if group not in ('all','lactating','dry','heifer','unknown','not_lactating'):group='lactating'
    term=(query.get('q') or [''])[0].strip()
    with ns['db']() as c:
        animals=c.execute("select * from animals a where gender='Dişi' and coalesce(status,'Aktif')='Aktif' and not exists(select 1 from animal_losses l where l.animal_id=a.id) order by tag").fetchall()
        statuses=dairy.status_rows(c)
        summaries=[(a,milk_summary(c,a,statuses)) for a in animals]
        selected=[(a,sm) for a,sm in summaries if (group=='all' or sm['state']['status']==group) and search_matches(term, *(a[key] for key in ('tag','nickname','paddock','breed')))]
        today_rows={r['animal_id']:dict(r) for r in c.execute('select * from milk where measure_date=? order by id',(date.today().isoformat(),))}
    lactating=sum(sm['state']['status']=='lactating' for a,sm in summaries)
    unknown=sum(sm['state']['status']=='unknown' for a,sm in summaries)
    total=sum(sm['today'] for a,sm in summaries)
    options=''.join(f'<option value="{key}" {"selected" if group==key else ""}>{label}</option>' for key,label in [('lactating','Laktasyonda / Sağmal'),('all','Tüm aktif dişiler'),('dry','Kuru'),('heifer','Düve'),('unknown','Belirtilmedi'),('not_lactating','Laktasyonda değil')])
    rows=''
    for animal,sm in selected:
        aid=animal['id'];state=sm['state'];entry=today_rows.get(aid,{})
        cells=[f'<a href="/animal?id={aid}"><b>{esc(animal["tag"])}</b></a><small>{esc(animal["nickname"])}</small>',esc(animal['paddock'] or 'Padoksuz'),f'<a href="/dairy-status?animal={aid}">{esc(state["label"])}</a>',str(state['dim'])+' gün' if state['dim'] is not None else '—']
        for field,label in [('morning','Sabah'),('evening','Akşam')]:
            value=entry.get(field+'_liters')
            cells.append(f'<input class="milk-entry" type="number" min="0" step="0.1" name="{field}_{aid}" value="{esc(value) if value is not None else ""}" placeholder="0,0" aria-label="{esc(animal["tag"])} {label} litre">')
        cells += [f'{sm["today"]:.1f} L',f'{sm["avg7"]:.1f} L',f'{sm["avg30"]:.1f} L',f'{sm["total"]:.1f} L' if sm['total'] is not None else '—']
        labels=['Hayvan','Padok','Laktasyon Durumu','Sağım Günü','Sabah L','Akşam L','Bugün','7 Gün Ort.','30 Gün Ort.','Laktasyon Toplamı']
        rows+='<tr>'+''.join(f'<td data-label="{label}">{cell}</td>' for label,cell in zip(labels,cells))+'</tr>'
    rows=rows or '<tr><td colspan="10">Bu durumda hayvan yok. Laktasyon Belirle ile sağımdaki hayvanları seçebilir veya Tüm aktif dişiler filtresini açabilirsin.</td></tr>'
    return f'''<section class="cp-shared-milk"><header class="cp-shared-head"><div><h1>Süt & Laktasyon</h1><p>Manuel laktasyon durumu ve günlük süt kayıtları.</p></div><a class="btn" href="/dairy-status">Laktasyon Belirle</a></header><div class="cp-milk-kpis"><article class="card"><small>Sağmal</small><b data-milk-lactating>{lactating}</b></article><article class="card"><small>Durumu Belirtilmedi</small><b>{unknown}</b></article><article class="card"><small>Bugünkü Süt · tüm dişiler</small><b>{total:.1f} L</b></article></div><form method="get" action="/milk-center" class="card cp-milk-filter"><label>Göster<select name="group">{options}</select></label><label>Hayvan ara<input type="search" name="q" value="{esc(term)}" placeholder="Küpe, ad veya padok"></label><button class="btn">Filtrele</button><b role="status">{len(selected)} hayvan</b></form><form method="post" action="/milk-center" class="card" data-submit-lock="1"><input type="hidden" name="measure_date" value="{date.today().isoformat()}"><div class="cp-milk-table-scroll"><table class="cp-milk-table"><thead><tr>{''.join('<th>'+label+'</th>' for label in ['Hayvan','Padok','Laktasyon Durumu','Sağım Günü','Sabah L','Akşam L','Bugün','7 Gün Ort.','30 Gün Ort.','Laktasyon Toplamı'])}</tr></thead><tbody>{rows}</tbody></table></div><div class="cp-shared-actions"><button class="btn" type="submit">Günlük Sütleri Kaydet</button></div></form><p class="mut cp-milk-note">Sağmal sayısı kaydettiğin manuel durumu kullanır. Başlangıç bilinmiyorsa sağım günü ve laktasyon toplamı boş kalır. 7 ve 30 günlük ortalamalar yalnız süt girilmiş günlerden hesaplanır. Yeni süt girişi laktasyon durumunu değiştirmez.</p></section>'''


def install(ns, icon):
    app=ns['App'];original_get=app.do_GET
    def do_GET(self):
        parsed=urlparse(self.path);query=parse_qs(parsed.query)
        modules=parsed.path=='/modules' or (parsed.path=='/' and query.get('app_view')==['modules'])
        if not modules and parsed.path!='/milk-center':return original_get(self)
        if not self.require():return
        ok,_,message=ns['license_status']()
        if not ok:return self.redirect('/license',message)
        body=modules_markup(icon) if modules else milk_markup(ns,self.path)
        title='Modüller' if modules else 'Süt & Laktasyon'
        path='/modules' if modules else '/milk-center'
        return self.send_html(ns['page'](title,body,path,self.user()['username'],(query.get('msg') or [''])[0]))
    app.do_GET=do_GET
