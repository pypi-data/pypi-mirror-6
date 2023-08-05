import os
import importlib
import sqlite3
import json
import kaa
from kaa import consts, utils


class KaaHistoryStorage:
    # todo: lock directory for network drives?

    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.conn.execute('''
            PRAGMA synchronous = NORMAL
        ''')
        self.hists = {}
        self._updated = False

    BUFFER_DURATION = 10

    def updated(self):
        if not self._updated:
            kaa.app.call_later(self.BUFFER_DURATION, self.flush)
            self._updated = True

    def flush(self):
        for hist in self.hists.values():
            hist.flush()
        self.conn.commit()
        self._updated = False

    def close(self):
        for hist in self.hists.values():
            hist.flush()

        for hist in self.hists.values():
            hist.close()

        self.conn.commit()
        self.conn.close()
        self.hists = None

    def get_history(self, name):
        if name not in self.hists:
            hist = History(self, name)
            self.hists[name] = hist

        return self.hists[name]


class History:
    MAX_HISTORY = 1000

    def __init__(self, storage, name):
        self.storage = storage
        self.name = name
        self.table_name = 'hist_' + self.name

        self._register()
        self.buffer = []

    def _register(self):
        self.storage.conn.execute('''
            CREATE TABLE IF NOT EXISTS {}
                (id INTEGER PRIMARY KEY,
                value TEXT,
                info  TEXT)'''.format(self.table_name))

    @utils.ignore_errors
    def close(self):
        ret = self.storage.conn.execute('''
            SELECT id FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name), (self.MAX_HISTORY * 2, ))
        recs = [value for value in ret]
        if recs:
            last, = recs[-1]
            self.storage.conn.execute('''
                DELETE FROM {} WHERE id < ?
                '''.format(self.table_name), (last,))

    @utils.ignore_errors
    def add(self, value, info=None):
        for n, (buf_value, buf_info) in enumerate(self.buffer):
            if value == buf_value:
                del self.buffer[n]
                break
        self.buffer.insert(0, (value, info))
        self.storage.updated()

    def get(self):
        buf_values = set(value for value, info in self.buffer)

        ret = self.storage.conn.execute('''
            SELECT value, info FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name),
            (self.MAX_HISTORY,))

        return self.buffer + [(value, json.loads(info))
                              for value, info in ret if value not in buf_values]

    @utils.ignore_errors
    def find(self, value):
        for buf_value, buf_info in self.buffer:
            if value == buf_value:
                return buf_info

        ret = self.storage.conn.execute('''
            SELECT info FROM {} WHERE value=?
            '''.format(self.table_name),
            (value,))

        for info, in ret:
            return json.loads(info)

    @utils.ignore_errors
    def flush(self):
        for value, info in self.buffer[::-1]:
            ret = self.storage.conn.execute('''
                DELETE FROM {} WHERE value = ?'''.format(self.table_name),
                                            (value, ))

            self.storage.conn.execute('''
                INSERT INTO {}(value, info) VALUES(?, ?)
                '''.format(self.table_name), (value, json.dumps(info)))
        self.buffer = []


class Config:
    FILETYPES = [
        'kaa.filetype.default',
        'kaa.filetype.python',
        'kaa.filetype.html',
        'kaa.filetype.javascript',
        'kaa.filetype.css',
        'kaa.filetype.diff',
        'kaa.filetype.rst',
        'kaa.filetype.markdown',
        'kaa.filetype.c',
    ]

    DEFAULT_NEWLINE = 'auto'
    DEFAULT_ENCODING = 'utf-8'
    AMBIGUOUS_WIDTH = 1

    def __init__(self, option):
        kaadir = os.path.abspath(
            os.path.expandvars(
                os.path.expanduser(consts.KAA_DIR)))

        if not os.path.exists(kaadir):
            os.makedirs(kaadir)

        logdir = os.path.join(kaadir, consts.LOGDIR)
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        histdir = os.path.join(kaadir, consts.HISTDIR)
        if not os.path.exists(histdir):
            os.mkdir(histdir)

        self.KAADIR = kaadir
        self.LOGDIR = logdir
        self.HISTDIR = histdir

        self.palette = option.palette

    def init_history(self):
        self.hist_storage = KaaHistoryStorage(
            os.path.join(self.HISTDIR, consts.HIST_DBNAME))

    def close(self):
        self.hist_storage.close()

    def hist(self, name):
        return self.hist_storage.get_history(name)

    def get_mode_packages(self):
        for pkgname in self.FILETYPES:
            try:
                pkg = importlib.import_module(pkgname)
            except Exception:
                kaa.log.exception('Error loading filetype: ' + repr(pkgname))
            else:
                yield pkg
