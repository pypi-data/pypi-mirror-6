from setuptools import setup, find_packages
import os

version = '0.1.0'

tests_require = ['plone.app.testing']

setup(name='collective.typecriterion',
      version=version,
      description="A new, more flexible, content type criterion for Plone collections",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        ],
      keywords='plone criterion collection type',
      author='keul',
      author_email='luca@keul.it',
      url='https://github.com/keul/collective.typecriterion',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.collection',
          'plone.app.querystring>=1.2.0',
          'plone.app.registry',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
