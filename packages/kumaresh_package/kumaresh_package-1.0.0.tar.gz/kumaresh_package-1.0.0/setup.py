from distribute_setup import use_setuptools
use_setuptools()
from setuptools.command.install import install
from setuptools import setup, find_packages

x =  find_packages()

with open("README") as f:
    long_desc = f.read()
    ind = long_desc.find("\n")
    long_desc = long_desc[ind + 1:]

setup(
        name="kumaresh_package",
        packages=find_packages(),
        version="1.0.0",
        install_requires=["numpy>=1.6.1", "scipy>=0.10.1", "pymatgen>=2.8.8", "custodian>=0.5.1"],
        author="Kumaresh Visakan Murugan",
        author_email="",
        maintainer="",
        license="MIT",
        description="Kumaresh project",
        long_description=long_desc,
        keywords=["kumaresh"],
        classifiers=[
            "Programming Language :: Python :: 2.7",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Scientific/Engineering :: Chemistry",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ],
)
