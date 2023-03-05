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
    'script_path': Path(os.getcwd()),
    'objects_path': Path(os.path.realpath(os.path.dirname(__file__))) / 'samples/objects',
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
