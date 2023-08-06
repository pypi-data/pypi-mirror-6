# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

description = """
Compiler plugin to use Django Asset Pipeline package with Compass
"""

setup(
    name='django-pipeline-compass-compiler',
    version='0.1',
    description=description,
    long_description=open('README.md').read(),
    author='Javi Velasco',
    author_email='javier.velasco86@gmail.com',
    url='https://github.com/javivelasco/django-pipeline-compass-compiler',
    license='MIT License',
    platforms=['OS Independent'],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Utilities',
    ]
)
