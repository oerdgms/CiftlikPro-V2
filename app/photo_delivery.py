"""Small photo previews; original uploads and database records stay unchanged."""
import hashlib
import html
import io
import os
from pathlib import Path
import re
import threading
from urllib.parse import parse_qs, quote, unquote, urlsplit

from PIL import Image, ImageOps

_locks = [threading.Lock() for _ in range(16)]
_img = re.compile(r'<img\b[^>]*>', re.I)
_src = re.compile(r'\bsrc\s*=\s*([\"\'])(.*?)\1', re.I)


def enhance_photos(document, uploads):
    def change(match):
        tag = match.group()
        source = _src.search(tag)
        if not source or 'data-photo-original=' in tag:
            return tag
        original = html.unescape(source.group(2))
        url = urlsplit(original)
        if url.scheme or url.netloc or not url.path.startswith('/uploads/'):
            return tag
        name = unquote(url.path[len('/uploads/'):])
        if not name or Path(name).name != name or '\\' in name:
            return tag
        # 320px covers the list tile at high pixel density; 640px for profiles/gallery.
        size = 320 if 'data-photo-zoom' not in tag else 640
        preview = '/photo-preview?name='+quote(name, safe='')+'&size='+str(size)
        replacement = 'src="'+html.escape(preview, quote=True)+'" data-photo-original="'+html.escape(original, quote=True)+'" decoding="async"'
        return tag[:source.start()]+replacement+tag[source.end():]
    document = _img.sub(change, document)
    if 'data-photo-original=' in document and '/app-assets/photo-retry.js' not in document:
        document = document.replace('</head>', '<script src="/app-assets/photo-retry.js" defer></script></head>', 1)
    return document


def preview_bytes(uploads, name, size):
    if not name or Path(name).name != name or '\\' in name or name.startswith('.') or '\x00' in name:
        raise FileNotFoundError(name)
    original = Path(uploads)/name
    info = original.stat()
    if not original.is_file():
        raise FileNotFoundError(name)
    identity = hashlib.sha256((name+':'+str(info.st_mtime_ns)+':'+str(info.st_size)+':'+str(size)+':v1').encode()).hexdigest()
    etag = '"'+identity+'"'
    folder = Path(uploads)/'.photo-previews'
    # One replaceable cache slot per filename/size: updates don't accumulate versions.
    slot = hashlib.sha256((name+':'+str(size)).encode()).hexdigest()
    cached = folder/(slot+'.webp')
    stamp = folder/(slot+'.etag')
    with _locks[int(slot[:2],16) % len(_locks)]:
        try:
            if stamp.read_text() == etag:
                return cached.read_bytes(), 'image/webp', etag
        except OSError:
            pass
        try:
            with Image.open(original) as image:
                image = ImageOps.exif_transpose(image)
                image.thumbnail((size,size), Image.Resampling.LANCZOS)
                image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                output = io.BytesIO()
                image.save(output, 'WEBP', quality=78, method=4)
                data = output.getvalue()
        except (OSError, ValueError):
            # Unsupported legacy format still uses the working original route.
            return None, None, None
        try:
            folder.mkdir(exist_ok=True)
            temp = cached.with_suffix('.tmp')
            temp.write_bytes(data)
            os.replace(temp,cached)
            stamp.write_text(etag)
        except OSError:
            pass  # Read-only data folder: deliver an in-memory preview.
        return data, 'image/webp', etag


def install(ns):
    app = ns['App']
    previous = app.do_GET
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path != '/photo-preview':
            return previous(self)
        query = parse_qs(url.query)
        name = query.get('name',[''])[0]
        size = 320 if query.get('size',['320'])[0] == '320' else 640
        try:
            data, mime, etag = preview_bytes(ns['UPLOADS'], name, size)
        except OSError:
            self.send_response(404)
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length','0')
            self.end_headers()
            return
        if data is None:
            self.send_response(302)
            self.send_header('Location','/uploads/'+quote(name,safe=''))
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length','0')
            self.end_headers()
            return
        unchanged = self.headers.get('If-None-Match') == etag
        self.send_response(304 if unchanged else 200)
        self.send_header('ETag',etag)
        self.send_header('Cache-Control','private, max-age=0, must-revalidate')
        if not unchanged:
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        if not unchanged:
            self.wfile.write(data)
    app.do_GET = do_GET
