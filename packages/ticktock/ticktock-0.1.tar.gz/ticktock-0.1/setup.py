from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ticktock',
    version='0.1',
    author='Thomas Roten',
    author_email='thomas@roten.us',
    url='https://github.com/tsroten/ticktock',
    description="adds least-recently-used cache management and automatic data "
                "timeout to Python's Shelf class.",
    long_description=long_description,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Filesystems',
        'Topic :: Database :: Front-Ends',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ],
    keywords=['shelf', 'dictionary-like', 'dict-like', 'cache', 'lru',
              'least-recently-used', 'timeout', 'persistent'],
    py_modules=['ticktock'],
    test_suite='test',
)
