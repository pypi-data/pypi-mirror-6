# -*- coding: utf-8 -*-
'''
    vdirsyncer.storage.filesystem
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Markus Unterwaditzer
    :license: MIT, see LICENSE for more details.
'''

import os
from vdirsyncer.storage.base import Storage, Item
import vdirsyncer.exceptions as exceptions
from vdirsyncer.utils import expand_path
import vdirsyncer.log as log
logger = log.get('storage.filesystem')


class FilesystemStorage(Storage):

    '''Saves data in vdir collection
    mtime is etag
    filename without path is href'''

    _repr_attributes = ('path',)

    def __init__(self, path, fileext, collection=None, encoding='utf-8',
                 **kwargs):
        '''
        :param path: Absolute path to a vdir or collection, depending on the
            collection parameter (see
            :py:class:`vdirsyncer.storage.base.Storage`).
        :param fileext: The file extension to use (e.g. `".txt"`). Contained in
            the href, so if you change the file extension after a sync, this
            will trigger a re-download of everything (but *should* not cause
            data-loss of any kind).
        :param encoding: File encoding for items.
        '''
        super(FilesystemStorage, self).__init__(**kwargs)
        if collection is not None:
            path = os.path.join(path, collection)
        self.collection = collection
        self.path = expand_path(path)
        self.encoding = encoding
        self.fileext = fileext

    @classmethod
    def discover(cls, path, **kwargs):
        if kwargs.pop('collection', None) is not None:
            raise TypeError('collection argument must not be given.')
        for collection in os.listdir(path):
            s = cls(path=path, collection=collection, **kwargs)
            yield s

    def _get_filepath(self, href):
        return os.path.join(self.path, href)

    def _get_href(self, uid):
        return uid + self.fileext

    def list(self):
        for fname in os.listdir(self.path):
            fpath = os.path.join(self.path, fname)
            if os.path.isfile(fpath) and fname.endswith(self.fileext):
                yield fname, os.path.getmtime(fpath)

    def get(self, href):
        fpath = self._get_filepath(href)
        with open(fpath, 'rb') as f:
            return (Item(f.read().decode(self.encoding)),
                    os.path.getmtime(fpath))

    def has(self, href):
        return os.path.isfile(self._get_filepath(href))

    def upload(self, obj):
        href = self._get_href(obj.uid)
        fpath = self._get_filepath(href)
        if os.path.exists(fpath):
            raise exceptions.AlreadyExistingError(obj.uid)
        with open(fpath, 'wb+') as f:
            f.write(obj.raw.encode(self.encoding))
        return href, os.path.getmtime(fpath)

    def update(self, href, obj, etag):
        fpath = self._get_filepath(href)
        if href != self._get_href(obj.uid):
            logger.warning('href != uid + fileext: href={}; uid={}'
                           .format(href, obj.uid))
        if not os.path.exists(fpath):
            raise exceptions.NotFoundError(obj.uid)
        actual_etag = os.path.getmtime(fpath)
        if etag != actual_etag:
            raise exceptions.WrongEtagError(etag, actual_etag)

        with open(fpath, 'wb') as f:
            f.write(obj.raw.encode('utf-8'))
        return os.path.getmtime(fpath)

    def delete(self, href, etag):
        fpath = self._get_filepath(href)
        if not os.path.isfile(fpath):
            raise exceptions.NotFoundError(href)
        actual_etag = os.path.getmtime(fpath)
        if etag != actual_etag:
            raise exceptions.WrongEtagError(etag, actual_etag)
        os.remove(fpath)
