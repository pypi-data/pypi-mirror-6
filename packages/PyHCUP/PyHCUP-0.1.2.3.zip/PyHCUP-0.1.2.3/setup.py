from distutils.core import setup

setup(
    name='PyHCUP',
    version='0.1.2.3',
    packages=['pyhcup'],
    license='',
    long_description=open('README.txt').read(),
    provides=['pyhcup'],
    requires=['pandas (>=0.11.0)'],
)