from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='vbeo.seantis.dir.events',
      version=version,
      description=(
          "Integration of seantis.dir.events "
          "for Volkswirtschaft Berner Oberland"
      ),
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Seantis GmbH',
      author_email='info@seantis.ch',
      url='https://github.com/seantis/vbeo.seantis.dir.events',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vbeo', 'vbeo.seantis', 'vbeo.seantis.dir'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'seantis.dir.events',
          'izug.basetheme',
          'plone.app.theming'
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
