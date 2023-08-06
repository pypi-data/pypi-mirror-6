"""Installer for marked
"""

from setuptools import setup, find_packages

setup(
    name='marked',
    description='Library/utility that converts HTML to markdown text',
    long_description=open('README.rst').read(),
    provides=['marked'],
    version='0.9.1',
    author='Wes Mason',
    author_email='wes@1stvamp.org',
    url='https://github.com/1stvamp/marked.py',
    install_requires=[
        'beautifulsoup4 >= 4.3',
        'markgen >= 0.9.6'
    ],
    packages=find_packages(exclude=['marked_tests']),
    license='BSD'
)
