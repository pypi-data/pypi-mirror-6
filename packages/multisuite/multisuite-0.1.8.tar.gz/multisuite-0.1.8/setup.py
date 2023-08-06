import sys

from setuptools import setup

if sys.argv[-1] == 'publish':
    sys.argv = [sys.argv[0], 'sdist', 'upload']

setup(
        name="multisuite",
        version="0.1.8",
        author="Project MONK Developers",
        author_email="project-monk@dreserach-fe.de",
        py_modules = [
            "multisuite",
        ],
        entry_points = {
            'console_scripts' : [
                'multisuite = multisuite:main',
            ],
        },
        install_requires = [
            "nose >= 1.3.0",
        ],
        url="https://github.com/DFE/multisuite",
        license="LICENSE",
        description="run independent nose test suites together",
        long_description=open("README.rst").read(),
)
