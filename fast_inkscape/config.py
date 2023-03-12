from pathlib import Path
import os


def latex_document(latex):
    return r"""
        \documentclass[12pt,border=12pt]{standalone}
        \usepackage[utf8]{inputenc}
        \usepackage[T1]{fontenc}
        \usepackage{textcomp}
        \usepackage{amsmath, amssymb}
        \newcommand{\R}{\mathbb R}
        \begin{document}
    """ + latex + r"\end{document}"


path_main_script_file = Path(__file__).resolve()

config = {
    # For example '~/.config/rofi/ribbon.rasi' or None
    'rofi_theme': None,
    'terminal': 'alacritty -e',
    'i3_float_window': '| (sleep .3 && i3-msg floating enable && i3-msg resize set 1240 480 && i3-msg border pixel 3 && i3-msg move position center)',
    # Font that's used to add text in inkscape
    'font': 'monospace',
    'font_size': 10,
    'latex_document': latex_document,
    'config_path': Path('~/.config/inkscape-shortcut-manager/').expanduser(),
    'path_main_script_file': path_main_script_file,
    'root_script': path_main_script_file.parent,
    'objects_path': path_main_script_file.parent / 'samples/objects/',
    'template_path': path_main_script_file.parent / 'samples/template.svg',

}

# def import_file(name, path):
#     import importlib.util as util
#     spec = util.spec_from_file_location(name, path)
#     module = util.module_from_spec(spec)
#     spec.loader.exec_module(module)
#     return module

CONFIG_PATH = Path('~/.config/inkscape-shortcut-manager').expanduser()

# if (CONFIG_PATH / 'config.py').exists():
#     userconfig = import_file('config', CONFIG_PATH / 'config.py').config
#     config.update(userconfig)
