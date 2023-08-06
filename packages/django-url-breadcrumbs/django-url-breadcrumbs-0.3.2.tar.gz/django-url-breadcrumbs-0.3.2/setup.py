import codecs
import re
from os import path
from setuptools import setup, Command


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return open(file_path).read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py', '--ds=urlbreadcrumbs.tests.settings'])
        raise SystemExit(errno)

setup(
    name='django-url-breadcrumbs',
    version=find_version('urlbreadcrumbs', '__init__.py'),
    description='a generic app to provide a simple breadcrumbs functionality in django projects',
    long_description=read('README.rst'),
    author='Slawek Ehlert',
    author_email='slafs@op.pl',
    license='BSD',
    url='https://bitbucket.org/slafs/django-url-breadcrumbs/',
    packages=[
        'urlbreadcrumbs',
        'urlbreadcrumbs.tests',
    ],
    cmdclass = {'test': PyTest},
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Utilities',
    ],
)
