import os
from setuptools import setup
import adipy

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='ADiPy',
    version=adipy.__version__,
    author='Abraham Lee',
    author_email='tisimst@gmail.com',
    description='Automatic Differentiation for Python',
    url='https://github.com/tisimst/adipy',
    license='BSD License',
    long_description=read('README.rst'),
    packages=['adipy', 'adipy.linalg'],
    install_requires=['numpy'],
    keywords=[
        'automatic differentiation',
        'algorithmic differentiation',
        'arbitrary order',
        'python',
        'linear algebra',
        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
        ]
    )
