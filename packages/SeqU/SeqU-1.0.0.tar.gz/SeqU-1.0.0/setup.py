#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014, Cameron White
import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="SeqU",
        version='1.0.0',
        description="Extended implemenation of the Unix seq command",
        license="BSD",
        author="Cameron Brandon White",
        author_email="cameronbwhite90@gmail.com",
        url="https://github.com/cameronbwhite/SeqU",
        py_modules = [
            "alpha", "roman",
        ],
        scripts = [
            "sequ",
        ],
        package_data={
            'SeqU': ["LISENSE", "README.md"],
        },
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: BSD License",
            "Intended Audience :: End Users/Desktop",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.3",
            "Topic :: Utilities",
        ],
        include_package_data=True,
    )
