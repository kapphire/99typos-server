import os
import boto3
import hashlib
import json
import requests
import shutil
from urllib.parse import urlparse
import zlib

from validators import url
from bs4 import BeautifulSoup
from string import whitespace, punctuation

from django.conf import settings

s3 = boto3.client('s3')