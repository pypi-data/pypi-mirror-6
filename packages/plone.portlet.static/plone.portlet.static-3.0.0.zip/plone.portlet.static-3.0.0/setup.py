import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.0.0'

long_description = (
    read('README.txt')
    + '\n' +
#    read('plone', 'portlet', 'static', 'README.txt')
#    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )


setup(name='plone.portlet.static',
      version=version,
      description="A simple static HTML portlet for Plone.",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='plone portlet static',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.portlet.static',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=["plone", 'plone.portlet'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
          'setuptools',
          "plone.portlets",
          "plone.app.portlets",
          "plone.app.textfield",
          "plone.i18n",
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'Zope2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
