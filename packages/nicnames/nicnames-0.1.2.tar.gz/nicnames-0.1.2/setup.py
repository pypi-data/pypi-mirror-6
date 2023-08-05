from setuptools import setup, find_packages
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

setup(
    name="nicnames",
    version='0.1.2',
    description='A collection of functions for performing whois and DNS queries.',
    long_description=open(os.path.join(__location__, 'README.rst')).read(),
    author='Stephan Solomonidis',
    author_email='stephan@stephan.io',
    url='https://github.com/stephan765/nicnames',
    download_url='https://pypi.python.org/pypi/nicnames',
    license='BSD (3-Clause) License',
    packages=find_packages(exclude=('tests',)),
    install_requires=[
        'bleach'
    ],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
        ]
    )
