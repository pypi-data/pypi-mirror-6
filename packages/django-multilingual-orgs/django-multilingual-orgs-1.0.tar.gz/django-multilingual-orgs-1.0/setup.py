import os
from setuptools import setup, find_packages
import multilingual_orgs as app


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

dependency_links = [
    # needs this dev version for django 1.6 fixes
    'https://github.com/KristianOellegaard/django-hvad/tarball/0e2101f15404eaf9611cd6cf843bfc424117b227',  # NOQA
]


setup(
    name="django-multilingual-orgs",
    version=app.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, cms, plugin, organizations, profile, localization',
    author='Daniel Kaufhold',
    author_email='daniel.kaufhold@bitmazk.com',
    url="https://github.com/bitmazk/django-multilingual-orgs",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django',
        'South',
        'django-libs',
        'django-filer',
        'Pillow',
        'django-people',
        'django-localized-names'
    ],
    dependency_links=dependency_links,
    tests_require=[
        'fabric',
        'factory_boy',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
        'flake8',
        'ipdb',
    ],
    test_suite='multilingual_orgs.tests.runtests.runtests',
)
