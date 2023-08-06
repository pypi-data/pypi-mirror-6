# coding: utf-8
from setuptools import find_packages, setup

pkgname = "vdt.versionplugin.default"

setup(name=pkgname,
      version="0.0.2",
      description="Default Version Increment Plugin for GIT",
      author="Lars van de Kerkhof",
      author_email="lars@devopsconsulting.nl",
      maintainer="Lars van de Kerkhof",
      maintainer_email="lars@devopsconsulting.nl",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['vdt', 'vdt.versionplugin'],
      zip_safe=True,
      install_requires=[
          "setuptools",
          "vdt.version",
      ],
      entry_points={},
)
