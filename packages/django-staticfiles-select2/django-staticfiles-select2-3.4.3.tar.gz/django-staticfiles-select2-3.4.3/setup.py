from setuptools import setup
import os
import re


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return open(file_path).read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-staticfiles-select2',
    version=find_version('staticfiles_select2', '__init__.py'),
    description='select2 meets Django staticfiles',
    author='Slawek Ehlert',
    author_email='slafs@op.pl',
    url='http://bitbucket.org/slafs/django-staticfiles-select2/',
    packages=['staticfiles_select2'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
