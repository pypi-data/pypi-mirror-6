"""setup/install script for truncate"""


from distutils.core import setup

from truncate import __version__, __author__, __license__


setup(
    name='truncate',
    version=__version__,
    py_modules=['__init__'],
    author=__author__,
    author_email='www.kelvinwong.ca',
    url='https://github.com/un33k/python-slugify',
    description='Intelligently truncate a given string',
    long_description='',
    download_url='',
    keywords='',
    license=__license__,
    install_requires=[''],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ]
)
