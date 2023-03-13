from pathlib import Path


# $PATH_SCRIPT/fast_inkscape/fast_inkscape/fast_inkscape.py
path_main_script_file = Path(__file__).resolve()

config = {
    # For example '~/.config/rofi/ribbon.rasi' or None
    'rofi_theme': None,
    'terminal': 'alacritty -e',
    'i3_float_window': '| (sleep .3 && i3-msg floating enable && i3-msg resize set 1240 480 && i3-msg border pixel 3 && i3-msg move position center)',
    # Font that's used to add text in inkscape
    'font': 'monospace',
    'font_size': 10,
    'config_path': Path('~/.config/inkscape-shortcut-manager/').expanduser(),

    'path_main_script_file': path_main_script_file,
    'root_script': path_main_script_file.parents[1],
    'objects_path': path_main_script_file.parents[1] / 'samples/objects/',
    'template_path': path_main_script_file.parents[1] / 'samples/template.svg',
    'desired_name_window': 'inkscape',
}

CONFIG_PATH = Path('~/.config/inkscape-shortcut-manager').expanduser()
