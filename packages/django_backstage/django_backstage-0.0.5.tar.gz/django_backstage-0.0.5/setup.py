from setuptools import setup, find_packages

setup(
    name='django_backstage',
    version='0.0.5',
    description='Django project and site deployment using uWSGI, nginx, etc.',
    author='MiddleFork',
    author_email='walker@mfgis.com',
    packages=find_packages(),
    install_requires=['django==5.5', ],
    classifiers=[
            "Development Status :: 2 Pre-Alpha", ],
)
