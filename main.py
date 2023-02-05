#!/usr/bin/env python3
import subprocess as sp
import click
import pyperclip
import pathlib
import os
from appdirs import user_config_dir
import shutil
import re

# command = [
#     'inkscape', filepath,
#     '--export-area-page',
#     '--export-dpi', '300',
#     '--export-type=pdf',
#     '--export-latex',
#     '--export-filename', pdf_path
# ]

name_images_directory = 'images'

# Создание конфига
user_config_directory = pathlib.Path(user_config_dir("fast_inkscape"))

if not user_config_directory.is_dir():
    user_config_directory.mkdir()

root_projects_file =  user_config_directory / 'root_projects'
template_image = user_config_directory / 'template.svg'
config_file = user_config_directory / 'config.py'

# Создаем файлы конифга, если их нет
if not root_projects_file.is_file():
    root_projects_file.touch()

if not template_image.is_file():
    source = str(pathlib.Path(__file__).parent / 'template.svg')
    destination = str(template_image)
    shutil.copy2(source, destination)


@click.group()
def cli():
    pass


def run_inkscape(path):
    sp.Popen(['inkscape', str(path)])


def get_code_latex_template(title):
    return '\n'.join((
            r"\begin{figure}[H]",
            rf"\centering \incfig{{{title}}}",
            rf"\caption{{{title}}} \label{{fig:{title}}}",
            r"\end{figure}"))


# def save_image_pdf_extension():
#     command = [
#         'inkscape', filepath,
#         '--export-area-page',
#         '--export-dpi', '300',
#         '--export-type=pdf',
#         '--export-latex',
#         '--export-filename', pdf_path
#     ]
#     sp.Popen(command)


@cli.command()
@click.argument('title')
@click.argument(
    'root_project',
    default=os.getcwd(),
    type=click.Path(exists=False, dir_okay=True, file_okay=False)
)
def create_image(title, root_project):
    """
    Function create image.svg and open with inkscape
    """
    root_project = root_project + '/images/'
    path_image = pathlib.Path(root_project).absolute()

    if not path_image.exists():
        path_image.mkdir()

    def create_normal_title_image(number_copy):
        normal_title_image = title.strip().replace(' ', '_').lower() + str(number_copy) + '.svg'
        return normal_title_image

    normal_title_image = create_normal_title_image(0)

    path_name_image = path_image / normal_title_image

    count_copy_name_image = 0

    while path_name_image.exists():
        count_copy_name_image += 1
        normal_title_image = create_normal_title_image(count_copy_name_image)
        path_name_image = path_image / normal_title_image

    path_name_image = str(path_name_image)

    path_name_template_image = str(pathlib.Path(__file__).parent / 'template.svg')

    shutil.copy2(path_name_template_image, path_name_image)

    name_image_without_extension = normal_title_image[:-4]
    latex_code = get_code_latex_template(name_image_without_extension)
    pyperclip.copy(latex_code)

    run_inkscape(path_name_image)


@cli.command()
@click.argument('title')
@click.argument(
    'root_project',
    default=os.getcwd(),
    type=click.Path(exists=False, dir_okay=True, file_okay=False)
)
def edit_image(title, root_project):
    """
    Function edit image.svg and open with inkscape
    """
    root_project = root_project + '/images/'
    path_image = pathlib.Path(root_project).absolute()

    if not re.search('incfig', title):
        return
    else:
        normal_title_image = re.search(r"{.*}", title)

    if normal_title_image:
        normal_title_image = normal_title_image.group(0)[1:-1] + '.svg'
    else:
        return

    path_name_image = str(path_image / normal_title_image)

    run_inkscape(path_name_image)


if __name__ == "__main__":
    cli()
