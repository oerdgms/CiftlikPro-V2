import socket
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer

import server

URL = f"http://127.0.0.1:{server.PORT}/login"


def port_is_open() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", server.PORT), timeout=0.5):
            return True
    except OSError:
        return False


def open_browser_when_ready() -> None:
    for _ in range(80):
        if port_is_open():
            webbrowser.open(URL)
            return
        time.sleep(0.15)


def run() -> None:
    if port_is_open():
        webbrowser.open(URL)
        return

    server.init_db()
    server.ensure_archive_schema()
    server.promote_mature_calves()

    httpd = ThreadingHTTPServer(("0.0.0.0", server.PORT), server.App)
    threading.Thread(target=open_browser_when_ready, daemon=True).start()

    def background_backup() -> None:
        try:
            server.daily_backup()
        except Exception:
            pass

    threading.Thread(target=background_backup, daemon=True).start()
    httpd.serve_forever()


if __name__ == "__main__":
    run()
