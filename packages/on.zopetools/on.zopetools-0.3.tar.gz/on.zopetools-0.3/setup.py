from setuptools import setup, find_packages
import os

version_file = os.path.join('on', 'zopetools', 'version.txt')
version = open(version_file).read().strip()

setup(name='on.zopetools',
      version=version,
      description="dynamic display of zopetools files",
      long_description=open("README.rst").read() + \
                       open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Environment :: Console",
        "Programming Language :: Zope",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Zope",
        "Topic :: Utilities",
        ],
      keywords='plone zopetools',
      author='Toni Mueller',
      author_email='support@oeko.net',
      url='http://www.oeko.net/',
      license='AGPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['on'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          #'Pillow', # side effect of the Plone requirements
          'plone.app.dexterity [grok]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'collective.autopermission',
          'plone.app.registry',
          'transaction',
          'Zope2',
          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      createmountpoints = on.zopetools.zodbmountpoints:main

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=['setuptools-git'],
      )
