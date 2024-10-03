from PIL import Image
import pillow_heif
import pillow_avif
import numpy as np
import os


def convert_image_mt(param):
    return convert_image(*param)


def convert_image(src_path: str, extension: str, duplicate_names: str | None = None):
    src_ext = os.path.splitext(src_path)[1].lower()[1:]
    if src_ext in ["heif", "heic", "avif"]:
        img = pillow_heif.open_heif(src_path, convert_hdr_to_8bit=False, bgr_mode=False)
        img = Image.fromarray(np.array(img))
    else:
        img = Image.open(src_path)

    if os.path.splitext(os.path.basename(src_path))[0] in duplicate_names:
        dst_path = src_path + extension
    else:
        dst_path = os.path.splitext(src_path)[0] + extension
    match extension:
        case ".jpg":
            img = img.convert('RGB')
            img.save(dst_path, quality=95)
        case ".png":
            imgc = 'RGBA' if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info) else 'RGB'
            img = img.convert(imgc)
            img.save(dst_path, optimize=False, compress_level=0)
        case ".webp":
            img.save(dst_path, lossless=True)
        case ".bmp":
            img.save(dst_path)
        case ".heic":
            pillow_heif.from_pillow(img).save(dst_path, quality=-1)
        case ".avif":
            img.save(dst_path, "AVIF")
        case default:
            pass

    if src_path != dst_path:
        os.remove(src_path)
    return dst_path


if __name__ == '__main__':
    print("PASS")
