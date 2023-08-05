from distutils.core import setup

setup(
    name='PyHCUP',
    version='0.1.2dev',
    packages=['pyhcup'],
    license='',
    long_description=open('README.txt').read(),
    provides=['pyhcup'],
    install_requires=['pandas(>=0.11.0)','pyodbc(>=3.0.6)'],
)