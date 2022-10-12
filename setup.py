# -*- coding: utf-8 -*-
"""Installer for the onlyoffice.plone package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.md').read(),
    open('AUTHORS.md').read(),
    open('CHANGELOG.md').read(),
])


setup(
    name='onlyoffice.plone',
    version='3.0.1',
    description="Plone ONLYOFFICE integration plugin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords='Python Plone',
    author='Ascensio System SIA',
    author_email='integration@onlyoffice.com',
    url='https://github.com/ONLYOFFICE/onlyoffice-plone',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/onlyoffice.plone',
        'Source': 'https://github.com/ONLYOFFICE/onlyoffice-plone',
        'Tracker': 'https://github.com/ONLYOFFICE/onlyoffice-plone/issues',
        # 'Documentation': 'https://onlyoffice.plone.readthedocs.io/en/latest/',
    },
    license='Apache-2.0 License',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['onlyoffice'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.4",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.restapi',
        'plone.app.dexterity',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = onlyoffice.plone.locales.update:update_locale
    """,
)
