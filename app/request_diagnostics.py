"""Request-local timings; no credentials, queries or farm records in logs."""
from contextvars import ContextVar
from functools import wraps
import os
from time import perf_counter
from urllib.parse import urlsplit

_timings = ContextVar('request_stage_timings', default=None)


def measured(label, original):
    @wraps(original)
    def run(*args, **kwargs):
        state = _timings.get()
        if state is None:
            return original(*args, **kwargs)
        started = perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            elapsed, count = state.get(label, (0.0, 0))
            state[label] = (elapsed + perf_counter() - started, count + 1)
    return run


def install(ns):
    if ns.get('_request_diagnostics_installed'):
        return
    ns['_request_diagnostics_installed'] = True
    for name, label in (
        ('promote_mature_calves', 'buzağı geçişi'),
        ('sync_daily_paddock_feed_stock', 'stok eşitleme'),
        ('rebuild_feed_cost_history', 'maliyet geçmişi'),
        ('password_verify', 'şifre kontrolü'),
        ('page', 'sayfa oluşturma'),
    ):
        ns[name] = measured(label, ns[name])
    from multi_farm import Registry
    Registry.sync_accounts = measured('hesap eşitleme', Registry.sync_accounts)
    for method in ('do_GET', 'do_POST'):
        original = getattr(ns['App'], method)
        def wrap(original):
            @wraps(original)
            def request(handler):
                path = urlsplit(handler.path).path
                if path not in ('/', '/login', '/all-animals', '/performance', '/feeds', '/paddocks'):
                    return original(handler)
                state = {}
                token = _timings.set(state)
                started = perf_counter()
                try:
                    return original(handler)
                finally:
                    total = perf_counter() - started
                    _timings.reset(token)
                    if total >= .5 or os.environ.get('CIFTLIKPRO_PERF') == '1':
                        stages = ' · '.join(f'{key}: {elapsed:.3f} sn ({count})'
                                            for key, (elapsed, count) in sorted(state.items()))
                        print(f'[PERF] İstek {handler.command} {path}: {total:.3f} sn · {stages}')
            return request
        setattr(ns['App'], method, wrap(original))
