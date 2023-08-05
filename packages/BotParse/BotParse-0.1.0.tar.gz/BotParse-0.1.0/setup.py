#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013, Cameron White
import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="BotParse",
        version='0.1.0',
        description="A modified version of argparse to make bot making easer",
        license="BSD",
        author="Cameron Brandon White",
        author_email="cameronbwhite90@gmail.com",
        url="https://github.com/cameronbwhite/BotParse",
        download_url="https://github.com/cameronbwhite/BotParse/downloads",
        provides=[
            "BotParse",
        ],
        py_modules = [
            "botparse",
        ],
        package_data={
            'PyOLP': ["LICENSE", "README.md"],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: BSD License",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        include_package_data=True,
    )
