from setuptools import setup

setup(
    name='orakelsuperscript',  # This is the name of your PyPI-package.
    version='0.2',  # Update the version number for new releases
    entry_points={
        'console_scripts': ['orakelsuperscript=orakelsuperscript:main'],
    }
)