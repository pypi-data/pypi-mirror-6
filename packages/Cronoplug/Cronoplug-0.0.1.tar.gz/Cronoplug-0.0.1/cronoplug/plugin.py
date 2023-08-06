import zipfile
import io
import yaml

def from_fs(base_path):
    def get(filename):
        full_path = "{}/{}".format(base_path, filename)
        return open(full_path, 'rb')
    return get

class Plugin:
    def __init__(self, stream, name, source = lambda x: None):
        self.file = zipfile.ZipFile(stream, 'w')
        self._wrote_main = False
        self.name = name
        self._src = source

    def __enter__(self):
        return self

    def add_file(self, name, content):
        info = zipfile.ZipInfo(filename=name)
        if name == 'main.lua':
            self._wrote_main = True
            info.comment = self.name.encode('utf-8')
        if isinstance(content, io.IOBase):
            content = content.read()
        self.file.writestr(info, content)

    def import_file(self, name):
        content = self._src(name)
        if content is None:
            raise KeyError("No file {}".format(name))
        self.add_file(name, self._src(name))

    def import_from_manifest(self):
        manifest_src = self._src('manifest.yaml')
        if manifest_src is None:
            raise KeyError("No manifest found")
        try:
            data = yaml.load(manifest_src)
        except yaml.parser.ParserError:
            raise ValueError("Bad manifest file")
        files = data["files"]
        for fn in files:
            self.import_file(fn)

    def __exit__(self, type, value, traceback):
        if not self._wrote_main:
            self.add_file(name = 'main.lua', content = b'')
        self.file.close()

