from setuptools import setup, find_packages

setup(
    name='plicata',
    version='0.0.124',
    description='Django Application for Book Publishers',
    author='MiddleFork',
    url='http://plicata.com',
    author_email='walker@mfgis.com',
    packages=find_packages(),
    install_requires=[
        "setuptools_git >= 0.3",
        "django == 1.5.5",
        "mezzanine == 1.4.16",
    ],
)
