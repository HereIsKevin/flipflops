[app]
title = FlipFlops
project_dir = ./
input_file = ./main.py
exec_directory = ./dist/
project_file = ../pyproject.toml
icon = ./resources/flipflops.icns

[python]
python_path = ./.venv/bin/python
packages = Nuitka==2.7

[qt]

[nuitka]
mode = standalone
extra_args = --quiet --noinclude-qt-translations
