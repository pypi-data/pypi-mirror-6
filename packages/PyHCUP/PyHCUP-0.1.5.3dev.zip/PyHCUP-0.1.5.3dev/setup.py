from distutils.core import setup

setup(
    name='PyHCUP',
    version='0.1.5.3dev',
    description='Python tools working with data from the Healthcare Cost and Utilization Program (http://hcup-us.ahrq.gov).',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    keywords='HCUP SAS healthcare analysis pandas',
    author='Terry James Biel',
    author_email='terry.biel@gmail.com',
    packages=['pyhcup'],
    license='MIT',
    provides=['pyhcup'],
    requires=['pandas (>=0.11.0)'],
    package_data={'pyhcup': ['data/loadfiles/*/*.*']},
)