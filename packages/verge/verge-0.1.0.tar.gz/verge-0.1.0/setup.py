import os

from setuptools import find_packages, setup

from verge import __version__


BIN_DIR = os.path.join(os.path.dirname(__file__), "bin")

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    long_description = readme.read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy"
]

setup(
    name="verge",
    version=__version__,
    packages=find_packages(),
    author="Julian Berman",
    author_email="Julian@GrayVines.com",
    classifiers=classifiers,
    description="Parallel execution inspired by GNU Parallel",
    license="MIT",
    long_description=long_description,
    scripts=[os.path.join(BIN_DIR, bin) for bin in os.listdir(BIN_DIR)],
    url="https://github.com/Julian/Verge",
)
