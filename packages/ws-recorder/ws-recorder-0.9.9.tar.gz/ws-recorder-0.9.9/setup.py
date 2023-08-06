import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ws-recorder',
    version='0.9.9',
    packages=['wsrecorder'],
    include_package_data=True,
    license='LGPL',
    description='Tool to record Web Service calls and to serve them afterwards',
    long_description=README,
    url='https://bitbucket.org/kkujawinski/ws-recorder',
    author='Kamil Kujawinski',
    author_email='kamil@kujawinski.net',
    install_requires=[
        'lxml',
        'lxml-xpath2-functions',
    ],
    tests_require=[
        'unittest2',
    ],
    test_suite="tests",
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Testing',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
