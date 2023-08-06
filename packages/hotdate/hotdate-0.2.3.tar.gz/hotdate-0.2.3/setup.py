from distutils.core import setup
import hotdate

setup(
    name='hotdate',
    version=hotdate.__version__,
    author='Samuel "mansam" Lucidi',
    author_email="mansam@csh.rit.edu",
    packages=['hotdate'],
    url='http://pypi.python.org/pypi/when/',
    license='LICENSE',
    description='Intuitive date formatting.',
    long_description=open('README.md').read()
)
