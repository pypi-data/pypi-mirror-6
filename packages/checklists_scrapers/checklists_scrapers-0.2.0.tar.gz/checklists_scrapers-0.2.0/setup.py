import os

from setuptools import setup, find_packages


version = __import__('checklists_scrapers').get_version()


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


setup(
    name='checklists_scrapers',
    version=version,
    description='Web scrapers for downloading checklists of birds from online'
                'databases such as eBird.',
    long_description=read("README.rst"),
    author='Stuart MacKay',
    author_email='smackay@flagstonesoftware.com',
    url='http://pypi.python.org/pypi/checklists_scrapers/',
    license='GPL',
    packages=find_packages(),
    keywords='eBird worldbirds web scraper birds checklists',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP",
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose==1.3.0',
    ],
    install_requires=[
        'scrapy == 0.16.4',
        'unidecode',
    ],
)
