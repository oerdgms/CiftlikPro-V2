"""Dashboard query indexes and read reuse confined to one HTTP request."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from time import perf_counter
from urllib.parse import urlparse


_request = ContextVar('dashboard_request_reads', default=None)

# Non-unique indexes preserve existing rows and rules. Create them at startup,
# after the canonical schema/migrations, rather than during a page request.
INDEXES = (
    'CREATE INDEX IF NOT EXISTS idx_dash_weights_latest ON weights(animal_id,measure_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_dash_calf_weights_latest ON calf_weights(calf_id,measure_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_dash_inseminations_latest ON inseminations(animal_id,insemination_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_dash_calves_birth ON calves(mother_id,birth_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_dash_losses_animal ON animal_losses(animal_id)',
    'CREATE INDEX IF NOT EXISTS idx_dash_losses_calf ON animal_losses(calf_id)',
    'CREATE INDEX IF NOT EXISTS idx_dash_feed_stock ON feed_stock_transactions(feed_id,tx_type,quantity_kg)',
    'CREATE INDEX IF NOT EXISTS idx_dash_feed_price ON feed_prices(feed_id,effective_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_dash_feed_cost ON feed_cost_history(feed_id,effective_date DESC,id DESC)',
    'CREATE INDEX IF NOT EXISTS idx_dash_health_animal ON health(animal_id)',
    'CREATE INDEX IF NOT EXISTS idx_dash_adult_paddock ON animals(paddock_id,status)',
    'CREATE INDEX IF NOT EXISTS idx_dash_calf_paddock ON calves(paddock_id,promoted_animal_id,status)',
)


@contextmanager
def request_reads():
    state = {'active': False, 'values': {}}
    token = _request.set(state)
    try:
        yield state
    finally:
        _request.reset(token)


def _reuse(name, original):
    @wraps(original)
    def read(connection, *args, **kwargs):
        state = _request.get()
        if state is None:
            return original(connection, *args, **kwargs)
        # Dashboard counts run after birth reconciliation and maintenance.
        # Earlier maintenance must always see fresh reads and writes.
        if name == 'dashboard_herd_counts':
            state['active'] = True
        if not state['active']:
            return original(connection, *args, **kwargs)
        key = (name, args, tuple(sorted(kwargs.items())))
        if key not in state['values']:
            state['values'][key] = original(connection, *args, **kwargs)
        return state['values'][key]
    return read


def install(ns):
    if ns.get('_dashboard_performance_installed'):
        return
    ns['_dashboard_performance_installed'] = True
    original_init = ns['init_db']

    @wraps(original_init)
    def init_db():
        original_init()
        connection = ns['db']()
        try:
            for statement in INDEXES:
                connection.execute(statement)
            connection.commit()
        finally:
            connection.close()

    ns['init_db'] = init_db
    for name in ('dashboard_herd_counts', 'active_pregnancy_records',
                 'current_pregnancy_record', 'health_plan_entries',
                 'pregnancy_vaccine_tasks'):
        ns[name] = _reuse(name, ns[name])

    app = ns['App']
    original_get = app.do_GET

    @wraps(original_get)
    def do_GET(handler):
        if urlparse(handler.path).path != '/':
            return original_get(handler)
        started = perf_counter()
        with request_reads() as state:
            try:
                return original_get(handler)
            finally:
                elapsed = perf_counter() - started
                if state['active'] and elapsed >= 1:
                    print(f'[PERF] Dashboard sunucu yanıtı: {elapsed:.3f} sn')

    app.do_GET = do_GET
