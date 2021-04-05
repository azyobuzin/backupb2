import os
from os import path
import subprocess
from tarfile import TarFile
from tempfile import NamedTemporaryFile
import typing as t
from .backup_context import BackupContext

__all__ = ['upload_archive', 'add_sqlite_file', 'download_and_extract']

path_like_obj = t.Union[os.PathLike, str, bytes]


def upload_archive(ctx: BackupContext,
                   dst: str,
                   create_archive: t.Callable[[
                       BackupContext, TarFile], None]
                   ) -> None:
    with NamedTemporaryFile(mode='wb', suffix='.tar.xz') as archive_file:
        ctx.logger.debug('Creating archive to %s', archive_file.name)
        with TarFile.open(fileobj=archive_file, mode='w:xz') as tar:
            create_archive(ctx, tar)
        archive_file.flush()

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


def download_and_extract(ctx: BackupContext, src: str, dst: path_like_obj) -> bool:
    ctx.logger.info('Restoring from %s to %s', src, dst)

    with NamedTemporaryFile(mode='rb') as download_dst:
        if not ctx.download_file_if_exists(src, download_dst.name):
            ctx.logger.info('No backup is found')
            return False

        ctx.logger.debug('Extracting to %s', dst)
        os.makedirs(dst, exist_ok=True)

        with TarFile.open(fileobj=download_dst, mode='r:*') as tar:
            tar.extractall(dst, numeric_owner=True)

    return True
