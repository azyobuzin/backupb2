import logging
from .uploaders import Uploader, path_like_obj


class BackupContext:
    logger: logging.Logger
    uploader: Uploader

    def __init__(self, logger: logging.Logger, uploader: Uploader):
        self.logger = logger
        self.uploader = uploader

    def upload_file(self, src: path_like_obj, dst: str) -> None:
        self.logger.info('Uploading to %s', dst)
        uploaded = self.uploader.upload(src, dst)
        if uploaded:
            self.logger.info('Uploaded to %s', dst)
        else:
            self.logger.info('Upload skipped')
