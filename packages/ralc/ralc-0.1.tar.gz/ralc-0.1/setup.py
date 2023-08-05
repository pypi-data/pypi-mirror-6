import os
import re
import sys

from setuptools import setup


DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

README = open(rel('README.rst')).read()
INIT_PY = open(rel('ralc.py')).read()
VERSION = re.findall("__version__ = '([^']+)'", INIT_PY)[0]


setup(
    name='ralc',
    version=VERSION,
    description='Rate Calculator.',
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    url='https://github.com/playpauseandstop/ralc',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='',
    license='BSD License',
    entry_points={
        'console_scripts': ['ralc=ralc:main']
    },
    install_requires=list(filter(None, [
        'argparse==1.2.1' if sys.version_info[:2] < (2, 7) else None,
    ])),
    py_modules=[
        'ralc'
    ],
    test_suite='tests',
    tests_require=list(filter(None, [
        'unittest2==0.5.1' if sys.version_info[:2] < (2, 7) else None,
    ]))
)
