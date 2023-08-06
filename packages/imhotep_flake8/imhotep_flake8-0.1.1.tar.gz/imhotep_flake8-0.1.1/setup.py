from setuptools import setup

setup(
    name = 'imhotep_flake8',
    packages = ['imhotep_flake8'], 
    version = '0.1.1',
    description = 'An imhotep plugin for flake8 validation.',
    author = 'Giorgos Logiotatidis',
    author_email = 'giorgos@mozilla.com',
    url = 'https://github.com/glogiotatidis/imhotep_flake8',
    download_url = 'https://github.com/glogiotatidis/imhotep_flake8/tarball/0.1', 
    keywords = ['testing', 'imhotep'], 
    classifiers = [],
    requires=['flake8'],
    entry_points={
        'imhotep_linters': [
            '.py = imhotep_flake8.plugin:Flake8Linter'
        ],
    },
)
