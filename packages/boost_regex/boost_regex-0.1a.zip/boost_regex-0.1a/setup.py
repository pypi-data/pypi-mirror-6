from distutils.core import setup, Extension
setup(
    name='boost_regex',
    version='0.1a',
    ext_modules=[Extension('boost_regex', ['boost_regex.cpp'], include_dirs=['.'])],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Bart Jellema',
    author_email='bart@zeromail.com',
    url='http://pypi.python.org/pypi/boost_regex/',
    description='Very basic interface to the boost regex library.'
)