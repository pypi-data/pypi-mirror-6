import sys

from setuptools import setup
from setuptools import find_packages


if sys.version_info[0] == 3:
    LONG_DESCRIPTION = open('README', encoding='utf-8').read()
else:
    LONG_DESCRIPTION = open('README').read()

setup(
    name='prettyplotlib',
    version='0.1.7',
    author='Olga B. Botvinnik',
    author_email='olga.botvinnik@gmail.com',
    packages=find_packages(),
    license='MIT License',
    url='http://olgabot.github.io/prettyplotlib',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering'
    ],
    description='Painlessly create beautiful default `matplotlib` plots.',
    long_description=LONG_DESCRIPTION,
    install_requires=['matplotlib >= 1.2.1',
                      'brewer2mpl >= 1.3.1']
)
