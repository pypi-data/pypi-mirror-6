# encoding: utf-8
from setuptools import setup, find_packages

import simpy.io


setup(
    name='simpy.io',
    version=simpy.io.__version__,
    author='Ontje Lünsdorf',
    author_email='the_com at gmx.de',
    description='Asynchronous networking based on SimPy.',
    long_description=open('README.rst', 'rb').read().decode('utf-8'),
    url='https://bitbucket.org/simpy/simpy.io',
    license='MIT License',
    install_requires=[
        'SimPy>=3',
    ],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Networking',
    ],
)
