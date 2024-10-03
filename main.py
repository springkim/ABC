import time

from tkinterdnd2 import DND_FILES, TkinterDnD
import os, sys
from tkinter import filedialog
from CTkScrollableDropdown import CTkScrollableDropdown, CTkScrollableDropdownFrame
import natsort
from collections import Counter
import customtkinter as ctk
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
from converter.image_converter import convert_image, convert_image_mt
from converter.audio_converter import convert_audio, convert_audio_mt
from file_type_checker import FileTypeChecker
from config import mltext, get_supported_extensions, change_language
import webbrowser

VERSION = "0.0.1"
DEBUG = False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


ctk.FontManager.load_font(resource_path("res/KoPubWorld Dotum Bold.ttf"))
# ctk.FontManager.load_font(resource_path("res/KoPubWorld Dotum Medium.ttf"))
# ctk.FontManager.load_font(resource_path("res/KoPubWorld Dotum Light.ttf"))
FONT = "KoPubWorld돋움체 Bold"


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.font = ctk.CTkFont(FONT, 16)
        self.title(mltext("ABOUT_TITLE"))
        self.geometry("300x100")
        self.resizable(False, False)

        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()
        self.github_address = f"https://github.com/springkim/ABC"

        title_label = ctk.CTkLabel(self, text=f"All Batch Converter {VERSION}", font=self.font)
        title_label.pack(pady=(20, 5))

        homepage_label = ctk.CTkLabel(self, text=self.github_address, font=self.font)
        homepage_label.pack(pady=(0, 20))
        homepage_label.bind("<Button-1>", self.open_url)

        self.after(10, self.center_window)

    def open_url(self, event):
        webbrowser.open(self.github_address)

    def center_window(self):
        self.update_idletasks()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        self.lift()
        self.focus_force()


