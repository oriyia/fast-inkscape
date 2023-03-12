#!/usr/bin/env python3
import subprocess as sp
import click
import pyperclip
from pathlib import Path
import os
from appdirs import user_config_dir
import shutil
import re
from loguru import logger
from config import config
from terminal_tool_box import run_inkscape, save_image_pdf_extension


# Создание конфига
# user_config_directory = Path(user_config_dir("fast_inkscape"))
#
# if not user_config_directory.is_dir():
#     user_config_directory.mkdir()
#
# root_projects_file =  user_config_directory / 'root_projects'
# template_image = user_config_directory / 'template.svg'
# config_file = user_config_directory / 'config.py'
#
# # Создаем файлы конифга, если их нет
# if not root_projects_file.is_file():
#     root_projects_file.touch()
#
# if not template_image.is_file():
#     source = str(config['template_path'])
#     destination = str(template_image)
#     shutil.copy2(source, destination)


@click.group()
def cli():
    pass


def get_code_latex_template(title) -> str:
    title = title.parent / title.stem
    return '\n'.join((
            r"\begin{figure}[H]",
            rf"\centering \incfig{{{title}}}",
            rf"\caption{{{title}}} \label{{fig:{title}}}",
            r"\end{figure}"))


def create_normal_title_image(number_copy: int, title: str) -> str:
    title_image = title.strip().replace(' ', '_').lower() + str(number_copy) + '.svg'
    return title_image


def create_images_directory(root: str, name: str):
    target = root + name
    images_path = Path(target).absolute()
    if not images_path.exists():
        images_path.mkdir()
    return images_path


def create_image_base(title: str, root_project: str):
    image_directory_path = create_images_directory(root_project, 'images')
    normal_title_image = create_normal_title_image(0, title)

    path_name_image = image_directory_path / normal_title_image
    count_copy_image = 0

    while path_name_image.exists():
        count_copy_image += 1
        normal_title_image = create_normal_title_image(count_copy_image, title)
        path_name_image = image_directory_path / normal_title_image

    template_path = str(config['template_path'])
    shutil.copy2(template_path, str(path_name_image))
    return path_name_image, normal_title_image


@cli.command()
@click.argument('title')
@click.argument(
    'root_project',
    default=os.getcwd(),
    type=click.Path(exists=False, dir_okay=True, file_okay=False)
)
def create_image(title, root_project):
    """
    Function create title.svg in root_project and open with inkscape
    """
    path_name_image, normal_title_image = create_image_base(title, root_project)
    latex_code = get_code_latex_template(normal_title_image)
    pyperclip.copy(latex_code)

    result = run_inkscape(str(path_name_image))

    if result == 0:
        save_image_pdf_extension(path_name_image)


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
    image_directory_path = Path(root_project).absolute()

    if not re.search('incfig', title):
        return
    else:
        normal_title_image = re.search(r"{.*}", title)

    if normal_title_image:
        normal_title_image = normal_title_image.group(0)[1:-1] + '.svg'
    else:
        return

    path_name_image = image_directory_path / normal_title_image

    result = run_inkscape(str(path_name_image))

    if result == 0:
        save_image_pdf_extension(path_name_image)


if __name__ == "__main__":
    cli()
