import os
import fleep
import tkinterdnd2
import pyperclip

fleep_path = os.path.dirname(fleep.__file__)
fleep_data_json_path = os.path.join(fleep_path, 'data.json').replace('\\', '/')
tkdnd_path = os.path.dirname(tkinterdnd2.__file__).replace('\\', '/')

args = [
    '--name=ABC',
    '--onefile',
    '--windowed',
    '--icon=res/icon.ico',
    '--add-data "res/KoPubWorld Dotum Bold.ttf;res"',
    '--add-data "res/icon.ico;res"',
    f'--add-data "{fleep_data_json_path}:fleep"',
    f'--add-data "{tkdnd_path}:tkinterdnd2"',
    f'--add-binary "{tkdnd_path}/tkdnd:tkdnd"',
    'main.py',
]
command = 'pyinstaller' + ' ' + ' '.join(args)
print(command)

pyperclip.copy(command)

print("The above command has been copied to the clipboard, paste it in the console and run.")
