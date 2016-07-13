import py4syn
import versioneer
from setuptools import setup, find_packages

readme = open('README.rst').read()

setup(
    name='Py4Syn',
    author='LNLS',
    author_email='sol@lnls.br',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    scripts=[],
    url='',
    license='LICENSE',
    description='Python Tools for Synchrotron Laboratories',
    long_description=readme,
    install_requires=[
        "versioneer>=0.16",
        "numpy>=1.8.1",
        "matplotlib>=1.3.0",
        "pyepics>=3.2.0",
        "h5py>=2.3",
        "lmfit>=0.8.3"
    ]
)
