import codecs

from setuptools import setup


with codecs.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-actionviews',
    version='0.1dev1',
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
    install_requires=[
        'django',
    ],
)
