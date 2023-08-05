#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="file2py",
    packages=['file2py'],
    version="0.2.1",
    author="Krzysztof Warunek",
    author_email="kalmaceta@gmail.com",
    description="Allows to include/manage binary files in python source file.",
    license="MIT",
    keywords="binary, converter, pyside, qt, pyqt, file2py",
    url="https://github.com/kAlmAcetA/file2py",
    long_description='Allows to include/manage binary files in python source file.',
    scripts=['scripts/file2py', 'scripts/image2py'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX',
        'Development Status :: 3 - Alpha'
    ]
)
