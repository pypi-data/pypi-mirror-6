from setuptools import setup, find_packages
import os

version = '2.0.0b2'

tests_require = ['plone.app.testing', 'pyquery', 'collective.recaptcha', ]

setup(name='redturtle.sendto_extension',
      version=version,
      description='An extension for the "Send this" Plone document action',
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone plonegov sendto mail users groups',
      author='Redturtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/redturtle.sendto_extension',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'collective.js.jqueryui',
          'rt.zptformfield',
          'collective.autopermission',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
