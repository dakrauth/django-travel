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
        'Django>=2.2.24,<4.1',
        'django-bootstrap-v5>=1.0.8',
        'python-dateutil>=2.8.2',
        'pytz>=2021.3',
        'djangorestframework>=3.12.4',
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
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'Topic :: Education',
    ]
)
