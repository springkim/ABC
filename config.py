from dotted_dict import DottedDict
import locale

LANG = DottedDict({
    "KO": "KO",
    "EN": "EN",
})

MLTEXT = DottedDict({
    "APPEND_FILE"     : {
        LANG.KO: "파일 추가",
        LANG.EN: "Add File(s)"
    },
    "CLEAR_LIST"      : {
        LANG.KO: "목록 지우기",
        LANG.EN: "Clear List"
    },
    ##### MENU #####
    "FILE"            : {
        LANG.KO: "파일",
        LANG.EN: "File"
    },
    "EDIT"            : {
        LANG.KO: "편집",
        LANG.EN: "Edit"
    },
    "LANGUAGE"        : {
        LANG.KO: "언어",
        LANG.EN: "Language"
    },
    "THEME"           : {
        LANG.KO: "테마",
        LANG.EN: "Theme"
    },
    "INFO"            : {
        LANG.KO: "도움말",
        LANG.EN: "About"
    },
    ##### OTHERS #####
    "NOFILE"          : {
        LANG.KO: "파일 없음",
        LANG.EN: "No Files"
    },
    "UNAVAILABLE"     : {
        LANG.KO: "변환 불가능",
        LANG.EN: "Unable to Convert"
    },
    "CVT_PREFIX"      : {
        LANG.KO: "",
        LANG.EN: "Convert to "
    },
    "CVT_POSTFIX"     : {
        LANG.KO: "로 변환",
        LANG.EN: ""
    },
    ##### ScrollableFileList #####
    "HOW_TO_ADD_FILES": {
        LANG.KO: "여기에 파일을 드래그 앤 드롭하거나 클릭하여 추가하세요",
        LANG.EN: "Drag and drop or click to add files here"
    },
    "HEADER_TYPE"     : {
        LANG.KO: "종류",
        LANG.EN: "File Type"
    },
    "HEADER_NAME"     : {
        LANG.KO: "파일 이름",
        LANG.EN: "File Name"
    },
    "HEADER_SIZE"     : {
        LANG.KO: "크기",
        LANG.EN: "File Size"
    },
    ##### AboutWindow #####
    "ABOUT_TITLE"     : {
        LANG.KO: "프로그램 정보",
        LANG.EN: "About ABC"
    }
})
locale_lang_map = {
    'ko_KR': 'KO',
    'en_US': "EN",
    # 'ja_JP':"JP"
}
GLOBAL_CURRENT_LANGUAGE = locale_lang_map.get(locale.getdefaultlocale()[0], "EN")


def mltext(text):
    return MLTEXT[text][GLOBAL_CURRENT_LANGUAGE]


def get_languages():
    return LANG.keys()


def change_language(lang):
    global GLOBAL_CURRENT_LANGUAGE
    GLOBAL_CURRENT_LANGUAGE = lang


def get_supported_extensions(file_type):
    d = {
        'image': ["jpg", "png", "webp", "bmp", "heic", "avif"],
        'audio': ["mp3", "wav", "m4a", "ogg", "flv"],
    }
    return d[file_type]
