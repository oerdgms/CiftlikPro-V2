import os
import shutil
import socket
import threading
import time
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer

# DEV verisi, kurulu kararlı ÇiftlikPro verisinden tamamen ayrı tutulur.
local_appdata = Path(os.environ.get("LOCALAPPDATA") or Path.home())
dev_root = Path(os.environ.get("CIFTLIKPRO_DATA_DIR") or (local_appdata / "CiftlikPro_DEV"))
prod_root = local_appdata / "CiftlikPro"
dev_root.mkdir(parents=True, exist_ok=True)

# İlk DEV açılışında gerçek verinin bir KOPYASINI al. Asıl veritabanına dokunulmaz.
for filename in ("ciftlik.db", "ciftlikpro.license"):
    src = prod_root / filename
    dst = dev_root / filename
    if src.exists() and not dst.exists():
        try:
            shutil.copy2(src, dst)
        except OSError:
            pass

# server.py, CIFTLIKPRO_DATA_DIR ortam değişkenini import sırasında okur.
os.environ["CIFTLIKPRO_DATA_DIR"] = str(dev_root)

import server  # noqa: E402

server.PORT = int(os.environ.get("CIFTLIKPRO_DEV_PORT", "8954"))
server.APP_CHANNEL = "DEV"
server.APP_LABEL = f"{server.APP_LABEL} · DEV TEST"
URL = f"http://127.0.0.1:{server.PORT}/login"


def port_is_open() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", server.PORT), timeout=0.5):
            return True
    except OSError:
        return False


def open_browser_when_ready() -> None:
    for _ in range(120):
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

    print("=" * 64)
    print("CiftlikPro DEV TEST")
    print(f"DEV adresi : {URL}")
    print(f"DEV veri   : {dev_root}")
    print("Kararli kurulum verisi degistirilmez.")
    print("Kapatmak icin bu pencereyi kapatabilir veya Ctrl+C yapabilirsiniz.")
    print("=" * 64)

    httpd.serve_forever()


if __name__ == "__main__":
    run()
