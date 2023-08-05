import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

from viren import __version__


long_description = \
"""
See docs and report bugs at https://github.com/cberzan/viren.
"""

setup(
    name = "viren",
    version = __version__,
    packages = ["viren"],
    py_modules = ["distribute_setup"],

    # metadata for upload to PyPI
    author = "Constantin Berzan",
    author_email = "cberzan@gmail.com",
    description = "bulk-rename files using your editor",
    long_description = long_description,
    license = "MIT",
    keywords = "rename",
    url = "https://github.com/cberzan/viren",
    # download_url =

    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
    ],

    entry_points = {
        'console_scripts': [
            'viren = viren.viren:main',
        ],
    },
)
