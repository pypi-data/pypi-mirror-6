from setuptools import setup, find_packages
from fcc import api

setup(name='fcc',
    version=api.__version__,
    description='Python interface for Federal Communication Commission web API',
    author='Michael Selik',
    author_email='mike@selik.org',
    url='http://github.com/selik/fcc-api/',
    py_modules=['fcc'],
    license="MIT",
    long_description=open('README.md').read(),
    packages=find_packages(),
    platforms=["any"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=['requests>=1.0'],
)