from setuptools import setup, find_packages

version = '1.0rc2'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.local.workspace',
      version=version,
      description="A dexterity container that provides all collective.local features",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Thomas Desvenain',
      author_email='thomas.desvenain@gmail.com',
      url='https://github.com/tdesvenain/collective.local.workspace',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective', 'collective.local'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.local.adduser',
          'collective.local.addgroup',
          'collective.local.sendto',
          'collective.local.userlisting',
          'collective.local.contentrules',
          'plone.app.dexterity',
      ],
      extras_require={
          'test': ['plone.app.testing',
                   'plone.app.robotframework',
                   'robotframework-selenium2screenshots',
                   'ecreall.helpers.testing',
                   ],
          },

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
