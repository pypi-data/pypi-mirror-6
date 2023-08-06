from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = read('README.md')

setup(
    name='underpy',
    version='0.1.1',
    url='https://github.com/ramonski/underpy',
    license='MIT',
    author='Ramon Bartl',
    author_email='ramon.bartl@googlemail.com',
    tests_require=['nose'],
    description='Functional helpers for Python',
    long_description=long_description,
    platforms='any',
    test_suite='nose.collector',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    setup_requires=['nose>=1.0'],
    extras_require={
      'testing': ['nose'],
    }
)
