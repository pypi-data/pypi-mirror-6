from setuptools import setup, find_packages
import sys
import os.path

sys.path.append(os.path.dirname(__file__))

from sbdk import VERSION


setup(
    name="sbgsdk",
    version=VERSION,
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['sbg = sbdk.main:main'],
    },
    install_requires=['nose==1.3.0', 'docker-py==0.3.0']
)