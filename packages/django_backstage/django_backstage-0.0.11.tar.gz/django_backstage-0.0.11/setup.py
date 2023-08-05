from setuptools import setup, find_packages

setup(
    name='django_backstage',
    version='0.0.11',
    description='Django project and site deployment using uWSGI, nginx, etc.',
    author='MiddleFork',
    author_email='walker@mfgis.com',
    packages=find_packages(),
    install_requires=[
        "setuptools_git >= 0.3",
    ],
)
