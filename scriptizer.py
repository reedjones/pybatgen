import os
import shutil
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.progress import track

console = Console()

APP_DATA_FOLDER = Path.home() / "AppData/Local/python_script_generator"

def create_app_data_folder():
    APP_DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    console.log(f"App data folder: {APP_DATA_FOLDER}")

@click.command()
@click.argument('entry_file', type=click.Path(exists=True))
@click.option('--include-dir', '-d', multiple=True, type=click.Path(exists=True), help='Additional directories to include.')
@click.option('--dest', '-o', type=click.Path(), help='Destination folder for scripts.')
@click.option('--venv', '-v', type=click.Path(), help='Virtual environment to use.')
def main(entry_file, include_dir, dest, venv):
    """Generate a .bat script for a Python program."""
    create_app_data_folder()
    destination = Path(dest) if dest else APP_DATA_FOLDER

    if not destination.exists():
        destination.mkdir(parents=True)
        console.log(f"Created destination directory: {destination}")

    entry_file_path = Path(entry_file)
    shutil.copy(entry_file_path, destination / entry_file_path.name)
    console.log(f"Copied entry file to {destination}")

    for dir_path in include_dir:
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

if __name__ == '__main__':
    main()
