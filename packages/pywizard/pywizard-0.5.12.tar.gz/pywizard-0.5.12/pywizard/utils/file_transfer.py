from base64 import b64encode, b64decode
import hashlib
import json
import zipfile
import os
import stat
from cStringIO import StringIO
import sys


class TransferBadChkException(Exception):
    pass


def __create_zip(path):
    def walktree(top=".", depthfirst=True):
        names = os.listdir(top)
        if not depthfirst:
            yield top, names
        for name in names:

            if name[0] == '.':
                continue

            try:
                st = os.lstat(os.path.join(top, name))
            except os.error:
                continue
            if stat.S_ISDIR(st.st_mode):
                for (newtop, children) in walktree(os.path.join(top, name),
                                                   depthfirst):
                    yield newtop, children
        if depthfirst:
            yield top, names



    list_ = []
    for (basepath, children) in walktree(path, False):

        for child in children:
            if child[0] == '.':
                continue
            if child[-4:] == '.pyc':
                continue

            f = os.path.join(basepath, child)

            if os.path.isfile(f):
                f = f.encode(sys.getfilesystemencoding())

                list_.append(f)

    f = StringIO()
    file_ = zipfile.ZipFile(f, "w")

    for fname in list_:
        nfname = fname[len(path) + 1:]
        file_.write(fname, nfname, zipfile.ZIP_DEFLATED)
    file_.close()

    f.seek(0)
    return f.read()


def __hashsum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def package_data_to_json(data):
    return {
        'chk': __hashsum(data),
        'data': b64encode(data)
    }


def load_package_from_fs(path):
    with open(path) as f:
        data = f.read()
    return package_data_to_json(data)


def create_transfer_package(path):
    data = __create_zip(path)
    return package_data_to_json(data)


def extract_transport_package(pkg, path):
    data_ = b64decode(pkg['data'])
    if __hashsum(data_) != pkg['chk']:
        raise TransferBadChkException()

    f = StringIO(data_)
    file_ = zipfile.ZipFile(f)
    file_.extractall(path)