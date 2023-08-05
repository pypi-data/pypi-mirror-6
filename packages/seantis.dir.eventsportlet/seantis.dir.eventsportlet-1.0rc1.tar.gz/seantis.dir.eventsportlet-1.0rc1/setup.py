from setuptools import setup, find_packages
import os

name = 'seantis.dir.eventsportlet'
description = (
    "Portlet for displaying events."
)
version = '1.0rc1'

def get_long_description():
    readme = open('README.rst').read()
    history = open(os.path.join('docs', 'HISTORY.rst')).read()
    contributors = open(os.path.join('docs', 'CONTRIBUTORS.rst')).read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, contributors, history))

tests_require = [
    'collective.betterbrowser>=0.4',
    'collective.testcaselayer',
    'plone.app.testing',
    'mock'
]

setup(name=name, version=version, description=description,
      long_description=get_long_description(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Seantis GmbH',
      author_email='info@seantis.ch',
      url='https://github.com/seantis/seantis.dir.eventsportlet',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['seantis', 'seantis.dir'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone>=4.3',
      ],
      extras_require=dict(
          tests=tests_require
      ),
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
