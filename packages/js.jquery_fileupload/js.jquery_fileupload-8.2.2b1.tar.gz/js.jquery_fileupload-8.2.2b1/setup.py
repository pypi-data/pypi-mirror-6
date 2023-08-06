from setuptools import setup, find_packages
import os

version = '8.2.2b1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'jquery_fileupload', 'test_jquery_fileupload.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.jquery_fileupload',
    version=version,
    description="Fanstatic packaging of jquery.fileupload.js.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://github.com/tmassman/js.jquery_fileupload',
    download_url='http://pypi.python.org/pypi/js.jquery_fileupload',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.bootstrap',
        'js.jquery',
        'js.jqueryui',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'jquery_fileupload = js.jquery_fileupload:library',
        ],
    },
)
