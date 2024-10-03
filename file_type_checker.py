from glob import glob
from logging import debug

import puremagic
import mimetypes
import fleep
import filetype
from collections import Counter


class FileTypeChecker:
    def __init__(self, debug=False):
        self.debug = debug
        self.file_type_map = {
            "heif"  : "heic",
            "jpeg"  : "jpg",
            "x-flac": "flac",
        }
        self.content_type = {
            'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', "heif", "heic", "avif"},
            'audio': {'mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg', 'wma', '3gp', 'mpeg'},
        }

    def __get_file_type_puremagic(self, file_path):
        try:
            mime_type = puremagic.from_file(file_path)
            return mime_type[1:]
        except puremagic.PureError:
            return "unknown"

    def __get_file_type_fleep(self, file_path):
        with open(file_path, "rb") as file:
            info = fleep.get(file.read(128))
        return info.mime[0].split('/')[1] if info.mime else "unknown"

    def __get_file_type_filetype(self, file_path):
        kind = filetype.guess(file_path)
        return kind.mime.split("/")[1] if kind else "unknown"

    def __get_file_type_mimetypes(self, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type.split("/")[1] if mime_type is not None else "unknown"

    def get_file_type(self, file_path):
        file_type_candidates = [
            self.__get_file_type_puremagic(file_path),
            self.__get_file_type_fleep(file_path),
            self.__get_file_type_filetype(file_path),
            self.__get_file_type_mimetypes(file_path),
        ]
        for i in range(len(file_type_candidates)):
            file_type_candidates[i] = self.file_type_map.get(file_type_candidates[i], file_type_candidates[i])
        count = Counter(file_type_candidates)
        result_types = sorted(list(count.most_common(4)), key=lambda x: x[1], reverse=True)
        file_type = result_types[0][0]
        if len(result_types) > 1 and file_type == "unknown":
            if result_types[0][1] == result_types[1][1]:
                file_type = result_types[1][0]
        if file_type in self.content_type['image']:
            ret = f'image/{file_type}'
        elif file_type in self.content_type['audio']:
            ret = f'audio/{file_type}'
        else:
            ret = "unknown/unknown"
        if self.debug:
            return ret, file_type, file_type_candidates
        else:
            return ret
