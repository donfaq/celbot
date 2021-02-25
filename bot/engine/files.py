import pathlib
import tempfile

import dropbox
from celery.utils.log import get_task_logger
from dropbox.files import FileMetadata


class StorageManager:
    """Wrapper around Dropbox library to access persisted storage"""
    __local_folder: pathlib.Path = None

    def __init__(self, access_token):
        self.logger = get_task_logger(self.__class__.__name__)
        self.dbx = dropbox.Dropbox(access_token)

    def __download_remote_folder(self) -> pathlib.Path:
        self.logger.info("Downloading remote folder")
        tmp_path = tempfile.mkdtemp()

        for entry in self.dbx.files_list_folder('', recursive=True).entries:
            if isinstance(entry, FileMetadata):
                src_path_str = entry.path_lower
                target_path = pathlib.Path(tmp_path + entry.path_lower)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                self.dbx.files_download_to_file(download_path=target_path, path=src_path_str)

        return pathlib.Path(tmp_path)

    def get_local_folder(self) -> pathlib.Path:
        if self.__local_folder:
            return self.__local_folder
        self.__local_folder = self.__download_remote_folder()
        return self.get_local_folder()
