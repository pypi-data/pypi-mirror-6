# coding: utf-8

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


base_path = os.path.dirname(os.path.abspath(__file__))
long_description = open(os.path.join(base_path, 'README.rst')).read()

setup(
    name="featureforge",
    version="0.1.2",
    description="A library to build and test machine learning features",
    long_description=long_description,
    author="Rafael Carrascosa, Daniel Moisset, Javier Mansilla",
    author_email="rcarrascosa@machinalis.com",
    url="https://github.com/machinalis/featureforge",
    packages=[
        "featureforge",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
    ],
    keywords=[
        "machine learning", "scikit", "scikit-learn", "sklearn",
        "features", "testing", "vectorization", "preprocessing"
    ],
    install_requires=[
        "mock",
        "future",
        "schema==0.2.1",
        "numpy",
        "scipy"
    ],
    dependency_links=[
        "https://github.com/jmansilla/schema/tarball/master#egg=schema-0.2.1"
    ],
    include_package_data=False,
)