class ScrollableFileList(ctk.CTkScrollableFrame):
    def __init__(self, master, add_files_callback, append_file_callback, check_file_type_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.ftc = FileTypeChecker()
        self.file_frames = []
        self.font = ctk.CTkFont(FONT, 16)
        self.header_font = ctk.CTkFont(FONT, 18, weight="bold")
        self.add_files_callback = add_files_callback
        self.append_file_callback = append_file_callback
        self.check_file_type_callback = check_file_type_callback

        self.grid_columnconfigure(0, weight=1)
        self.create_header()

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.drop)

        self.info_label = ctk.CTkLabel(self, text=mltext("HOW_TO_ADD_FILES"), font=self.font)
        self.info_label.grid(row=2, column=0, pady=30)

        self.bind("<Button-1>", self.on_click)

    def create_header(self):
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)

        self.header_type = ctk.CTkLabel(header_frame, text=mltext("HEADER_TYPE"), font=self.header_font, width=100, anchor="w", justify="left")
        self.header_type.grid(row=0, column=0, padx=(5, 10), sticky="w")
        self.header_name = ctk.CTkLabel(header_frame, text=mltext("HEADER_NAME"), font=self.header_font, anchor="w", justify="left")
        self.header_name.grid(row=0, column=1, padx=(0, 10), sticky="w")
        self.header_size = ctk.CTkLabel(header_frame, text=mltext("HEADER_SIZE"), font=self.header_font, width=100, anchor="e", justify="right")
        self.header_size.grid(row=0, column=2, padx=(0, 5), sticky="e")

        separator = ctk.CTkFrame(self, height=2, fg_color="gray")
        separator.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

    def add_file(self, file_path, file_type):
        def format_size(size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"

        if not self.file_frames:
            self.info_label.grid_forget()

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_str = format_size(file_size)

        frame = ctk.CTkFrame(self)
        frame.grid(row=len(self.file_frames) + 2, column=0, sticky="ew", padx=5, pady=2)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text=file_type, font=self.font, width=100, anchor="w", justify="left").grid(row=0, column=0, padx=(5, 10), sticky="w")
        ctk.CTkLabel(frame, text=file_name, font=self.font, anchor="w", justify="left").grid(row=0, column=1, padx=(0, 10), sticky="w")
        ctk.CTkLabel(frame, text=size_str, font=self.font, width=100, anchor="e", justify="right").grid(row=0, column=2, padx=(0, 5), sticky="e")

        self.file_frames.append(frame)
        self.append_file_callback(file_path, file_type)
        return True

    def clear_files(self):
        for frame in self.file_frames:
            frame.destroy()
        self.file_frames.clear()
        self.info_label.grid(row=2, column=0, pady=30)

    def drop(self, event):
        files = self.tk.splitlist(event.data)
        with ThreadPoolExecutor(max_workers=os.cpu_count() // 2) as pool:
            file_types = list(pool.map(self.ftc.get_file_type, files))
        for file, file_type in zip(files, file_types):
            self.add_file(file, file_type)
        self.check_file_type_callback()

    def on_click(self, event):
        if not self.file_frames:
            self.add_files_callback()
            self.check_file_type_callback()

    def refresh_language(self):
        self.header_type.configure(text=mltext("HEADER_TYPE"), font=self.header_font)
        self.header_name.configure(text=mltext("HEADER_NAME"), font=self.header_font)
        self.header_size.configure(text=mltext("HEADER_SIZE"), font=self.header_font)
        self.info_label.configure(text=mltext("HOW_TO_ADD_FILES"), font=self.font)
        pass


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ftc = FileTypeChecker()
        self.edit_menu_values = {
            "image": [f"{mltext('CVT_PREFIX')}{fmt}{mltext('CVT_POSTFIX')}" for fmt in get_supported_extensions('image')],
            "audio": [f"{mltext('CVT_PREFIX')}{fmt}{mltext('CVT_POSTFIX')}" for fmt in get_supported_extensions('audio')]
        }

        self.TkdndVersion = TkinterDnD._require(self)
        self.files = []
        # TODO
        # icon 바꾸기
        self.title("ABC")
        self.minsize(1200, 480)
        window_width = 1280
        window_height = 640
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.font = ctk.CTkFont(FONT, 16)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=3)
        self.menu_frame.grid_columnconfigure(3, weight=1)

        self.file_menu = ctk.CTkOptionMenu(self.menu_frame, width=200, font=self.font, dropdown_font=self.font)
        self.file_menu.set(mltext("FILE"))
        self.file_menu.grid(row=0, column=0, padx=3, pady=3)
        self.file_menu_dropdown = CTkScrollableDropdown(self.file_menu,
                                                        values=[mltext("APPEND_FILE"), mltext("CLEAR_LIST")],
                                                        command=self.file_menu_callback,
                                                        justify="left", font=self.font, scrollbar=False, button_height=30)

        self.edit_menu = ctk.CTkOptionMenu(self.menu_frame, width=200, font=self.font, dropdown_font=self.font)
        self.edit_menu.set(mltext("EDIT"))
        self.edit_menu.grid(row=0, column=1, padx=3, pady=3)
        self.edit_menu_dropdown = CTkScrollableDropdown(self.edit_menu,
                                                        values=[mltext("NOFILE")],
                                                        command=self.edit_menu_callback,
                                                        justify="left", font=self.font, scrollbar=False, button_height=30)

        self.lang_menu = ctk.CTkOptionMenu(self.menu_frame, width=200, font=self.font, dropdown_font=self.font)
        self.lang_menu.set(mltext("LANGUAGE"))
        self.lang_menu.grid(row=0, column=2, padx=3, pady=3)
        self.lang_menu_dropdown = CTkScrollableDropdown(self.lang_menu,
                                                        values=["한국어", "English"],
                                                        command=self.lang_menu_callback,
                                                        justify="left", font=self.font, scrollbar=False, button_height=30)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.menu_frame, width=200, height=27, corner_radius=5)
        self.progress_bar.set(0.0 if not DEBUG else 0.5)
        self.progress_bar.grid(row=0, column=3, padx=3, pady=3, sticky="w")
        if not DEBUG:
            self.progress_bar.grid_forget()

        # Theme
        theme_mode = ctk.get_appearance_mode().lower()
        self.switch_var = ctk.StringVar(value=theme_mode)
        self.theme_switch = ctk.CTkSwitch(self.menu_frame, text=mltext("THEME"), variable=self.switch_var, onvalue="dark", offvalue="light", font=self.font, command=self.theme_switch_callback)
        self.theme_switch.grid(row=0, column=4, padx=3, pady=1, sticky="e")

        # Info button
        self.help_button = ctk.CTkButton(self.menu_frame, text=mltext("INFO"), command=self.show_about, font=self.font)
        self.help_button.grid(row=0, column=5, padx=5, pady=5, sticky="e")

        self.file_list = ScrollableFileList(self, add_files_callback=self.add_files,
                                            append_file_callback=self.append_file,
                                            check_file_type_callback=self.check_file_type)
        self.file_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.toplevel_window = None
        self.queue = queue.Queue()

        self.dst_paths = []
        self.file_types = []
        self.files_len = 0

    def refresh_language(self):
        self.edit_menu_values = {
            "image": [f"{mltext('CVT_PREFIX')}{fmt}{mltext('CVT_POSTFIX')}" for fmt in get_supported_extensions('image')],
            "audio": [f"{mltext('CVT_PREFIX')}{fmt}{mltext('CVT_POSTFIX')}" for fmt in get_supported_extensions('audio')]
        }
        self.file_menu.set(mltext("FILE"))
        self.edit_menu.set(mltext("EDIT"))
        self.lang_menu.set(mltext("LANGUAGE"))

        self.file_menu_dropdown.configure(values=[mltext("APPEND_FILE"), mltext("CLEAR_LIST")], font=self.font)
        self.edit_menu_dropdown.configure(values=[mltext("NOFILE")], font=self.font)

        self.theme_switch.configure(text=mltext("THEME"), font=self.font)
        self.help_button.configure(text=mltext("INFO"), font=self.font)

        self.check_file_type()
        self.file_list.refresh_language()

    def theme_switch_callback(self):
        theme = self.switch_var.get()
        ctk.set_appearance_mode(theme)
        # self.theme_switch.configure(text=theme)

    def file_menu_callback(self, choice):
        if choice == mltext("APPEND_FILE"):
            self.add_files()
        elif choice == mltext("CLEAR_LIST"):
            self.clear_list()
        self.file_menu.set(mltext("FILE"))

    def edit_menu_callback(self, choice):
        filename_list = [os.path.splitext(os.path.basename(file))[0] for file in self.files]

        src_file_types = list(set([x.split('/')[0] for x in self.file_types]))
        if len(src_file_types) != 1:
            return

        duplicate_names = [item for item, count in Counter(filename_list).items() if count > 1]
        for s in [mltext("CVT_PREFIX"), mltext("CVT_POSTFIX")]:
            if len(s) != 0:
                choice = choice.replace(s, "")

        match choice:
            case "jpg" | "png" | "webp" | "bmp" | "heic" | "avif":
                self.convert_work_threading(convert_image_mt, f".{choice}", duplicate_names, self.files)
            case _:
                pass
        match choice:
            case "mp3" | "wav" | "m4a" | "ogg" | "flv":
                self.convert_work_threading(convert_audio_mt, f".{choice}", duplicate_names, self.files)
            case _:
                return

    def lang_menu_callback(self, choice):
        language_map = {
            "한국어"    : "KO",
            "English": "EN"
        }
        match choice:
            case "한국어" | "English":
                change_language(language_map[choice])
                self.refresh_language()
            case _:
                print("default")

    def convert_mt(self, convert_func, extension: str, duplicate_names: list[str], files: list[str], convert_check):
        self.progress_bar.grid(row=0, column=3, padx=3, pady=3, sticky="w")
        params = [(file, extension, duplicate_names) for file in files]
        completed = 0
        total = len(files)

        with ThreadPoolExecutor(max_workers=os.cpu_count() // 2) as pool:
            future_to_param = {pool.submit(convert_func, param): param for param in params}

            for future in as_completed(future_to_param):
                try:
                    dst_path = future.result()
                    self.dst_paths.append(dst_path)
                except Exception as exc:
                    raise Exception(f'Unknown exception: {exc}')

                completed += 1
                value = completed / total
                self.progress_bar.set(value)
                self.queue.put((value, True))

        self.progress_bar.set(0.0)
        self.progress_bar.grid_forget()
        self.queue.put((1.0, False))
        convert_check()

    def convert_st(self, convert_func, extension: str, duplicate_names: list[str], files: list[str]):
        self.progress_bar.grid(row=0, column=3, padx=3, pady=3, sticky="w")
        completed = 0
        total = len(files)
        for file in files:
            dst_path = convert_func(file, extension, duplicate_names)
            self.dst_paths.append(dst_path)
            completed += 1
            value = completed / total
            self.progress_bar.set(value)
            self.queue.put((value, True))
        self.progress_bar.grid_forget()
        self.queue.put((1.0, False))

    def disable_menu(self):
        self.file_menu.configure(state="disabled")
        self.edit_menu.configure(state="disabled")
        self.lang_menu.configure(state="disabled")
        self.help_button.configure(state="disabled")
        self.theme_switch.configure(state="disabled")

    def enable_menu(self):
        self.file_menu.configure(state="normal")
        self.edit_menu.configure(state="normal")
        self.lang_menu.configure(state="normal")
        self.help_button.configure(state="normal")
        self.theme_switch.configure(state="normal")

    def convert_work_threading(self, convert_func, extension: str, duplicate_names: list[str], files: list[str]):
        self.disable_menu()
        worker_thread = threading.Thread(target=self.convert_mt, args=(convert_func, extension, duplicate_names, files, self.check_convert_progress))
        worker_thread.start()
        self.after(10, self.check_convert_progress)

    def check_convert_progress(self):
        is_working = True
        try:
            progress, is_working = self.queue.get(0)
            self.queue.task_done()
        except queue.Empty:
            pass
        if len(self.dst_paths) == len(self.files):
            if len(self.files) != self.files_len:
                self.after(10, self.check_convert_progress)
            else:
                self.queue = queue.Queue()
                self.file_list.clear_files()
                self.files.clear()
                self.dst_paths = natsort.humansorted(self.dst_paths)
                with ThreadPoolExecutor(max_workers=os.cpu_count() // 2) as pool:
                    file_types = list(pool.map(self.ftc.get_file_type, self.dst_paths))
                for dst_path, dst_type in zip(self.dst_paths, file_types):
                    self.file_list.add_file(dst_path, dst_type)
                self.files = self.dst_paths.copy()
                self.dst_paths.clear()
                self.files = natsort.humansorted(self.files)
                self.enable_menu()
                if len(self.files) != self.files_len:
                    raise Exception(f'Number of files are different: {self.files_len} != {len(self.files)}')

        elif is_working:
            self.after(10, self.check_convert_progress)

    def check_file_type(self):
        src_file_types = list(set([x.split('/')[0] for x in self.file_types]))
        if len(src_file_types) == 1:
            src_file_types = src_file_types[0].split('/')[0]
            self.edit_menu_dropdown.configure(values=self.edit_menu_values[src_file_types], font=self.font)
        else:
            self.edit_menu_dropdown.configure(values=[mltext("UNAVAILABLE")], font=self.font)

    def append_file(self, file, file_type):
        self.files.append(file)
        self.file_types.append(file_type)
        self.files_len = len(self.files)

    def add_files(self):
        tk_files = filedialog.askopenfilenames()
        tk_files = natsort.humansorted(tk_files)
        with ThreadPoolExecutor(max_workers=os.cpu_count() // 2) as pool:
            file_types = list(pool.map(self.ftc.get_file_type, tk_files))
        for file, file_type in zip(tk_files, file_types):
            self.file_list.add_file(file, file_type)
        self.check_file_type()

    def clear_list(self):
        self.file_list.clear_files()
        self.files.clear()
        self.file_types.clear()
        self.dst_paths.clear()
        self.edit_menu_dropdown.configure(values=[mltext("NOFILE")], font=self.font)

    def show_about(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = AboutWindow(self)
        else:
            self.toplevel_window.focus_force()
            self.toplevel_window.center_window()
            self.toplevel_window.attributes("-topmost", True)

        self.attributes("-disabled", True)
        self.toplevel_window.protocol("WM_DELETE_WINDOW", self.on_about_close)

    def on_about_close(self):
        self.toplevel_window.destroy()
        self.attributes("-disabled", False)
        self.lift()
        self.focus_force()


if __name__ == "__main__":
    ctk.set_appearance_mode("system")

    ctk.set_default_color_theme("blue")
    app = App()
    app.iconbitmap(resource_path("res/icon.ico"))
    app.mainloop()
