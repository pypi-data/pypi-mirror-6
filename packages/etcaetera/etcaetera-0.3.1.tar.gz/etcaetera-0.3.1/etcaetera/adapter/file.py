import os
import imp

from etcaetera.adapter.base import Adapter
from etcaetera.utils import format_key
from etcaetera.constants import (
    JSON_EXTENSIONS,
    YAML_EXTENSIONS,
    PYTHON_EXTENSIONS
)


class File(Adapter):
    def __init__(self, filepath, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.filepath = filepath

    def load(self):
        _, file_extension = os.path.splitext(self.filepath)
        fd = open(self.filepath, 'r')

        if file_extension.lower() in JSON_EXTENSIONS:
            import json
            self.data = {format_key(k):v for k,v in json.load(fd).items()}
        elif file_extension.lower() in YAML_EXTENSIONS:
            from yaml import load as yload, dump as ydump
            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            self.data = {format_key(k):v for k,v in yload(fd, Loader=Loader).items()}
        elif file_extension.lower() in PYTHON_EXTENSIONS:
            mod = imp.load_source('mod', self.filepath)
            self.data = {k:v for k,v in vars(mod).items() if k.isupper()}
        else:
            raise ValueError("Unhandled file extension {0}".format(file_extension))

        fd.close()
