# coding: utf-8
import sys
import os
from setuptools import setup, Extension
from functools import partial


# load version info
exec(open("peanut/version.py").read())


USE_CYTHON = True   # command line option, try-import, ...


Extension = partial(Extension, extra_compile_args=["-O3"])


ext = '.pyx' if USE_CYTHON else '.c'
extensions = [
    Extension("peanut.{}".format(filename), ["peanut/{}{}".format(filename, ext)])
    for filename in "postprocessing input output alignment bitencoding".split()]


if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, language="c++")


setup(
    name='peanut',
    version=__version__,
    author='Johannes Köster',
    author_email='johannes.koester@tu-dortmund.de',
    description='A massively parallel read mapper using OpenCL.',
    license='MIT',
    url='https://bitbucket.org/johanneskoester/peanut',
    packages=['peanut'],
    install_requires=["cython>=0.19", "numpy>=1.7", "pyopencl>=2013.1"],
    ext_modules=extensions,
    entry_points={"console_scripts": ["peanut = peanut:main"]},
    package_data={'': ['*.cl']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
