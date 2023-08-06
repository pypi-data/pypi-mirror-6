
# isbntools - tools for extracting, cleaning and transforming ISBNs
# Copyright (C) 2014  Alexandre Lima Conde

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from distutils.core import setup
from isbntools import __version__

setup(
    name='isbntools',
    version=__version__,
    author='Alexandre Conde',
    author_email='alexandreconde@hotmail.com',
    url='https://github.com/xlcnd/isbntools',
    download_url='https://github.com/xlcnd/isbntools/archive/master.zip',
    packages=['isbntools', 'isbntools/dev', 'isbntools/data'],
    scripts=['bin/isbn_validate', 'bin/to_isbn10', 'bin/to_isbn13',
             'bin/isbn_mask', 'bin/isbn_info', 'bin/isbn_meta',
             'bin/isbntools', 'bin/isbn_stdin_validate',
             'bin/isbn_from_words', 'bin/isbn_editions',
             ],
    license='LGPL v3',
    description='Extract, clean, transform, hyphenate and metadata for ISBNs (International Standard Book Number).',
    long_description=open('README.rst').read(),
    keywords='ISBN, validate, transform, hyphenate, metadata',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Text Processing :: General',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
