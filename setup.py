import os
import sys
import runpy
from setuptools import setup, find_packages


VERSION = runpy.run_path("src/travel/__init__.py")["get_version"]()

setup(
    name="django-travel",
    version=VERSION,
    url="https://github.com/dakrauth/travel",
    description="A travelogue and bucket list app for Django",
    author="David A Krauth",
    author_email="dakrauth@gmail.com",
    platforms=["any"],
    license="MIT License",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.10",
    zip_safe=False,
    install_requires=[
        "Django>=4.2,<5.2",
        "django-bootstrap5",
        "python-dateutil",
        "djangorestframework",
        "django-vanilla-views",
    ],
    extras_require={
        "test": ["pytest-django", "pytest", "pytest-cov"],
        "dev": ["ipdb", "django-extensions"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Education",
    ],
)
