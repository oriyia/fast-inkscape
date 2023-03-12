import subprocess
from config import config
import tempfile
import os
from pathlib import Path
from Xlib import X
from constants import TARGET


def copy_file(file, target=None):
    extra_args = []
    if target != None:
        extra_args += ['-target', target]

    return subprocess.run(
        ['xclip', '-sel', 'clip'] + extra_args + [file],
        universal_newlines=True,
    )

def copy_text(string, target=None):
    extra_args = []
    if target != None:
        extra_args += ['-target', target]

    return subprocess.run(
        ['xclip', '-selection', 'c'] + extra_args,
        universal_newlines=True,
        input=string
    )

def get(target=None):
    extra_args = []
    if target != None:
        extra_args += ['-target', target]

    result = subprocess.run(
        ['xclip', '-selection', 'c', '-o'] + extra_args,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    # returncode = result.returncode
    stdout = result.stdout.strip()
    return stdout


def open_vim(filename):
    subprocess.run([
        f"alacritty -e nvim {filename} | (sleep .3 && i3-msg floating enale && i3-msg resize set 1240 480 && i3-msg border pixel 3 && i3-msg move position center)"
        # f"i3-msg open floating toggle border pixel 3 resize grow left 1000, resize grow up 300, move position center exec 'alacritty -e nvim {filename}'"
    ], shell=True)


def create_name_image(message):
    result = subprocess.run([f"rofi -dmenu"], shell=True, stdout=subprocess.PIPE, text=True, input='')
    name_image = result.stdout
    name_image = str(name_image).strip()
    if name_image:
        normal_name_image = name_image.replace(' ', '_')
        return Path(normal_name_image + '.svg')
    else:
        return 'None'


def save_image(self):
    svg = get(TARGET)
    if not 'svg' in svg:
        return

    save_images = config['objects_path'].glob('*.svg')
    coincidence = True
    message = 'Create_name?:'
    while coincidence:
        new_image = create_name_image(message)
        answer = 'None'
        if new_image == 'None':
            return
        for image in save_images:
            image = Path(image.name)
            if image == new_image:
                message = f"File_{new_image}_exists._Overwrite:_y/n?"
                answer = create_name_image(message)
                if answer == 'y':
                    (config['objects_path'] / f"{new_image}").write_text(svg)
                    coincidence = False
                    break
                elif answer == 'n':
                    break
        if answer == 'None':
            (config['objects_path'] / f"{new_image}").write_text(svg)
            coincidence = False


def enter_text_in_editor(compile_latex) -> str:
    tmp_math_text = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tex')
    tmp_math_text.write('$$')
    tmp_math_text.close()

    open_vim(tmp_math_text.name)

    math_text = ""
    with open(tmp_math_text.name, 'r') as file:
        math_text = file.read().strip()
        print(f"формула latex: {math_text}")

    os.remove(tmp_math_text.name)

    if math_text != '$$':
        print('latex=' + math_text)
        if not compile_latex:
            svg = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg>
              <text
                 style="font-size:{config['font_size']}px; font-family:'{config['font']}';-inkscape-font-specification:'{config['font']}, Normal';fill:#000000;fill-opacity:1;stroke:none;"
                 xml:space="preserve"><tspan sodipodi:role="line" >{math_text}</tspan></text>
            </svg> """
            # copy(svg, target=TARGET)
    return math_text


def run_search_window():
    save_images = config['objects_path'].glob('*.svg')
    string_images = ''
    not_file = ''
    for image in save_images:
        name_image = image.stem
        string_images = string_images + str(name_image) + '\n'
    result = subprocess.run([
        "rofi -dmenu"
    ], shell=True, stdout=subprocess.PIPE, text=True, input=string_images)
    new_image = str(result.stdout).strip()
    new_image = Path(new_image + '.svg')
    save_images = config['objects_path'].glob('*.svg')
    for image in save_images:
        image = Path(image.name)
        if image == new_image:
            return new_image
        not_file = image
    return not_file


def choose_file() -> str:
    object = run_search_window()
    path_image = config['objects_path'] / object
    return str(path_image)
