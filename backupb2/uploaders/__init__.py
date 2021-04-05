import abc
import os
import typing as t

__all__ = ['Uploader']

path_like_obj = t.Union[os.PathLike, str, bytes]


class Uploader(abc.ABC):
    @abc.abstractmethod
    def upload(self, src: path_like_obj, dst: str) -> bool:
        pass

    @abc.abstractclassmethod
    def download_if_exists(self, src: str, dst: path_like_obj) -> bool:
        pass
