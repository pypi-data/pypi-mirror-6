from distutils.core import setup, Extension



setup(
    name='boost_regex',
    version='0.1f',
    ext_modules=[
        Extension('boost_regex',
                  ['boost_regex.cpp'],
                  include_dirs=['/usr/include', '\\usr\\include', 'C:\\local\\boost_1_55_0'],
                  library_dirs=['C:\\local\\boost_1_55_0\\lib64-msvc-9.0', '\\usr\\lib']
        )
    ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Bart Jellema',
    author_email='bart@zeromail.com',
    url='http://pypi.python.org/pypi/boost_regex/',
    description='Very basic interface to the boost regex library.'
)