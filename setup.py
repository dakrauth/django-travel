import os
import sys
import runpy
from setuptools import setup, find_packages


VERSION = runpy.run_path('src/travel/__init__.py')['get_version']()

setup(
    name='django-travel',
    version=VERSION,
    url='https://github.com/dakrauth/travel',
    description='A travelogue and bucket list app for Django',
    author='David A Krauth',
    author_email='dakrauth@gmail.com',
    platforms=['any'],
    license='MIT License',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[
        'choice-enum>=1.0.0',
        'Django>=2.2.8,<3.1',
        'django-bootstrap3>=12.0.0',
        'python-dateutil>=2.8.1',
        'pytz>=2019.3',
        'djangorestframework>=3.10.3',
    ],
    extras_require={
        'test': ['pytest-django', 'pytest', 'pytest-cov'],
        'dev': ['ipdb', 'django-extensions'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 2.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
        'Topic :: Education',
    ]
)
