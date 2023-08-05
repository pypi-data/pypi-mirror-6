# coding: utf8

#from mzsudoku.ez_setup import use_setuptools
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

def make_setup():
    setup(
        name = "mzsudoku",
        version = "1.0.0",
        #packages = ["mzsudoku"], # find_packages(),
        py_modules = ["mzsudoku", "ez_setup"],
        author = "Zvolsky Mirek",
        author_email = "mirek.zvolsky@gmail.com",
        description = "Module/script to solve classical 9x9 Sudoku step by step",
        license = "open source GPL",
        keywords = "sudoku",
        url = "http://www.github.com/zvolsky/sudoku/",   # project home page
        # could also include long_description, download_url, classifiers, etc.
    ) 

if __name__ == '__main__':
    make_setup()