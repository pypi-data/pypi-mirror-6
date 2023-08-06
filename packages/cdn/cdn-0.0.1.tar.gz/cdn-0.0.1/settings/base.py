from unipath import Path

ROOT_DIR = Path()

DEBUG = False

DOMAIN = 'cdn.stroytest1.ru'

MEDIA_ROOT = ROOT_DIR.child('public', 'media')

STATIC_ROOT = ROOT_DIR.child('public', 'static')

IMAGES_ROOT = MEDIA_ROOT.child('images')

CACHE_ROOT = MEDIA_ROOT.child('cache')

USE_MONGODB = True  # if False will be used filesystem for store

LOG_FILE = ROOT_DIR.child('logs', 'app.log')
