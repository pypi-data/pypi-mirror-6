import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='thermocouples_reference',
    version='0.16',
    description='Thermocouple emf reference functions for types B,C,D,E,G,J,K,N,R,S,T',
    long_description=read('README.rst'),
    author='User:Nanite @ wikipedia',
    license='public domain',
    url='https://pypi.python.org/pypi/thermocouples_reference',
    packages=['thermocouples_reference'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Manufacturing',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords=[
        'thermocouple',
        'thermometer',
        'temperature',
        'emf',
        'lookup',
        'NIST',
    ],
    install_requires=[
        'numpy',
    ],
    extras_require = {
        'inverse_lookup':  ['scipy'],
    },
    zip_safe=True)

