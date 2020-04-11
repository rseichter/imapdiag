"""
This file is part of "imapdiag".

Copyright © 2020 Ralph Seichter
"""
import setuptools

from imapdiag import DESCRIPTION
from imapdiag import PROGRAM
from imapdiag import __version__

with open('README.md', 'rt') as f:
    long_description = f.read()
setuptools.setup(
    name=PROGRAM,
    version=__version__,
    packages=['imapdiag'],
    entry_points={
        'console_scripts': ['imapdiag = imapdiag.__main__:main'],
    },
    url='https://github.com/rseichter/imapdiag',
    license='Proprietary',
    author='Ralph Seichter',
    author_email='ralph.seichter@horus-it.de',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='imap diagnostics',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    install_requires=['SQLAlchemy>=1.1'],
    python_requires='>=3.7',
)
