# encoding: utf-8

try:
    from setuptools import setup, Extension
    uses_setuptools = True
except ImportError:
    from distutils.core import setup, Extension
    uses_setuptools = False


phpunserialize = Extension(
    "pakker.php._unserialize",
    sources=["pakker/php/_unserialize.c"])


if uses_setuptools:
    extra_kwargs = {
        "install_requires": ["singledispatch"]
    }
else:
    extra_kwargs = {}


setup(
    name="pakker",
    author="Andreas Stührk",
    author_email="andy-python@hammerhartes.de",
    description="Library for dealing with language-specific serialization "
                "formats.",
    license="BSD",
    url="http://buffer.io/+pakker/",
    packages=["pakker", "pakker.php", "pakker.tests"],
    version="0.2",
    ext_modules=[phpunserialize],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ],
    **extra_kwargs)
