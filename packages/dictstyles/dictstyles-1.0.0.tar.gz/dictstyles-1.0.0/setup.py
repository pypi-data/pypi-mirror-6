import os
import sys
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "dictstyles", "__version__.py")) as version_file:
    exec(version_file.read()) # pylint: disable=W0122

_INSTALL_REQUIERS = []

setup(name="dictstyles",
      classifiers = [
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          ],
      description="None",
      license="BSD3",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__, # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),

      url="https://github.com/vmalloc/dictstyles",

      install_requires=_INSTALL_REQUIERS,
      scripts=[],
      namespace_packages=[],

      entry_points = {
          "console_scripts": [
              "toggle_dict_style = dictstyles.main:main_entry_point",
              ]},
      )
