# -*- coding: utf-8 -*-
"""Setup for pspolicy.homes4.base package."""

from setuptools import setup, find_packages

version = '0.3'

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


install_requires = [
    'setuptools',
    'Products.Carousel',
    'Products.Doormat',
    'Products.PloneFormGen',
    'Products.RedirectionTool',
    'collective.carousel',
    'collective.contentleadimage',
    'collective.cover',
    'collective.googleanalytics',
    'collective.quickupload',
    'plone.app.caching',
    'plone.app.theming',
    'plone.mls.listing',
    'sc.social.like',
    'theming.toolkit.core',
    'theming.toolkit.viewlets',
    'theming.toolkit.views',
    'z3c.unconfigure',
]


setup(
    name='pspolicy.homes4.base',
    version=version,
    description="Plone Policy Add-On for the Homes4 sites.",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Framework :: Zope2",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone policy',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/pspolicy.homes4.base',
    license='gpl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['pspolicy', 'pspolicy.homes4'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """
)
