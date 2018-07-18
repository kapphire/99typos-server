from .__include__ import *


def get_hashed(data):
    hashed_data = hashlib.sha256(data)
    return hashed_data.hexdigest()


def upload_to_s3(**kwargs):
    s3_path = kwargs.get('path', None)
    file_path = os.path.join(settings.BASE_DIR, 'assets', s3_path)
    s3.upload_file(file_path, settings.S3_BUCKET_NAME, s3_path)
    return True


def get_plain_text(**kwargs):
    html = str(kwargs.get('html')).encode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    return soup


def get_filtered_text(**kwargs):
    content = list()
    soup = kwargs.get('soup', None)    
    for elem in soup(['script', 'style', '[document]', 'head', 'nav', 'title', 'header', 'footer', 'meta']):
        elem.extract()
    
    for item in soup.stripped_strings:
        if item in punctuation + whitespace:
            continue
        content.append(repr(item))

    # text = soup.get_text()
    # lines = (line.strip() for line in text.splitlines())
    # chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # content = '\n'.join(chunk for chunk in chunks if chunk)
    content = '\n'.join(content)
    return content


def get_img_links(**kwargs):
    soup = kwargs.get('soup', None)
    site_url = kwargs.get('url', None)
    result = list()
    for tag in soup(['img']):
        if not url(tag.attrs.get('src')):
            parsed_uri = urlparse(site_url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            result.append(domain + tag.attrs.get('src'))
        else:
            result.append(tag.attrs.get('src'))
    return result


def get_pg_links(**kwargs):
    soup = kwargs.get('soup', None)
    site_url = kwargs.get('url', None)
    result = list()
    for tag in soup(['a']):
        if not url(tag.attrs.get('href')):
            parsed_uri = urlparse(site_url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            result.append(domain + tag.attrs.get('href'))
        else:
            result.append(tag.attrs.get('href'))
    return result


def get_typos(**kwargs):
    content = kwargs.get('text')
    payload = {
        'text': content,
        'language': 'en-US'
    }
    resp = requests.post('http://127.0.0.1:8081/v2/check', data=payload)
    result = json.loads(resp.text)
    return result['matches']
 