from distutils.core import setup

__version__ = '0.0.3'

setup(
    name = 'espressocup',
    py_modules = ['espressocup'],
    version = __version__,
    description = 'A gevent-intended very very basic flask-like WSGI server',
    long_description=open('README.rst','r').read(),
    author = 'Daniel Fairhead',
    author_email = 'danthedeckie@gmail.com',
    url = 'https://bitbucket.org/dfairhead/espressocup',
    download_url = 'https://bitbucket.org/dfairhead/espressocup/get/' + __version__ + '.zip',
    keywords = ['WSGI'],
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Programming Language :: Python :: 2.7',
                  ],
    )
