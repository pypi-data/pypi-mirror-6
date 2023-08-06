import os
from setuptools import setup, find_packages

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

version = '1.2'

setup(
    name='collective.portletmetadata',
    version=version,
    description="Adds metadata functionality to portlets",
    long_description='\n'.join([
        read('README.rst'),
        read('CHANGES.rst'),
    ]),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Bo Simonsen',
    author_email='bo@headnet.dk',
    url='http://github.com/collective/collective.portletmetadata',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.monkeypatcher',
        'plone.portlets',
        'plone.app.portlets',
        'setuptools',
        'z3c.jbot',
        'z3c.unconfigure==1.0.1',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
        # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
    """,
)
