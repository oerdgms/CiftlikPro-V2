"""Use real adult and calf membership in every animal-report output."""


def rows(ns, group='all', status='Aktif', search='', paddock=''):
    with ns['db']() as c:
        adults = c.execute('''select a.*,
            (select m.tag from calves oldc join animals m on m.id=oldc.mother_id
             where oldc.promoted_animal_id=a.id limit 1) mother_tag,
            (select l.event_type from animal_losses l where l.animal_id=a.id
             order by l.event_date desc,l.id desc limit 1) report_loss
            from animals a order by a.tag''').fetchall()
        calves = c.execute('''select ca.*,m.tag mother_tag,
            (select l.event_type from animal_losses l where l.calf_id=ca.id
             order by l.event_date desc,l.id desc limit 1) report_loss
            from calves ca left join animals m on m.id=ca.mother_id
            where ca.promoted_animal_id is null order by ca.tag''').fetchall()

    result = []
    wanted = {'female': 'Dişi', 'male': 'Erkek', 'calves': 'Buzağı'}.get(group)
    term = ns['normalized_heading'](search)
    for record, source in [(r, 'animal') for r in adults] + [(r, 'calf') for r in calves]:
        actual_status = str(record['status'] or 'Aktif')
        if actual_status == 'Aktif' and record['report_loss']:
            actual_status = record['report_loss']
        if status != 'Tümü' and actual_status != status:
            continue
        record_group = 'Buzağı' if source == 'calf' else 'Dişi' if record['gender'] == 'Dişi' else 'Erkek'
        if wanted and record_group != wanted:
            continue
        row = {
            'tag': record['tag'], 'nickname': record['nickname'] or '',
            'group': record_group, 'species': 'Sığır', 'breed': record['breed'] or '',
            'gender': record['gender'] or '', 'birth_date': record['birth_date'] or '',
            'mother_tag': record['mother_tag'] or '', 'arrival_date': record['purchase_date'] or '',
            'paddock': record['paddock'] or '', 'status': actual_status,
        }
        if paddock and str(row['paddock']).strip() != paddock:
            continue
        if term and term not in ns['normalized_heading'](' '.join(str(row[key]) for key in
                ('tag', 'nickname', 'breed', 'gender', 'mother_tag', 'paddock'))):
            continue
        result.append(row)
    return sorted(result, key=lambda row: (row['group'], row['tag']))


def install(ns):
    # All four existing routes resolve this shared selector at request time.
    def animal_report_rows(group='all', status='Aktif', search='', paddock=''):
        return rows(ns, group, status, search, paddock)
    ns['animal_report_rows'] = animal_report_rows
