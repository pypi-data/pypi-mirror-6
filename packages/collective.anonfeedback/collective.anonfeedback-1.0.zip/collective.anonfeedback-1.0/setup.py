from setuptools import setup, find_packages
import os

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read().strip()

long_description = (
    read('README.txt')
    + '\n\n' +
    read('docs', 'CONTRIBUTORS.txt')
    + '\n\n' +
    read('docs', 'CHANGES.txt')
    + '\n\n')

setup(name='collective.anonfeedback',
      version=version,
      description="An anonymous feedback form",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        ],
      keywords='plone',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/collective/collective.anonfeedback',
      license='MIT',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFCore',
      ],
      extras_require = {
          'test': [
              'plone.app.testing',
#              'zope.globalrequest',
          ]
      },      
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
