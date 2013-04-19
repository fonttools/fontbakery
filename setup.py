# coding: utf-8

from setuptools import setup

setup(
    name="Font Bakery",
    version='0.1',
    url='https://github.com/xen/bakery',
    description='',
    author='Mikhail Kashkin',
    author_email='mkashkin@gmail.com',
    packages=["bakery"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Babel',
        'Flask-Mail',
        'Flask-OAuth',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
