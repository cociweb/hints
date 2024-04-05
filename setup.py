#!/usr/bin/env python3
from pathlib import Path
import os
import importlib.util

import setuptools
from setuptools import setup


#_DIR = Path(__file__).parent
#_VERSION_PATH = _DIR / "hints" / "VERSION"

#__version__ = _VERSION_PATH.read_text(encoding="utf-8").strip()

#__all__ = ["__version__", "__name__", "__description__", "__author__", "__email__", "__license__", "__url__"]

#this_dir = Path(__file__).parent

DIR = Path(__file__).parent

requirements = []
requirements_path = DIR / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

        file_path = f"./hints/__init__.py"
        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        all = module.__all__
        print(all)

data_files = []

module_dir =  DIR
module_version = all[0]
module_name = all[1]
module_description = all[2]
module_author = all[3]
module_email = all[4]
module_license = all[5]
module_url = all[6]
module_package = all[7]
print(module_name)

# -----------------------------------------------------------------------------

setup(
    name=module_name,
    version=module_version,
    description=module_description,
    url=module_url,
    author=module_author,
    author_email=module_email,
    license=module_license,
    packages=setuptools.find_packages(),
    package_data={module_name: [str(p.relative_to(module_dir)) for p in data_files]},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="Spell-checker Home-Assistant",
)
