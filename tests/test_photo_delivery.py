import concurrent.futures
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
from PIL import Image
import photo_delivery as photos
import test_app_edition as app_tests


class PhotoTests(unittest.TestCase):
    def test_preview_cache_resize_original_unchanged_and_invalidation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test photo.jpg'
            Image.effect_noise((1800,1200),80).convert('RGB').save(path,quality=94)
            original=path.read_bytes()
            raw,mime,tag=photos.preview_bytes(tmp,path.name,320)
            self.assertEqual(mime,'image/webp')
            with Image.open(io.BytesIO(raw)) as image:self.assertEqual(image.size,(320,213))
            self.assertLess(len(raw),len(original)//5)
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),hashlib.sha256(original).digest())
            with patch.object(photos.Image,'open',side_effect=AssertionError('cache miss')):
                self.assertEqual(photos.preview_bytes(tmp,path.name,320),(raw,mime,tag))
            Image.new('RGB',(1200,1800),'red').save(path)
            raw2,_,tag2=photos.preview_bytes(tmp,path.name,320)
            self.assertNotEqual(tag,tag2)
            with Image.open(io.BytesIO(raw2)) as image:self.assertEqual(image.size,(213,320))
            self.assertEqual(len(list((Path(tmp)/'.photo-previews').glob('*.webp'))),1)

    def test_concurrent_requests_and_readonly_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            Image.new('RGB',(800,600),'blue').save(Path(tmp)/'x.png')
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                results=list(pool.map(lambda _:photos.preview_bytes(tmp,'x.png',320),range(16)))
            self.assertTrue(all(r==results[0] for r in results))
            with patch.object(Path,'mkdir',side_effect=PermissionError):
                self.assertTrue(photos.preview_bytes(tmp,'x.png',640)[0])

    def test_paths_missing_and_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ['../x.png','a/b.png','a\\b.png','.photo-previews','missing.jpg','bad\x00.jpg']:
                with self.assertRaises(OSError):photos.preview_bytes(tmp,name,320)
            (Path(tmp)/'legacy.jpg').write_bytes(b'not decodable')
            self.assertEqual(photos.preview_bytes(tmp,'legacy.jpg',320),(None,None,None))

    def test_markup_keeps_original_zoom_and_external_images(self):
        source='<head></head><img src="/uploads/a%20b.jpg" data-photo-zoom><img src="/uploads/list.jpg"><img src="https://example.test/x.jpg">'
        result=photos.enhance_photos(source,Path('/unused'))
        self.assertIn('size=640',result)
        self.assertIn('size=320',result)
        self.assertIn('data-photo-original="/uploads/a%20b.jpg"',result)
        self.assertIn('src="https://example.test/x.jpg"',result)
        self.assertEqual(photos.enhance_photos(result,Path('/unused')),result)


class PhotoHTTPTests(unittest.TestCase):
    setUp=app_tests.AppEditionTests.setUp
    tearDown=app_tests.AppEditionTests.tearDown
    get=app_tests.AppEditionTests.get

    def test_http_preview_conditional_missing_and_original(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(app_tests.server,'UPLOADS',Path(tmp)):
            Image.new('RGB',(1200,800),'green').save(Path(tmp)/'cow.jpg')
            raw=(Path(tmp)/'cow.jpg').read_bytes()
            status,headers,data,_=self.get('/photo-preview?name=cow.jpg&size=320',False)
            self.assertEqual(status,200)
            self.assertEqual(headers['Content-Type'],'image/webp')
            self.assertIn('private',headers['Cache-Control'])
            request=urllib.request.Request(self.base+'/photo-preview?name=cow.jpg&size=320',headers={'If-None-Match':headers['ETag']})
            with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(request)
            self.assertEqual(caught.exception.code,304)
            self.assertEqual(self.get('/uploads/cow.jpg',False)[2],raw)
            with self.assertRaises(urllib.error.HTTPError) as caught:self.get('/photo-preview?name=missing.jpg',False)
            self.assertEqual(caught.exception.code,404)
            self.assertEqual(caught.exception.headers['Cache-Control'],'no-store')
            (Path(tmp)/'legacy.jpg').write_bytes(b'old-file')
            self.assertEqual(self.get('/photo-preview?name=legacy.jpg',False)[2],b'old-file')

    def test_photo_asset_and_herd_markup(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(app_tests.server,'UPLOADS',Path(tmp)):
            ids=app_tests.AppEditionTests.seed(self)
            with app_tests.server.db() as c:
                c.execute("update animals set photo_url='/uploads/cow.jpg' where id=?",(ids[2],))
            text=self.get('/all-animals')[2].decode()
            self.assertIn('/photo-preview?name=cow.jpg&amp;size=',text)
            self.assertIn('data-photo-original="/uploads/cow.jpg"',text)
            self.assertIn('photo-retry.js?v=',text)
            self.assertEqual(self.get('/app-assets/photo-retry.js',False)[0],200)
