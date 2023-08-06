# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='proso-geography-data',
    version='0.9.7',
    description='Libs for manipulation with data from PROSO Geography project',
    author='Jan Papousek',
    author_email='jan.papousek@gmail.com',
    packages=['proso.geography'],
    license='Gnu GPL v3',
    url='https://github.com/proso/geography-data-libs/',
    install_requires=[
        'pandas>=0.13'
    ],
)
