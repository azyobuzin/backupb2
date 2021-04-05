import os
import typing as t
import b2sdk.v1 as b2
import b2sdk.v1.exception as b2exc
from . import Uploader, path_like_obj

__all__ = ['B2Uploader', 'join_b2_path']


class B2Uploader(Uploader):
    b2_api: t.Optional[b2.B2Api]
    application_key_id: str
    application_key: str

    def __init__(self, application_key_id: str, application_key: str):
        self.b2_api = None
        self.application_key_id = application_key_id
        self.application_key = application_key

    def _get_api(self) -> b2.B2Api:
        if self.b2_api is None:
            self.b2_api = b2.B2Api(
                b2.InMemoryAccountInfo(), max_upload_workers=2)
            self.b2_api.authorize_account(
                'production', self.application_key_id, self.application_key)
        return self.b2_api

    def upload(self, src: path_like_obj, dst: str) -> bool:
        api = self._get_api()

        parsed_destination = b2.parse_sync_folder(dst, api)
        if not isinstance(parsed_destination, b2.B2Folder):
            raise ValueError('dst is not a string starting with b2://')

        us = b2.UploadSourceLocalFile(os.fspath(src))
        sha1 = us.get_content_sha1()

        # Try to get file info of the existing file
        try:
            with self.b2_api.session.download_file_from_url(
                parsed_destination.bucket.get_download_url(
                    parsed_destination.folder_name),
                (0, 0)  # No downloading the content
            ) as res:
                if res.headers.get('X-Bz-Info-large_file_sha1') == sha1:
                    # No need to upload
                    return False
        except b2exc.FileNotPresent:
            pass

        parsed_destination.bucket.upload(
            us,
            parsed_destination.folder_name,
            file_info={'large_file_sha1': sha1})
        return True

    @classmethod
    def fromenv(cls) -> 'B2Uploader':
        application_key_id = os.getenv('B2_APPLICATION_KEY_ID')
        if not application_key_id:
            raise ValueError('B2_APPLICATION_KEY_ID is empty')
        application_key = os.getenv('B2_APPLICATION_KEY')
        if not application_key:
            raise ValueError('B2_APPLICATION_KEY is empty')
        return cls(application_key_id, application_key)


def join_b2_path(path1: str, path2: str) -> str:
    if not path1.endswith('/'):
        path1 += '/'
    return path1 + path2
