# -*- coding: utf-8 -*-

__author__ = 'Jayme Tosi Neto'

from setuptools import setup, find_packages

setup(name = "pycicu",
    version = "0.1.5.6",
    description = u"PyClean Image Crop Uploader (pycicu) provides AJAX file upload and image CROP functionalities" 
                  u"using Pyramid. It uses Modal from twitter-bootstrap. This is a fork of clean-image-crop-uploader.",
    long_description=open('README.rst').read(),
    author = "kalkehcoisa",
    author_email = "kalkehcoisa@gmail.com",
    url = "",
    keywords='web pylons pyramid upload image crop',
    packages = find_packages(),
    include_package_data=True,
    install_requires = [
        'Pillow>=1.5',
        'deform>=2.0a2',
        'colander>=1.0b1',
        'pyramid_chameleon>=0.1',
        'SQLAlchemy>=0.8.3',
        ],
    classifiers = [
        #https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    entry_points="""\
    [paste.app_factory]
    main = pycicu:main
    [console_scripts]
    initialize_pycicu_db = pycicu.scripts.initializedb:main""",
    zip_safe = False,
)
