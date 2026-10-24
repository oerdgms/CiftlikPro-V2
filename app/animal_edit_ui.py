"""Animal edit forms share the event sheet while retaining their original fields."""
import re
from html import escape


def tag_field(tag, label):
    value=str(tag or '').strip()
    match=re.fullmatch(r'TR([0-9]{8,14})',value,re.I)
    if not match:
        # Keep old/custom identifiers editable without silently renaming them.
        return '<label><span>'+escape(label)+'</span><input name="tag" required value="'+escape(value,quote=True)+'"></label>'
    return ('<label class="cp-edit-tag"><span>'+escape(label)+'</span><input type="hidden" name="tag_prefix" value="TR">'
            '<span class="cp-edit-tag-control"><span class="cp-edit-tag-prefix" aria-hidden="true">TR</span>'
            '<input type="text" name="tag_digits" data-cp-tag-digits inputmode="numeric" '
            'pattern="[0-9]{8,14}" maxlength="24" autocomplete="off" required '
            'aria-label="'+escape(label,quote=True)+', TR sonrası rakamlar" value="'+match[1]+'"></span></label>')


def markup(body, source, record):
    """Reuse the full multipart form, including photos and optional finance fields."""
    match=re.search(r'<form\b[^>]*>.*?</form>',body,re.S)
    if not match:return body
    form=match[0]
    label='Buzağı Küpesi' if source=='calf' else 'Küpe No'
    form=re.sub(r'<label>(?:Küpe No|Buzağı Küpesi)<input name="tag" required value="[^"]*"></label>',
                lambda _:tag_field(record['tag'],label),form,count=1)
    form=form.replace('class="form"','class="form cp-edit-form"',1)
    # These inputs already accept decimal values in the record handlers. Do not
    # pass them through the legacy formatter that strips decimal punctuation.
    money_names={'sold_price','purchase_price','daily_feed_cost','daily_care_cost','target_sale_price'}
    def money_input(match):
        element=match[0]
        name=re.search(r'\bname="([^"]+)"',element)
        return element[:-1]+' data-money-skip="1" inputmode="decimal">' if name and name[1] in money_names else element
    form=re.sub(r'<input\b[^>]*>',money_input,form)
    back='/'+source+'?id='+str(record['id'])
    form=re.sub(r'<a class="btn alt" href="[^"]*">İptal</a>',
                '<a class="btn alt" data-cp-state-close href="'+back+'">Vazgeç</a>',form)
    title='Buzağıyı Düzenle' if source=='calf' else 'Hayvanı Düzenle'
    subject=escape(str(record['tag'])+(' · '+str(record['nickname']) if record['nickname'] else ''))
    icon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m6 8-3-3v6l3 2m12-5 3-3v6l-3 2M6 6h12v10l-3 4H9l-3-4zM8 13h8v5H8zM9 9h.01M15 9h.01"/></svg>'
    return ('<section class="cp-state-content cp-edit-content" data-cp-edit-content lang="tr">'
            '<div class="cp-state-handle" aria-hidden="true"></div><header class="cp-state-head"><div><h2 id="cpStateTitle">'+title+'</h2></div>'
            '<a class="cp-state-cancel" data-cp-state-close href="'+back+'">Vazgeç</a></header>'
            '<div class="cp-state-subject"><span class="cp-state-subject-icon">'+icon+'</span><div><b>'+subject+'</b><small>'+('Buzağı' if source=='calf' else escape(str(record['gender'])))+'</small></div></div>'
            '<div class="cp-state-body">'+form+'</div></section>')
