import os
from pydub import AudioSegment


def convert_audio_mt(param):
    return convert_audio(*param)


def convert_audio(src_path: str, extension: str, duplicate_names: str | None = None):
    try:
        src_ext = os.path.splitext(src_path)[1].lower()[1:]

        snd = AudioSegment.from_file(src_path)

        if os.path.splitext(os.path.basename(src_path))[0] in duplicate_names:
            dst_path = src_path + extension
        else:
            dst_path = os.path.splitext(src_path)[0] + extension
        match extension:
            case ".mp3" | ".wav" | ".ogg" | ".flv":
                snd.export(dst_path, format=extension[1:])
            case ".m4a":
                snd.export(dst_path, format="ipod")
            case _:
                pass
        if src_path != dst_path:
            os.remove(src_path)
        return dst_path
    except Exception as e:
        print(e)
        exit()
