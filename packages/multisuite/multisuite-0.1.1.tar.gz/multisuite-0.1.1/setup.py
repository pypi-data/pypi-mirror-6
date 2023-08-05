from setuptools import setup

setup(
        name="multisuite",
        version="0.1.1",
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
        url="https://github.com/DFE/multisuite",
        license="LICENSE",
        description="run independent nose test suites together",
        long_description=open("README.rst").read(),
)
