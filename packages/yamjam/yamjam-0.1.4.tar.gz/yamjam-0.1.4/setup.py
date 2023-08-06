'''setup for yamjam to build an sdist'''
from setuptools import setup

with open('README.rst') as h_readme:
    LONG_DESCRIPTION = h_readme.read()

setup(
    name="yamjam",
    version="0.1.4",
    description="A multi-project, shared, yaml based configuration system",
    long_description=LONG_DESCRIPTION,
    author="Jeff Hinrichs",
    author_email="jeffh@dundeemt.com",
    url="https://bitbucket.org/dundeemt/yamjam",   # project home page, if any
    py_modules=['YamJam'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['README.rst', 'LICENSE.txt', '*.rst'],
    },
    install_requires=['pyyaml'],
    # metadata for upload to PyPI
    license="BSD - LICENSE.txt",
    keywords="config yaml django settings",
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
