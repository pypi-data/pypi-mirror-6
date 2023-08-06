#!/usr/bin/env python
from setuptools import setup, find_packages
import os.path
import sys


def lt27():
    v = sys.version_info
    return (v[0], v[1]) < (2, 7)


def lt33():
    v = sys.version_info
    return (v[0], v[1]) < (3, 3)


tests_require = [
    'nose>=1.0',
    'coverage'
]


ROOT_PATH = os.path.dirname(__file__)
with open(os.path.join(ROOT_PATH, "README.rst")) as f:
    long_description = f.read()


if lt27():
    tests_require.append('unittest2')


setup(
    name='pygments-gchangelog',
    description='Pygments lexer and style for Gentoo ChangeLog',
    long_description=long_description,
    url="https://github.com/bacher09/pygments-gchangelog",
    py_modules=['pygments_gchangelog'],
    install_requires=[
        'pygments'
    ],
    entry_points="""
    [pygments.lexers]
    chagelog = pygments_gchangelog:ChangelogLexer
    [pygments.styles]
    changelog = pygments_gchangelog:ChangelogStyle
    """,
    tests_require=tests_require,
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries",
    ],
    license="MIT",
    platforms='any',
    author='Slava Bacherikov',
    author_email='slava@bacherikov.org.ua',
    keywords=["pygments", "lexer", "changelog", "gentoo"],
    version="0.1"
)
