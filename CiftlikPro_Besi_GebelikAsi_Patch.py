from pathlib import Path
import shutil, sys, datetime


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: beklenen parça 1 kez bulunmalıydı, {count} kez bulundu.")
    return text.replace(old, new, 1)


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    candidates = [root / 'app' / 'server.py', root / 'server.py']
    server = next((p for p in candidates if p.exists()), None)
    if not server:
        raise SystemExit('server.py bulunamadı. Betiği CiftlikPro-V2 klasöründe çalıştırın veya klasör yolunu parametre olarak verin.')

    text = server.read_text(encoding='utf-8')
    original = text

    # Sürüm etiketi
    text = text.replace("APP_VERSION='3.1.0'", "APP_VERSION='3.1.1'", 1)
    text = text.replace("APP_LABEL='ENTERPRISE V3.1 BESİ PERFORMANS'", "APP_LABEL='ENTERPRISE V3.1.1 BESİ + GEBELİK AŞILARI'", 1)

    old_cost = '''def animal_cost_values(a):\n    purchase=float(a['purchase_price'] or 0) if 'purchase_price' in a.keys() else 0.0\n    feed=float(a['daily_feed_cost'] or 0) if 'daily_feed_cost' in a.keys() else 0.0\n    care=float(a['daily_care_cost'] or 0) if 'daily_care_cost' in a.keys() else 0.0\n    start=(a['purchase_date'] if 'purchase_date' in a.keys() else '') or (a['birth_date'] if 'birth_date' in a.keys() else '')\n    try: days=max(0,(date.today()-date.fromisoformat(start)).days)\n    except Exception: days=0\n    daily=feed+care\n    accumulated=days*daily\n    return days,daily,accumulated,purchase+accumulated\n'''
    new_cost = '''def animal_cost_values(a):\n    purchase=float(a['purchase_price'] or 0) if 'purchase_price' in a.keys() else 0.0\n    feed=float(a['daily_feed_cost'] or 0) if 'daily_feed_cost' in a.keys() else 0.0\n    care=float(a['daily_care_cost'] or 0) if 'daily_care_cost' in a.keys() else 0.0\n    start=(a['purchase_date'] if 'purchase_date' in a.keys() else '') or (a['birth_date'] if 'birth_date' in a.keys() else '')\n    # Aktif hayvanın maliyeti bugüne kadar yürür. Satılan/kesilen hayvanda çıkış\n    # tarihinde donar; böylece geçmiş besi maliyeti sonradan büyümeye devam etmez.\n    end=date.today()\n    status=(a['status'] if 'status' in a.keys() else '') or 'Aktif'\n    exit_date=(a['exit_date'] if 'exit_date' in a.keys() else '') or ''\n    if status!='Aktif' and exit_date:\n        try:end=date.fromisoformat(exit_date)\n        except Exception:pass\n    try: days=max(0,(end-date.fromisoformat(start)).days)\n    except Exception: days=0\n    daily=feed+care\n    accumulated=days*daily\n    return days,daily,accumulated,purchase+accumulated\n\ndef pregnancy_vaccine_tasks(con, horizon_days=7):\n    \"\"\"Gebe hayvanların 7. ve 8. ay aşı görevlerini üretir.\n    280 günlük gebelik modelinde 7. ay=210. gün, 8. ay=240. gün kabul edilir.\n    Yapılan görevler health.notes içine benzersiz işaretle kaydedilir.\n    \"\"\"\n    today=date.today()\n    limit=today+timedelta(days=horizon_days)\n    pregnancies=con.execute(\n        \"\"\"select i.id insemination_id,i.animal_id,i.insemination_date,a.tag,a.nickname\n           from inseminations i join animals a on a.id=i.animal_id\n           where i.pregnancy_result='Pozitif' and coalesce(a.status,'Aktif')='Aktif'\n             and i.id=(select i2.id from inseminations i2 where i2.animal_id=i.animal_id\n                       and i2.pregnancy_result='Pozitif' order by i2.insemination_date desc,i2.id desc limit 1)\n           order by i.insemination_date\"\"\"\n    ).fetchall()\n    tasks=[]\n    for p in pregnancies:\n        try: base=date.fromisoformat(p['insemination_date'])\n        except Exception: continue\n        for month,offset in ((7,210),(8,240)):\n            task_date=base+timedelta(days=offset)\n            if task_date>limit: continue\n            marker=f\"[GEBELIK_ASI:{p['insemination_id']}:{month}]\"\n            done=con.execute(\"select 1 from health where animal_id=? and notes like ? limit 1\",(p['animal_id'],f'%{marker}%')).fetchone()\n            if done: continue\n            days_left=(task_date-today).days\n            state='GECİKMİŞ' if days_left<0 else 'BUGÜN' if days_left==0 else 'YAKLAŞIYOR'\n            tasks.append({'insemination_id':p['insemination_id'],'animal_id':p['animal_id'],'tag':p['tag'],'nickname':p['nickname'],'month':month,'task_date':task_date.isoformat(),'days_left':days_left,'state':state,'marker':marker})\n    return sorted(tasks,key=lambda x:(x['task_date'],x['tag'],x['month']))\n'''
    text = replace_once(text, old_cost, new_cost, 'maliyet fonksiyonu')

    old_dashboard = '''                male_records=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif')='Aktif'").fetchall()\n                male_purchase_total=sum(float(r['purchase_price'] or 0) for r in male_records)\n                male_operating_cost=sum(animal_cost_values(r)[2] for r in male_records)\n                male_current_cost=male_purchase_total+male_operating_cost\n'''
    new_dashboard = '''                male_records=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif')='Aktif'").fetchall()\n                # Besi maliyetinde aktif erkekler + kesilmiş erkeklerin kesim gününde donmuş maliyeti tutulur.\n                male_cost_records=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif') in ('Aktif','Kesildi')").fetchall()\n                male_purchase_total=sum(float(r['purchase_price'] or 0) for r in male_cost_records)\n                male_operating_cost=sum(animal_cost_values(r)[2] for r in male_cost_records)\n                male_current_cost=male_purchase_total+male_operating_cost\n                slaughtered_male_cost=sum(animal_cost_values(r)[3] for r in male_cost_records if r['status']=='Kesildi')\n'''
    text = replace_once(text, old_dashboard, new_dashboard, 'dashboard maliyet kayıtları')

    text = replace_once(text,
        "                health_rows=c.execute(\"select h.next_date,a.id,a.tag,h.kind,h.product from health h left join animals a on a.id=h.animal_id where h.next_date between ? and ? order by h.next_date limit 8\",(date.today().isoformat(),(date.today()+timedelta(days=30)).isoformat())).fetchall()\n",
        "                health_rows=c.execute(\"select h.next_date,a.id,a.tag,h.kind,h.product from health h left join animals a on a.id=h.animal_id where h.next_date between ? and ? order by h.next_date limit 8\",(date.today().isoformat(),(date.today()+timedelta(days=30)).isoformat())).fetchall()\n                pregnancy_vaccines=pregnancy_vaccine_tasks(c,7)\n",
        'dashboard aşı görev sorgusu')

    old_health_html = "            health_html=''.join(f'<div class=\"alertitem\">💉 {h(r[\"tag\"] or \"Genel\")} · {h(r[\"kind\"])}<br><span class=\"mut\">{h(r[\"product\"])} — {h(r[\"next_date\"])}</span></div>' for r in health_rows) or '<p class=\"mut\">30 gün içinde planlanan sağlık işlemi yok.</p>'\n"
    new_health_html = old_health_html + "            pregnancy_vaccine_html=''.join(f'<div class=\"alertitem\" style=\"border-left-color:{\"#c8392b\" if t[\"state\"]==\"GECİKMİŞ\" else \"#e58c16\"}\"><b>💉 {h(t[\"tag\"])} · {t[\"month\"]}. Ay Gebelik Aşısı</b><br><span class=\"mut\">Planlanan: {h(t[\"task_date\"])} · {h(t[\"state\"])}</span><form method=\"post\" action=\"/pregnancy-vaccine-done\" style=\"margin-top:8px\"><input type=\"hidden\" name=\"animal_id\" value=\"{t[\"animal_id\"]}\"><input type=\"hidden\" name=\"insemination_id\" value=\"{t[\"insemination_id\"]}\"><input type=\"hidden\" name=\"month\" value=\"{t[\"month\"]}\"><button class=\"btn red\">Aşı Yapıldı</button></form></div>' for t in pregnancy_vaccines) or '<p class=\"mut\">7 gün içinde bekleyen 7./8. ay gebelik aşısı yok.</p>'\n"
    text = replace_once(text, old_health_html, new_health_html, 'dashboard aşı HTML')

    old_cost_rows = "            max_male_cost=max([animal_cost_values(r)[3] for r in male_records]+[1])\n            male_cost_rows=''.join(f'<div class=\"progress-item\"><div class=\"progress-head\"><span>🐂 {h(r[\"tag\"])} {h(r[\"nickname\"])}</span><b>{money(animal_cost_values(r)[3])}</b></div><div class=\"progress-track\"><div class=\"progress-fill\" style=\"width:{max(3,int(animal_cost_values(r)[3]/max_male_cost*100))}%\"></div></div></div>' for r in sorted(male_records,key=lambda x:animal_cost_values(x)[3],reverse=True)[:8]) or '<p class=\"mut\">Aktif erkek hayvan kaydı yok.</p>'\n"
    new_cost_rows = "            max_male_cost=max([animal_cost_values(r)[3] for r in male_cost_records]+[1])\n            male_cost_rows=''.join(f'<div class=\"progress-item\"><div class=\"progress-head\"><span>🐂 {h(r[\"tag\"])} {h(r[\"nickname\"])} {\"<span class=\\\"perf-badge status-none\\\">Kesildi</span>\" if r[\"status\"]==\"Kesildi\" else \"\"}</span><b>{money(animal_cost_values(r)[3])}</b></div><div class=\"progress-track\"><div class=\"progress-fill\" style=\"width:{max(3,int(animal_cost_values(r)[3]/max_male_cost*100))}%\"></div></div></div>' for r in sorted(male_cost_records,key=lambda x:animal_cost_values(x)[3],reverse=True)[:8]) or '<p class=\"mut\">Besi maliyet kaydı yok.</p>'\n"
    text = replace_once(text, old_cost_rows, new_cost_rows, 'hayvan bazlı maliyet listesi')

    text = text.replace('Erkek Hayvan Alış Değeri<b>{money(male_purchase_total)}</b><small>Aktif erkeklerin toplam alış fiyatı</small>',
                        'Erkek Hayvan Alış Değeri<b>{money(male_purchase_total)}</b><small>Aktif + kesilen erkeklerin toplam alış fiyatı</small>', 1)
    text = text.replace('Erkekler Toplam Anlık Maliyeti<b>{money(male_current_cost)}</b><small>Alış değeri + birikmiş gider</small>',
                        'Toplam Gerçekleşmiş Besi Maliyeti<b>{money(male_current_cost)}</b><small>Aktifler + kesilenlerin kesim gününe kadarki maliyeti</small>', 1)
    text = text.replace('Grafik yalnızca aktif erkek hayvanların toplam maliyetini gösterir.',
                        'Grafik aktif erkekleri ve kesilen erkeklerin kesim tarihinde donmuş maliyetini birlikte gösterir. Kesilen maliyeti: {money(slaughtered_male_cost)}.', 1)
    text = text.replace('<h2>Hayvan Bazında Anlık Maliyet</h2>', '<h2>Hayvan Bazında Besi Maliyeti</h2>', 1)

    old_tail = '<div class="two" style="margin-top:14px"><div class="card"><h2>Yaklaşan Doğumlar</h2><div class="alertlist">{due_html}</div></div><div class="card"><h2>Yaklaşan Aşı / Sağlık</h2><div class="alertlist">{health_html}</div></div></div>\'\'\''
    new_tail = '<div class="two" style="margin-top:14px"><div class="card"><h2>Yaklaşan Doğumlar</h2><div class="alertlist">{due_html}</div></div><div class="card"><h2>Yaklaşan Aşı / Sağlık</h2><div class="alertlist">{health_html}</div></div></div><div class="card warning-panel" style="margin-top:14px"><h2>🚨 Gebelik 7./8. Ay Aşı Görevleri</h2><p class="mut">Aşı yapılana kadar bu uyarılar ana ekranda kalır. Tarihi geçenler kırmızı gösterilir.</p><div class="alertlist">{pregnancy_vaccine_html}</div></div>\'\'\''
    text = replace_once(text, old_tail, new_tail, 'dashboard aşı paneli')

    # Sağlık sayfasında da bekleyen görevleri göster.
    old_health_page = "        if path=='/health':\n            with db() as c: animals=c.execute('select id,tag,nickname from animals order by tag').fetchall(); rows=c.execute('select h.*,a.tag from health h left join animals a on a.id=h.animal_id order by applied_date desc').fetchall()\n            opts=''.join(f'<option value=\"{a[\"id\"]}\">{h(a[\"tag\"])} - {h(a[\"nickname\"])}</option>' for a in animals); trs=''.join(f'<tr><td>{h(r[\"tag\"])}</td><td>{h(r[\"kind\"])}</td><td>{h(r[\"product\"])}</td><td>{h(r[\"applied_date\"])}</td><td>{h(r[\"next_date\"])}</td><td>{money(r[\"cost\"])}</td></tr>' for r in rows)\n"
    new_health_page = "        if path=='/health':\n            with db() as c:\n                animals=c.execute('select id,tag,nickname from animals order by tag').fetchall()\n                rows=c.execute('select h.*,a.tag from health h left join animals a on a.id=h.animal_id order by applied_date desc').fetchall()\n                pregnancy_vaccines=pregnancy_vaccine_tasks(c,7)\n            opts=''.join(f'<option value=\"{a[\"id\"]}\">{h(a[\"tag\"])} - {h(a[\"nickname\"])}</option>' for a in animals); trs=''.join(f'<tr><td>{h(r[\"tag\"])}</td><td>{h(r[\"kind\"])}</td><td>{h(r[\"product\"])}</td><td>{h(r[\"applied_date\"])}</td><td>{h(r[\"next_date\"])}</td><td>{money(r[\"cost\"])}</td></tr>' for r in rows)\n            pv_html=''.join(f'<div class=\"alertitem\" style=\"border-left-color:{\"#c8392b\" if t[\"state\"]==\"GECİKMİŞ\" else \"#e58c16\"}\"><b>{h(t[\"tag\"])} · {t[\"month\"]}. Ay Gebelik Aşısı</b> — {h(t[\"task_date\"])} ({h(t[\"state\"])})<form method=\"post\" action=\"/pregnancy-vaccine-done\" style=\"margin-top:8px\"><input type=\"hidden\" name=\"animal_id\" value=\"{t[\"animal_id\"]}\"><input type=\"hidden\" name=\"insemination_id\" value=\"{t[\"insemination_id\"]}\"><input type=\"hidden\" name=\"month\" value=\"{t[\"month\"]}\"><button class=\"btn red\">Aşı Yapıldı</button></form></div>' for t in pregnancy_vaccines) or '<p class=\"mut\">Bekleyen gebelik aşı görevi yok.</p>'\n"
    text = replace_once(text, old_health_page, new_health_page, 'sağlık sayfası sorgu')
    text = text.replace("body=f'''<h1>Sağlık</h1><div class=\"card\"><form method=\"post\" class=\"form\">",
                        "body=f'''<h1>Sağlık</h1><div class=\"card warning-panel\"><h2>🚨 Gebelik 7./8. Ay Aşı Görevleri</h2><div class=\"alertlist\">{pv_html}</div></div><div class=\"card\" style=\"margin-top:14px\"><form method=\"post\" class=\"form\">", 1)

    # POST: Gebelik aşısını tek tıkla sağlık geçmişine kaydet.
    post_anchor = "                if path=='/health':\n                    c.execute('insert into health(animal_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?)',(f.get('animal_id'),f['kind'],f['product'],f['applied_date'],f.get('next_date'),float(f.get('cost') or 0),f.get('notes')))\n"
    post_new = "                if path=='/pregnancy-vaccine-done':\n                    aid=f.get('animal_id'); ins_id=f.get('insemination_id'); month=int(f.get('month') or 0)\n                    if month not in (7,8): return self.redirect('/','Geçersiz gebelik aşı görevi.')\n                    preg=c.execute(\"select i.id,a.tag from inseminations i join animals a on a.id=i.animal_id where i.id=? and i.animal_id=? and i.pregnancy_result='Pozitif'\",(ins_id,aid)).fetchone()\n                    if not preg:return self.redirect('/','Gebelik kaydı bulunamadı.')\n                    marker=f'[GEBELIK_ASI:{ins_id}:{month}]'\n                    already=c.execute('select 1 from health where animal_id=? and notes like ? limit 1',(aid,f'%{marker}%')).fetchone()\n                    if not already:\n                        c.execute('insert into health(animal_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?)',(aid,'Aşı',f'Gebelik {month}. Ay Aşısı',date.today().isoformat(),' ',0,f'Otomatik gebelik aşı görevi tamamlandı. {marker}'))\n                    return self.redirect('/','Aşı yapıldı olarak kaydedildi ve hayvan sağlık geçmişine işlendi.')\n                if path=='/health':\n                    c.execute('insert into health(animal_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?)',(f.get('animal_id'),f['kind'],f['product'],f['applied_date'],f.get('next_date'),float(f.get('cost') or 0),f.get('notes')))\n"
    text = replace_once(text, post_anchor, post_new, 'aşı tamamla POST')

    if text == original:
        raise RuntimeError('Hiçbir değişiklik uygulanmadı.')

    backup = server.with_name(server.name + '.before_besi_gebelik_asi_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.bak')
    shutil.copy2(server, backup)
    server.write_text(text, encoding='utf-8')

    # Python sözdizimi kontrolü
    compile(text, str(server), 'exec')
    print('OK')
    print('Güncellendi:', server)
    print('Yedek:', backup)
    print('Değişiklikler: kesilen hayvan maliyeti + 7./8. ay gebelik aşı görevleri')

if __name__ == '__main__':
    main()
