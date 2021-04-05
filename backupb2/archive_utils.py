import os
from os import path
import subprocess
from tarfile import TarFile
from tempfile import NamedTemporaryFile
import typing as t
from .backup_context import BackupContext

__all__ = ['upload_archive', 'add_sqlite_file']


def upload_archive(ctx: BackupContext,
                   dst: str,
                   create_archive: t.Callable[[
                       BackupContext, TarFile], None]
                   ) -> None:
    with NamedTemporaryFile(mode='rb', suffix='.tar.xz') as archive_file:
        ctx.logger.debug('Creating archive to %s', archive_file.name)
        with TarFile.open(archive_file.name, 'w:xz') as tar:
            create_archive(ctx, tar)

        ctx.upload_file(archive_file.name, dst)


def add_sqlite_file(ctx: BackupContext,
                    tar: TarFile,
                    src: t.Union[os.PathLike, str],
                    arcname: str) -> None:
    if not path.isfile(src):
        return

    with NamedTemporaryFile(mode='rb', suffix='.db') as db_backup_file:
        ctx.logger.debug('Dumping database from %s to %s',
                         src, db_backup_file.name)
        subprocess.run(
            ['sqlite3', str(src), f".backup '{db_backup_file.name}'"],
            check=True)

        # 元ファイルのメタデータを使用する
        src_stat = os.stat(src)
        ti = tar.gettarinfo(db_backup_file.name, arcname)
        ti.mtime = src_stat.st_mtime
        ti.mode = src_stat.st_mode
        ti.uid = src_stat.st_uid
        ti.gid = src_stat.st_gid
        ti.uname = ''
        ti.gname = ''

        with open(src, 'rb') as f:
            tar.addfile(ti, f)
