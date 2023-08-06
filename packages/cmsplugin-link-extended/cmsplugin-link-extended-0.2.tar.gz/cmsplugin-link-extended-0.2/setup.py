import os
from setuptools import setup, find_packages
import cmsplugin_link_extended


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name="cmsplugin-link-extended",
    version=cmsplugin_link_extended.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, django-cms, plugin, link, extension',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    url="https://github.com/bitmazk/cmsplugin-link-extended",
    packages=find_packages(),
    install_requires=[
        'django',
        'django-cms',
    ],
    include_package_data=True,
)
