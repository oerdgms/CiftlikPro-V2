"""Module read reuse confined to one GET; no page or cross-request cache."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from sqlite3 import Row
from urllib.parse import urlparse

_request = ContextVar('besi_performance_reads', default=None)

ROUTES = frozenset(('/', '/all-animals', '/animals', '/males', '/calves', '/animal', '/calf',
    '/paddocks', '/performance', '/feeds', '/rations', '/ration-workbench', '/reproduction-center',
    '/estrus', '/inseminations', '/health', '/milk-center', '/finance', '/reports', '/agriculture',
    '/archive/sold', '/archive/slaughtered', '/archive/lost'))

INDEXES = (
    'CREATE INDEX IF NOT EXISTS idx_page_ration_history ON ration_item_history(ration_id,feed_id,effective_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_page_ration_dates ON ration_item_history(ration_id,effective_date)',
    'CREATE INDEX IF NOT EXISTS idx_page_pad_history ON paddock_history(animal_source,animal_id,moved_at,id)',
    'CREATE INDEX IF NOT EXISTS idx_page_pad_rations ON paddock_rations(paddock_id,start_date,end_date)',
    'CREATE INDEX IF NOT EXISTS idx_page_pad_extra ON paddock_extra_feeds(paddock_id,start_date,end_date)',
    'CREATE INDEX IF NOT EXISTS idx_page_finance_animal ON finance(animal_id,tx_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_page_finance_calf ON finance(calf_id,tx_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_page_finance_owners ON finance_animals(animal_id,finance_id)',
    'CREATE INDEX IF NOT EXISTS idx_page_milk_animal ON milk(animal_id,measure_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_page_estrus_animal ON estrus_records(animal_id,estrus_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_page_treat_animal ON treatments(animal_id,start_date)',
    'CREATE INDEX IF NOT EXISTS idx_page_vet_animal ON veterinary_visits(animal_id,visit_date)',
)


def activate():
    state = _request.get()
    if state is not None:
        state['active'] = True


@contextmanager
def request_reads():
    state = {'active':False, 'values':{}, 'weights':{}, 'bulk_weights':False}
    token = _request.set(state)
    try:
        yield state
    finally:
        _request.reset(token)


def weight_rows(connection, animal_id):
    """Same three-column SQLite rows, ordered as the canonical helper."""
    state = _request.get()
    if state is None or not state['bulk_weights']:
        return connection.execute('select measure_date,weight,notes from weights where animal_id=? order by measure_date,id',(animal_id,)).fetchall()
    # The workspace loop starts after the GET's maintenance writes.
    state['active'] = True
    key = (connection, connection.total_changes)
    if key not in state['weights']:
        shape = connection.execute('select measure_date,weight,notes from weights where 0')
        grouped = {}
        rows = connection.execute("""select w.measure_date,w.weight,w.notes,w.animal_id
            from weights w join animals a on a.id=w.animal_id
            where a.gender='Erkek' and coalesce(a.status,'Aktif') in ('Aktif','Kesildi','Satıldı')
            order by w.animal_id,w.measure_date,w.id""").fetchall()
        for row in rows:
            grouped.setdefault(row['animal_id'], []).append(Row(shape, tuple(row)[:3]))
        state['weights'][key] = grouped
    return list(state['weights'][key].get(animal_id, ()))


def _reuse(name, original, connection_first=True):
    @wraps(original)
    def read(*args, **kwargs):
        state = _request.get()
        if state is None or not state['active']:
            return original(*args, **kwargs)
        if connection_first == 'second':
            connection = args[1] if len(args)>1 else kwargs.get('con')
        else:
            connection = args[0] if connection_first and args else None
        if connection_first is True and connection is None:
            return original(*args, **kwargs)
        revision = connection.total_changes if connection is not None else None
        key = (name, args, tuple(sorted(kwargs.items())), revision)
        try:
            hash(key)
        except TypeError:
            return original(*args, **kwargs)
        if key not in state['values']:
            state['values'][key] = original(*args, **kwargs)
        value = state['values'][key]
        return list(value) if isinstance(value, list) else dict(value) if isinstance(value, dict) else value
    return read


def install(ns):
    if ns.get('_performance_speed_installed'):
        return
    ns['_performance_speed_installed'] = True
    original_init = ns['init_db']

    @wraps(original_init)
    def init_db():
        original_init()
        with ns['db']() as connection:
            for statement in INDEXES:
                connection.execute(statement)
    ns['init_db'] = init_db
    for name in ('paddock_feed_cost_between','ration_cost_between','ration_cost_on_date',
                 'ration_items_on_date','paddock_extra_feed_cost_between',
                 'paddock_extra_feed_cost_on_date','current_pregnancy_record',
                 'active_pregnancy_records'):
        ns[name] = _reuse(name, ns[name])
    ns['setting_float'] = _reuse('setting_float', ns['setting_float'], connection_first=False)
    ns['setting_get'] = _reuse('setting_get', ns['setting_get'], connection_first=False)
    for name in ('current_feed_price','feed_stock_kg'):
        ns[name] = _reuse(name, ns[name], connection_first='second')
    app = ns['App']
    original_get = app.do_GET

    @wraps(original_get)
    def do_GET(handler):
        if urlparse(handler.path).path not in ROUTES:
            return original_get(handler)
        with request_reads() as state:
            if state is not None:
                state['bulk_weights'] = urlparse(handler.path).path == '/performance'
            return original_get(handler)
    app.do_GET = do_GET
