import socket
import threading
import time
from http.server import ThreadingHTTPServer

import server

URL = f"http://127.0.0.1:{server.PORT}/login"

def port_is_open() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", server.PORT), timeout=0.4):
            return True
    except OSError:
        return False

def start_server() -> None:
    if port_is_open():
        return
    server.init_db()
    server.ensure_archive_schema()
    server.promote_mature_calves()
    httpd = ThreadingHTTPServer(("127.0.0.1", server.PORT), server.App)
    def background_backup() -> None:
        try: server.daily_backup()
        except Exception: pass
    threading.Thread(target=background_backup, daemon=True).start()
    httpd.serve_forever()

def wait_until_ready() -> None:
    for _ in range(120):
        if port_is_open(): return
        time.sleep(0.1)
    raise RuntimeError("ÇiftlikPro sunucusu başlatılamadı.")

def run() -> None:
    if not port_is_open(): threading.Thread(target=start_server, daemon=True).start()
    wait_until_ready()
    try:
        import webview
        webview.create_window("ÇiftlikPro Enterprise", URL, width=1500, height=920, min_size=(1024,680), resizable=True, confirm_close=False, text_select=True)
        webview.start(debug=False)
    except Exception:
        import webbrowser
        webbrowser.open(URL)
        while True: time.sleep(3600)

if __name__ == "__main__": run()
