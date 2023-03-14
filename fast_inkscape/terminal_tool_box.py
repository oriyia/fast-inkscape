import subprocess
import tempfile
import os
from pathlib import Path
from Xlib import X
import subprocess as sp
import pyperclip
from loguru import logger

from config import config
from constants import TARGET
# from key_replacement import create_events


def run_inkscape(path: str) -> int:
    result = sp.Popen([f"(inkscape {path} &) &"], shell=True)
    return result.returncode


def focus_to_inkscape():
    result = sp.Popen(["I3SOCK=$(i3 --get-socket) && i3-msg workspace 4"], shell=True)


def paste_code_latex_document(title: str):
    title = str(Path(title).stem)
    latex_code = '\n'.join((
        r"\begin{figure}[H]",
        rf"\centering \incfig{{{title}}}",
        rf"\caption{{{title}}} \label{{fig:{title}}}",
        r"\end{figure}"))
    pyperclip.copy(latex_code)


def save_image_pdf_extension(path_name_image: Path):
    pdf_path = path_name_image.parent / (path_name_image.stem + '.pdf')
    command = [
        'inkscape', str(path_name_image),
        '--export-area-page',
        '--export-dpi', '300',
        '--export-type=pdf',
        '--export-latex',
        '--export-filename', str(pdf_path)
    ]
    sp.Popen(command)


# Для копирования файлов файловой системы
def copy_file(file, target=None):
    extra_args = []
    if target != None:
        extra_args += ['-target', target]

    return subprocess.run(
        ['xclip', '-sel', 'clip'] + extra_args + [file],
        universal_newlines=True,
    )

# Для копирование своего текста в коде
def copy_text(string, target=None):
    extra_args = []
    if target != None:
        extra_args += ['-target', target]

    return subprocess.run(
        ['xclip', '-selection', 'c'] + extra_args,
        universal_newlines=True,
        input=string
    )

def get_clipboard(target=None):
    extra_args = []
    if target != None:
        extra_args += ['-target', target]

    result = subprocess.run(
        ['xclip', '-selection', 'clip', '-o'] + extra_args,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )
    stdout = result.stdout.strip()
    return stdout


def open_vim(filename):
    subprocess.run([
        f"alacritty -e nvim {filename}"
        # f"alacritty -e nvim {filename} | (sleep .3 && I3SOCK=$(i3 --get-socket) && i3-msg floating enable && i3-msg resize set 1240 480 && i3-msg border pixel 3 && i3-msg move position center)"
        # f"I3SOCK=$(i3 --get-socket) && i3-msg open floating toggle border pixel 3 resize grow left 1000, resize grow up 300, move position center exec 'alacritty -e nvim {filename}'"
        # f"(I3SOCK=$(i3 --get-socket) && i3-msg open floating toggle border pixel 3 resize grow left 1000, resize grow up 300, move position center && alacritty -e nvim {filename} &) &"
    ], shell=True)


def enter_text_in_editor():
    tmp_math_text = tempfile.NamedTemporaryFile(
        mode='w+', delete=False, suffix='.tex', dir='/home/oriyia/.tmp/'
    )
    tmp_math_text.write('$$')
    tmp_math_text.close()
    logger.info(f"Открываем текстовый редактор файл: {tmp_math_text.name}")

    open_vim(tmp_math_text.name)

    math_text = ""
    with open(tmp_math_text.name, 'r') as file:
        math_text = file.read().strip()
        print(f"формула latex: {math_text}")

    os.remove(tmp_math_text.name)

    if math_text != '$$':
        print('latex=' + math_text)
        svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg>
          <text
             style="font-size:{config['font_size']}px; font-family:'{config['font']}';-inkscape-font-specification:'{config['font']}, Normal';fill:#000000;fill-opacity:1;stroke:none;"
             xml:space="preserve"><tspan sodipodi:role="line" >{math_text}</tspan></text>
        </svg> """
        # copy(svg, target=TARGET)
        copy_text(math_text)


def run_rofi(message:str, stdin: str):
    result = subprocess.run([
        f"rofi -dmenu -p '{message}'"
    ], shell=True, stdout=subprocess.PIPE, text=True, input=stdin)
    return result


def run_search_window() -> Path:
    images = [image for image in config['objects_path'].glob('*.svg')]
    rofi_stdin_images = ''
    rofi_message = 'Выбери объект:'
    for image in images:
        name_image = image.stem
        rofi_stdin_images = rofi_stdin_images + str(name_image) + '\n'

    while True:
        result = run_rofi(rofi_message, rofi_stdin_images)
        if result.stdout == '':
            return Path('exit')
        choose_image = str(result.stdout).strip()
        choose_image = Path(choose_image + '.svg')

        # проверка выбрал ли я файл
        for image in images:
            image = Path(image.name)
            if image == choose_image:
                return choose_image
        rofi_message = 'Что-то не так. Выбери заново:'


def choose_file() -> str:
    object = run_search_window()
    if 'exit' == str(object):
        return str(object)
    path_image = config['objects_path'] / object
    return str(path_image)


def paste_object():
    path_image = choose_file()
    if path_image == 'exit':
        return 1
    else:
        copy_file(path_image, TARGET)
        return 0


def create_name_image(message: str) -> Path:
    result = run_rofi(message, '')
    name_image = result.stdout
    name_image = str(name_image).strip()
    if name_image == '':
        return Path('exit')
    elif name_image:
        normal_name_image = name_image.replace(' ', '_')
        return Path(normal_name_image + '.svg')
    else:
        return Path('unknown.svg')


def save_object(self):
    events = self.create_events('c', X.ControlMask)
    self.send_events(events)
    object = get_clipboard(TARGET)
    if not 'svg' in object:
        return

    save_images = [image for image in config['objects_path'].glob('*.svg')]
    is_object_saved = False
    message = 'Укажите имя:'
    while not is_object_saved:
        name_image = create_name_image(message)
        if str(name_image) == 'unknown.svg':
            return
        elif str(name_image) == 'exit':
            return
        for image in save_images:
            image = Path(image.name)
            if image == name_image:
                message = f"Файл {name_image} существует. Перезаписать?: y/n?"
                answer = run_rofi(message, '')
                if answer == 'n':
                    break
                (config['objects_path'] / name_image).write_text(object)
                is_object_saved = True
                break
        else:
            (config['objects_path'] / name_image).write_text(object)
            is_object_saved = True
