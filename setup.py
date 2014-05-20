import codecs
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


# long description
with codecs.open('README.md', encoding='utf-8') as f:
    long_description = f.read()


# test command http://lnkfy.com/wnQ
class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='django-actionviews',
    version='0.2.0',
    description='Alternative Class Based Views for Django',
    long_description=long_description,
    url='https://github.com/lig/django-actionviews',
    author='Serge Matveenko',
    author_email='s@matveenko.ru',
    license='Apache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Framework :: Django',
    ],
    keywords='django generic views',
    packages=['actionviews'],
    install_requires=['django'],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)
