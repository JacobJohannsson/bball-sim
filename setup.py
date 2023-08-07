from setuptools import setup, find_packages
from setuptools.command.install import install
from install import install_directory

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        install_directory()

setup(
    name="bball_games",
    version="0.1",
    packages=find_packages(),
    cmdclass={
        'install': CustomInstallCommand,
    },
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "bball_games=source.cli_entry:cli",
        ],
    },
)