#!python
from setuptools import setup, find_packages

setup(name='z3c.formwidget.query',
      version='0.10',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "A source query widget for z3c.form.",
      long_description=(
          open('README.txt').read()
          + '\n\n' +
          open('CHANGES.txt').read()
          ),
      license = "ZPL 2.1",
      keywords = "zope zope3 z3c.form",
      url='http://pypi.python.org/pypi/z3c.formwidget.query',
      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c', 'z3c.formwidget'],
      extras_require = dict(test=['zope.testing',
                                  'z3c.form [test]'
                                  ]),
      install_requires = ['setuptools',
                          'z3c.form >= 2.6.0',
                          'zope.interface',
                          'zope.schema',
                          'zope.component',
                          'zope.i18nmessageid',
                          ],
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Framework :: Zope3',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     ],
      )
