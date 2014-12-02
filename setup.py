from setuptools import find_packages, setup


with open('README.rst') as f:
    readme = f.read()


setup(
    name='rattle',
    version='0.0.0',
    author='Curtis Maloney',
    description='Python templating tool',
    license='MIT',
    url='https://github.com/funkybob/rattle',
    packages=find_packages(),
    long_description=readme,
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
