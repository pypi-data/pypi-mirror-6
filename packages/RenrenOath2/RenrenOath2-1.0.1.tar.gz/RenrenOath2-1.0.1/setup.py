from distutils.core import setup
import sys

import renren

kw = dict(
    name = 'RenrenOath2',
    version = renren.__version__,
    description = 'Renren OAuth 2 API Python SDK',
    long_description = open('README', 'r').read(),
    author = 'Tianchi Liu',
    author_email = 'liutianchi@yahoo.com',
    url = 'https://github.com/icltc/renren_api_oauth2',
    download_url = 'https://github.com/icltc/renren_api_oauth2',
    py_modules = ['renren'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])

setup(**kw)
