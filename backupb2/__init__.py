from datetime import datetime, timedelta
import logging
import os
from random import random
import time
import typing as t

__all__ = ['BackupContext', 'setup', 'create_context', 'cron']

from .backup_context import BackupContext
from .uploaders.b2_uploader import B2Uploader


def setup() -> None:
    logging.basicConfig(format='[%(asctime)s, %(levelname)s, %(name)s]\n%(message)s')
    logger = logging.getLogger('servermng.backup')
    debug = os.getenv('DEBUG') == '1'
    logger.setLevel(logging.DEBUG if debug else logging.INFO)


def create_context() -> BackupContext:
    logger = logging.getLogger('servermng.backup')
    uploader = B2Uploader.fromenv()
    return BackupContext(logger, uploader)


def cron(ctx: BackupContext,
         backup_func: t.Callable[[BackupContext], None],
         interval_secs: float) -> None:
    # 1% だけランダムに
    interval_error = interval_secs / 10

    while True:
        ctx.logger.info("Start backup")

        try:
            backup_func(ctx)
        except Exception as exc:
            ctx.logger.error('Failed to backup', exc_info=exc)

        wait_time = interval_secs + \
            (random() * interval_error) - (interval_error / 2)
        ctx.logger.info('Next backup at %s', datetime.now() +
                        timedelta(seconds=wait_time))
        time.sleep(wait_time)
