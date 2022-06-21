from unittest.mock import patch
import os
from pathlib import Path
from os.path import join
from shutil import make_archive
from functools import reduce
from concurrent.futures import ThreadPoolExecutor

_os_path_isfile = os.path.isfile
_curpath = Path(".")

_ignorepath = ".backupignore"

with open(_ignorepath, "r") as f:
    _globs = [line.rstrip() for line in f]
# _globs = ['**/*.pyc', 'data/backup.zip']


def _accept(path):
    if Path(path) in reduce(lambda a, b: list(a) + list(b), map(lambda p: _curpath.glob(p), _globs)):
        return False
    return _os_path_isfile(path)


def _backup() -> str:
    try:
        with patch("os.path.isfile", side_effect=_accept):
            make_archive(join("data", "backup"), "zip")
    except Exception as e:
        return f"error: {e}"
    else:
        return "success"


def dobackup() -> str:
    with ThreadPoolExecutor(max_workers=20) as executor:
        future = executor.submit(_backup)
    return future.result()
