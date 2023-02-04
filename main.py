#!/usr/bin/env python3
import subprocess as sp
import click
import pyperclip
import pathlib
import os
from appdirs import user_config_dir
import shutil

# command = [
#     'inkscape', filepath,
#     '--export-area-page',
#     '--export-dpi', '300',
#     '--export-type=pdf',
#     '--export-latex',
#     '--export-filename', pdf_path
# ]

name_images_directory = 'images'

user_config_directory = pathlib.Path(user_config_dir("fast_inkscape"))

if not user_config_directory.is_dir():
    user_config_directory.mkdir()

root_projects_file =  user_config_directory / 'root_projects'
template_image = user_config_directory / 'template.svg'
config_file = user_config_directory / 'config.py'

@click.group()
def cli():
    pass


def run_inkscape(path):
    sp.Popen(['inkscape', str(path)])


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

    normal_title_image = title.strip().replace(' ', '_').lower() + '.svg'

    path_name_image = str(path_image / normal_title_image)

    path_name_template_image = str(pathlib.Path(__file__).parent / 'template.svg')

    shutil.copy2(path_name_template_image, path_name_image)

    run_inkscape(path_name_image)


if __name__ == "__main__":
    cli()
