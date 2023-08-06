
from distutils.core import setup
import setuptools

setup(
    name = 'abris',
    packages = setuptools.find_packages(),
    version = '0.1.4',
    description = 'Small data preprocessing engine built on top of sklearn for easy prototyping.',
    author = 'Gerard Madorell',
    author_email = 'gmadorell@gmail.com',
    url = 'https://github.com/Skabed/abris',
    download_url = 'https://github.com/Skabed/abris/tarball/0.1.3',
    keywords = ['preprocessing', 'data'],
    classifiers = [],
)