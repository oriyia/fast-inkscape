#!/usr/bin/env python3
import subprocess as sp
import click
import pyperclip
import pathlib
import os
from appdirs import user_config_dir

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

roots_file =  user_config_directory / 'roots'
template_image = user_config_directory / 'template.svg'
config = user_config_directory / 'config.py'

@click.group()
def cli():
    pass


def inkscape(path):
    sp.Popen(['inkscape', str(path)])


@cli.command()
@click.argument('title')
@click.argument(
    'root',
    default=os.getcwd(),
    type=click.Path(exists=False, dir_okay=True, file_okay=False)
)
def create_image(title, root):
    root += '/images/'
    target_path = pathlib.Path(root).absolute()
    if not target_path.exists():
        target_path.mkdir()

    title = title.strip()
    title_image = title.replace(' ', '_').lower() + '.svg'

    target_path_image = target_path / title_image

    inkscape(target_path_image)
    # image_directory = pathlib.Path(root).absolute()
    # image_directory = os.environ['PWD'] + "/images/"


# def main():
#     # inkscape()
#     cli()
#     # print(os.environ["PWD"])

if __name__ == "__main__":
    cli()
