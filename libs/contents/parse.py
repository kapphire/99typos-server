from .__include__ import *


class ContentHandler(object):
    def __init__(self, *args, **kwargs):
        self.dirname = tldextract.extract(kwargs.get('dirname', None)).domain
        self.filename = kwargs.get('filename', None)

    def get_file_path(self):
        path = os.path.join(self.dirname, self.filename + ext)
        return path

    def get_dir_path(self):
        path = os.path.join(settings.BASE_DIR, 'assets', self.dirname)
        return path

    def get_local_path(self):
        dir_path = self.get_dir_path()
        path = os.path.join(dir_path, self.filename + ext)
        return path

    def get_compressed(self, **kwargs):
        content = kwargs.get('content', None)
        pathlib.Path(self.get_dir_path()).mkdir(parents=True, exist_ok=True)

        compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, +15)
        compressed_data = compress.compress(content)
        compressed_data += compress.flush()

        f = open(self.get_local_path(), 'wb')
        f.write(compressed_data)
        f.close()

        return True