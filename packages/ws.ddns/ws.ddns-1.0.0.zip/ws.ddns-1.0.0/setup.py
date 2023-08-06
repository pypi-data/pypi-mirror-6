"""Update DNS settings using the Schlundtech XML-Gateway.
"""
from setuptools import setup, find_packages
import glob
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='ws.ddns',
    version='1.0.0',

    install_requires=[
        'flask',
        'gocept.logging',
        'lxml',
        'requests',
        'setuptools',
    ],

    entry_points={
        'console_scripts': [
            'schlund-ddns = ws.ddns.update:main',
            'schlund-ddns-cgi = ws.ddns.web:main',
        ],
    },

    author='Wolfgang Schnerring <wosc@wosc.de>',
    author_email='wosc@wosc.de',
    license='ZPL 2.1',
    url='https://bitbucket.org/wosc/schlund-ddns/',

    description=__doc__.strip(),
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
        'README.txt',
        'CHANGES.txt',
    )),

    namespace_packages=['ws'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob(project_path('*.txt')))],
    zip_safe=False,
)
