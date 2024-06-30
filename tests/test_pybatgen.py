#!/usr/bin/env python

"""Tests for `pybatgen` package."""

import pytest
import os
import shutil
from click.testing import CliRunner
from pathlib import Path
from pybatgen import APP_DATA_FOLDER
from cli import main




@pytest.fixture(scope="function")
def temp_app_data_folder():
    """Fixture to create and clean up a temporary app data folder."""
    temp_folder = APP_DATA_FOLDER / "test"
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
    temp_folder.mkdir(parents=True)
    yield temp_folder
    if temp_folder.exists():
        shutil.rmtree(temp_folder)


def test_create_app_data_folder(temp_app_data_folder):
    assert temp_app_data_folder.exists()


def test_generate_bat_script(temp_app_data_folder):
    runner = CliRunner()
    entry_file = temp_app_data_folder / "test_script.py"
    entry_file.write_text("print('Hello, World!')")

    result = runner.invoke(main, [str(entry_file)])
    assert result.exit_code == 0
    bat_script = temp_app_data_folder / "test_script.bat"
    assert bat_script.exists()
    assert (
        bat_script.read_text()
        == f"@echo off\n{os.sys.executable} {temp_app_data_folder / 'test_script.py'} %*\n"
    )


def test_include_dir(temp_app_data_folder):
    runner = CliRunner()
    entry_file = temp_app_data_folder / "test_script.py"
    entry_file.write_text("print('Hello, World!')")

    include_dir = temp_app_data_folder / "include_dir"
    include_dir.mkdir()
    (include_dir / "dummy_file.txt").write_text("dummy content")

    result = runner.invoke(main, [str(entry_file), "--include-dir", str(include_dir)])
    assert result.exit_code == 0
    copied_include_dir = temp_app_data_folder / "include_dir"
    assert copied_include_dir.exists()
    assert (copied_include_dir / "dummy_file.txt").read_text() == "dummy content"


def test_custom_dest(temp_app_data_folder):
    runner = CliRunner()
    entry_file = temp_app_data_folder / "test_script.py"
    entry_file.write_text("print('Hello, World!')")

    custom_dest = temp_app_data_folder / "custom_dest"

    result = runner.invoke(main, [str(entry_file), "--dest", str(custom_dest)])
    assert result.exit_code == 0
    copied_entry_file = custom_dest / "test_script.py"
    assert copied_entry_file.exists()
    assert copied_entry_file.read_text() == "print('Hello, World!')"

    bat_script = custom_dest / "test_script.bat"
    assert bat_script.exists()
    assert (
        bat_script.read_text()
        == f"@echo off\n{os.sys.executable} {custom_dest / 'test_script.py'} %*\n"
    )


def test_venv_option(temp_app_data_folder):
    runner = CliRunner()
    entry_file = temp_app_data_folder / "test_script.py"
    entry_file.write_text("print('Hello, World!')")

    venv_path = temp_app_data_folder / "venv"

    result = runner.invoke(main, [str(entry_file), "--venv", str(venv_path)])
    assert result.exit_code == 0

    bat_script = temp_app_data_folder / "test_script.bat"
    assert bat_script.exists()
    assert (
        bat_script.read_text()
        == f"@echo off\ncall {venv_path}\\Scripts\\activate.bat\n{os.sys.executable} {temp_app_data_folder / 'test_script.py'} %*\n"
    )
