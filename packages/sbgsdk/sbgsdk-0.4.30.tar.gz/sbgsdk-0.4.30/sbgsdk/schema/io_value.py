import os
import json
import logging
import tempfile
import shutil
from copy import deepcopy

from sbgsdk.util import DotAccessDict


class IOValue(unicode):
    meta = None

    def __new__(cls, value=None):
        if isinstance(value, list):
            value = value[0] if value else ''
        value = os.path.abspath(value) if value else value
        obj = unicode.__new__(cls) if not value else unicode.__new__(cls, value)
        obj.meta = DotAccessDict()
        return obj

    file = property(lambda self: self)

    def _load_meta(self):
        metadata_file = self + '.meta'
        if not os.path.exists(metadata_file):
            logging.warning('No metadata file found: %s', metadata_file)
            self.meta = DotAccessDict()
            return
        logging.info('Loading metadata from %s', metadata_file)
        try:
            with open(metadata_file) as f:
                self.meta = DotAccessDict(**json.load(f))
        except Exception, e:
            logging.exception('Error loading metadata')
            raise e

    def _save_meta(self):
        if not self.file:
            return
        metadata_file = self.file + '.meta'
        logging.info('Saving metadata to %s', metadata_file)
        if not os.path.exists(metadata_file):
            with open(metadata_file, 'w') as f:
                json.dump(self.meta, f)
            return
        tmp = tempfile.mktemp()
        with open(tmp, 'w') as f:
            json.dump(self.meta, f)
        shutil.move(tmp, metadata_file)

    def _abspath(self):
        self.file = os.path.normpath(os.path.abspath(self.file))

    @property
    def size(self):
        return os.stat(self).st_size if os.path.exists(self) else 0

    def make_metadata(self, **kwargs):
        return deepcopy(self.meta).update(**kwargs)

