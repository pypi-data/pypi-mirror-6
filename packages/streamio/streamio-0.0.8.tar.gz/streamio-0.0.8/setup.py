#!/usr/bin/env python

from glob import glob
from os import getcwd, path
from imp import new_module

from setuptools import setup


version = new_module("version")

exec(
    compile(
        open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "streamio"))), "streamio/version.py"), "r").read(),
        "streamio/version.py", "exec"
    ),
    version.__dict__
)


setup(
    name="streamio",
    version=version.version,
    description="reading, writing and sorting large files",
    long_description="{0:s}\n\n{1:s}".format(
        open("README.rst").read(), open("CHANGES.rst").read()
    ),
    author="James Mills",
    author_email="James Mills, j dot mills at griffith dot edu dot au",
    url="https://bitbucket.org/prologic/streamio",
    download_url="https://bitbucket.org/prologic/streamio/downloads/",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
    ],
    license="MIT",
    keywords="Python Large Files Reading Writing Sorting Streaming",
    platforms="POSIX",
    packages=["streamio"],
    scripts=glob("bin/*"),
    install_requires=[
        "py==1.4.19",
        "progress==1.2",
        "funcy==0.9",
        "unicodecsv==0.9.4",
    ],
    entry_points={
        "console_scripts": [
        ]
    },
    test_suite="tests.main.main",
    zip_safe=True
)
