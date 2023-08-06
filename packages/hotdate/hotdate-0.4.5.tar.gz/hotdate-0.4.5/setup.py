from setuptools import setup

setup(
    name='hotdate',
    version='0.4.5',
    author='Samuel "mansam" Lucidi',
    author_email="mansam@csh.rit.edu",
    packages=['hotdate'],
    url='http://pypi.python.org/pypi/hotdate/',
    license='LICENSE',
    install_requires=[
    	'six',
    	'python-dateutil',
    	'freezegun'

    ],
    description='Intuitive date formatting.',
    long_description=open('README.rst').read()
)
