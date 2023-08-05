# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-stdimage',
    version='0.3.0',
    description='Django Standarized Image Field',
    author='codingjoe',
    url='https://github.com/codingjoe/django-stdimage',
    author_email='info@johanneshoppe.com',
    license='License :: OSI Approved :: MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    packages=['stdimage'],
    include_package_data=True,
    requires=['django (>=1.2.7)', ],
)
