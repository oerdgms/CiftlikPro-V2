import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
import server

URL = f"http://127.0.0.1:{server.PORT}/login"
STATUS_URL = f"http://127.0.0.1:{server.PORT}/api/v1/status"
EXPECTED_MOBILE_BUILD = "MobileFullV1-ModuleHub"


def port_is_open() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", server.PORT), timeout=0.5):
            return True
    except OSError:
        return False


def running_build():
    try:
        with urllib.request.urlopen(STATUS_URL, timeout=1.2) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("mobile_api_build"), data.get("app_version")
    except Exception:
        return None, None


def listener_pids():
    if os.name != "nt":
        return []
    try:
        out = subprocess.check_output(["netstat", "-ano", "-p", "tcp"], text=True, errors="ignore")
    except Exception:
        return []
    pids = set()
    suffix = f":{server.PORT}"
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[0].upper() == "TCP" and parts[1].endswith(suffix) and parts[3].upper() == "LISTENING":
            if parts[4].isdigit():
                pids.add(int(parts[4]))
    return sorted(pids)


def stop_old_ciftlikpro_server() -> bool:
    pids = listener_pids()
    if not pids:
        return False
    for pid in pids:
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception:
            return False
    for _ in range(30):
        if not port_is_open():
            return True
        time.sleep(0.1)
    return not port_is_open()


def open_browser_when_ready() -> None:
    for _ in range(100):
        if port_is_open():
            webbrowser.open(URL)
            return
        time.sleep(0.15)


def run() -> None:
    background = "--background" in sys.argv or "--startup" in sys.argv
    if port_is_open():
        build, _ = running_build()
        if build == EXPECTED_MOBILE_BUILD:
            if not background:
                webbrowser.open(URL)
            return
        # A previous ÇiftlikPro source process is still holding the app port.
        # Restart it so the newly extracted package actually becomes active.
        if not stop_old_ciftlikpro_server():
            if not background:
                print(f"ÇiftlikPro'nun eski sürümü {server.PORT} portunda çalışıyor. Önce eski pencereyi kapatıp tekrar deneyin.")
            return

    server.init_db()
    server.ensure_archive_schema()
    server.promote_mature_calves()

    httpd = server.QuietThreadingHTTPServer(("0.0.0.0", server.PORT), server.App)
    if not background:
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
