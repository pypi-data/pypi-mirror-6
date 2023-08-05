import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from setuptools import setup
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    has_setuptools = False

if sys.version_info >= (3, ):
    if not has_setuptools:
        raise Exception('Python3 support in PyTransmit requires distribute.')

setup(
    name='PyTransmit',
    version='0.1',
    url='http://pytransmit.readthedocs.org/en/latest/',
    license='BSD',
    author='Ajay Kumar N',
    author_email='contact@pypix.com',
    download_url= "https: //github.com/ajkumar25/PyTransmit/tarball/0.1",
    description='A flexible FTPClient library for python web development.',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'pytransmit',
         ],
)
