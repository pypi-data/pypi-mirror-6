from distutils.core import setup, Extension
setup(
    name='tr1regex',
    version='0.1a',
    ext_modules=[Extension('tr1regex', ['tr1regex.cpp'])],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Bart Jellema',
    author_email='bart@zeromail.com',
    url='http://pypi.python.org/pypi/tr1regex/',
    description='Very basic interface to the default C++ tr1 regex standard library.'
)