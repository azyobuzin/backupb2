# backupb2

A Library or Container Image to backup files to Backblaze B2

[Docker Hub](https://hub.docker.com/r/azyobuzin/backupb2)

## Example Script

```python
# backup.py

# Environment variables:
# APP_ROOT=/data
# BACKUP_DESTINATION=b2://bucket/path.tar.xz
# B2_APPLICATION_KEY_ID=
# B2_APPLICATION_KEY=

import os
from pathlib import Path
import sys
from tarfile import TarFile, TarInfo
import typing as t
from backupb2 import *
from backupb2.archive_utils import *

APP_ROOT = os.getenv('APP_ROOT')
if not APP_ROOT: sys.exit('APP_ROOT is empty')
APP_ROOT = Path(APP_ROOT)

BACKUP_DESTINATION = os.getenv('BACKUP_DESTINATION')
if not BACKUP_DESTINATION: sys.exit('BACKUP_DESTINATION is empty')

def create_archive(ctx: BackupContext, tar: TarFile) -> None:
    def ffilter(tarinfo: TarInfo) -> t.Optional[TarInfo]:
        # Exclude SQLite file
        if tarinfo.name.startswith('./db.sqlite3'):
            return None
        return tarinfo

    tar.add(APP_ROOT, '.', filter=ffilter)
    add_sqlite_file(ctx, tar, APP_ROOT / 'db.sqlite3', './db.sqlite3')

def run_backup(ctx: BackupContext) -> None:
    upload_archive(ctx, BACKUP_DESTINATION, create_archive)

if __name__ == '__main__':
    setup()
    ctx = create_context()
    INTERVAL = 1 * 24 * 60 * 60 # 1 day
    cron(ctx, run_backup, INTERVAL)
```

## Reference

### Module: backupb2

```python
# Configures `logging` module.
def setup() -> None: ...

# Creates an uploader instance with the given environment variables (B2_APPLICATION_KEY_ID and B2_APPLICATION_KEY).
def create_context() -> BackupContext: ...

# Calls `backup_func` repeatedly. This function never returns.
def cron(ctx: BackupContext,
         backup_func: Callable[[BackupContext], None],
         interval_secs: float) -> None: ...

class BackupContext:
  # Uploads a file.
  # `dst` is a string with "b2://bucket/path" format
  def upload_file(self, src: Union[os.PathLike, str, bytes], dst: str) -> None: ...
```

### Module: backupb2.archive_utils

```python
# Makes an tar file and uploads it.
# `dst` is a string with "b2://bucket/path" format
# `create_archive` is a function which adds files to the second argument
def upload_archive(ctx: BackupContext,
                   dst: str,
                   create_archive: Callable[[BackupContext, TarFile], None]
                   ) -> None: ...

# Adds SQLite3 database file to the tar file.
# This function can be used in `create_archive` of `upload_archve`.
# This function uses `.backup` command of SQLite to make a copy of the database file.
# `src` is a path to SQLite3 database file
# `arcname` is a path in the tar file
def add_sqlite_file(ctx: BackupContext,
                    tar: TarFile,
                    src: t.Union[os.PathLike, str],
                    arcname: str) -> None: ...
```
