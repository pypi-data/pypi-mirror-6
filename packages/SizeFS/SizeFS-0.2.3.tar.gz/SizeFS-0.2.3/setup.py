__author__ = 'mm'
from distutils.core import setup
from distutils.extension import Extension

setup(
    name='SizeFS',
    version='0.2.3',
    author='Mark McArdle',
    author_email='mark.mcardle@sohonet.com',
    packages=['sizefs', 'tests'],
    scripts=[],
    url='http://pypi.python.org/pypi/SizeFS/',
    download_url='https://github.com/sohonetlabs/sizefs',
    license='LICENSE.txt',
    ext_modules=[
        Extension("sizefs.contents", ["sizefs/contents.pyx"]),
        Extension("sizefs.contents", ["sizefs/contents.c"])
    ],
    description='SizeFS is a mock filesystem for creating files of particular '
                'sizes with specified contents.',
    long_description=open('README.txt').read(),
    keywords=['testing', 'files', 'size'],
    install_requires=[
        "fusepy>=2.0.2",
        "Cython>=0.19.1",
        "docopt==0.6.1"
        ],
)
