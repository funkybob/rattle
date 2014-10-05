import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='rattle',
    version='0.0.0',
    author='funkybob',
    description='Python templating tool',
    license='MIT',
    url='https://github.com/funkybob/rattle',
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=[
        'rply>=0.7.2',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
