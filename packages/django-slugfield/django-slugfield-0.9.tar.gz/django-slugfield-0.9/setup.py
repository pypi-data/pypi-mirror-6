# coding=utf8

from setuptools import setup, find_packages

setup(
    name='django-slugfield',
    version='0.9',

    author='Dmitry Voronin',
    author_email='dimka665@gmail.com',

    url='https://github.com/dimka665/django-slugfield',
    description='Django manual slug field',

    packages=find_packages(),

    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='django slugfield slug field slugify url',
)
