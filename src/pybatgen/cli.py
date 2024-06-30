"""Console script for pybatgen."""

import os
import shutil
import sys
from pathlib import Path
import click
import typer
from rich.console import Console
from rich.progress import track
from typing_extensions import Annotated
from typing import List, Optional
from rich_pixels import Pixels
from rich.segment import Segment
from rich.style import Style

console = Console()
app = typer.Typer()

APP_DATA_FOLDER = Path.home() / "AppData/Local/python_script_generator"


def banner():
    here = Path(__file__).resolve().parent
    art_path = here / "banner.txt"
    with open(art_path, "r") as f:
        art = f.read()
        # """ /::::\  \    \::/_/~~~~"""
    mapping = {
        "~": Segment(" ", Style.parse("red on yellow")),
        ":": Segment(" ", Style.parse("white on black")),
        "/": Segment(" ", Style.parse("white on blue")),
        "\\": Segment(" ", Style.parse("blue on yellow")),
    }
    pixels = Pixels.from_ascii(art, mapping)
    console.print(pixels)


def create_app_data_folder():
    APP_DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    console.log(f"App data folder: {APP_DATA_FOLDER}")


@app.command()
def main(
    entry: Annotated[
        Path,
        typer.Option(
            default=None,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="The main entry file \nthe generated .bat file will execute and pass arguments to this file",
        ),
    ],
    dest: Annotated[
        Path,
        typer.Option(
            default=APP_DATA_FOLDER,
            exists=True,
            dir_okay=True,
            writable=True,
            resolve_path=True,
            help="Destination folder for scripts.",
        ),
    ],
    venv: Annotated[
        Optional[Path],
        typer.Option(
            default=None,
            exists=True,
            dir_okay=True,
            writable=False,
            readable=False,
            resolve_path=True,
            help="Virtual environment to use.",
        ),
    ],
    includes: Annotated[
        Optional[List[Path]],
        typer.Option(
            default=None,
            exists=True,
            file_okay=True,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="Additional paths to include.",
        ),
    ] = None,
):
    if not includes:
        includes = []
    elif includes and not isinstance(includes, list):
        includes = [includes]
    create_app_data_folder()
    destination = Path(dest)

    if not destination.exists():
        destination.mkdir(parents=True)
        console.log(f"Created destination directory: {destination}")

    entry_file_path = Path(entry)
    shutil.copy(entry_file_path, destination / entry_file_path.name)
    console.log(f"Copied entry file to {destination}")

    for dir_path in includes:
        dir_path = Path(dir_path)
        if dir_path.is_dir():
            dest_dir = destination / dir_path.name
            shutil.copytree(dir_path, dest_dir, dirs_exist_ok=True)
            console.log(f"Copied directory {dir_path} to {dest_dir}")

    bat_script_path = destination / f"{entry_file_path.stem}.bat"
    with bat_script_path.open("w") as bat_file:
        bat_file.write(f"@echo off\n")
        if venv:
            bat_file.write(f"call {venv}\\Scripts\\activate.bat\n")
        bat_file.write(f"{sys.executable} {destination / entry_file_path.name} %*\n")

    console.log(f"Generated .bat script: {bat_script_path}")


if __name__ == "__main__":
    banner()
    app()
