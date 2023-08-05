import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

try:
    import pypandoc
    DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    DESCRIPTION = 'Evercam API for Python'

LICENSE = open(
    os.path.join(os.path.dirname(__file__), 'LICENSE')).read().strip()

requests = 'requests >= 0.8.8'
if sys.version_info < (2, 6):
    requests += ', < 0.10.1'
install_requires = [requests]

setup(name='evercam',
      version='0.1.3',
      description='',
      author='Evercam',
      author_email='tomasz.jama@mhlabs.net',
      url='http://www.evercam.io/',
      install_requires=install_requires,
      license=LICENSE,
      long_description=DESCRIPTION,
      package_data = {
          '': ['LICENSE', '*.md']
      },
      packages=['evercam'],
      use_2to3=True,
      test_suite='unittest2.collector',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
      ],
)