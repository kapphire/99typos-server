import os
import pathlib
import tldextract
import zlib

from django.conf import settings


ext = settings.HTML_CONTENT_EXTENSION