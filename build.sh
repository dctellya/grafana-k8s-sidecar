#!/bin/bash

if [[ -d dist ]]; then
    rm -rf dist
fi

mkdir -p dist
cp -R src/. dist
cd dist
ls -pal
python3 -m venv .venv && .venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -U pip setuptools 
.venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt
rm requirements.txt
find $(pwd)/.venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+
cd ..

