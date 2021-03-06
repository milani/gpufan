from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gpufan',
    version='0.1.0a1',
    url='https://github.com/milani/gpufan',
    description='Control Nvidia GPU fan in your python script.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Morteza Milani',
    author_email='mrtz.milani@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3',
    keywords='machinelearning ai pytorch tensorflow torch nvidia gpu fan',
    packages=find_packages(exclude=['docs', 'tests']),
    setup_require=['pytest-runner'],
    tests_require=['pytest', 'sure'],
    scripts=['bin/gpufan'],
    project_urls={
        'Bug Reports': 'https://github.com/milani/gpufan/issues',
        'Home Page': 'https://github.com/milani/gpufan'
    }
)
